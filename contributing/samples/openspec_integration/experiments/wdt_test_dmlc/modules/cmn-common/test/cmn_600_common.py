# INTEL CONFIDENTIAL

# © 2019 Intel Corporation
#
# This software and the related documents are Intel copyrighted materials, and
# your use of them is governed by the express license under which they were
# provided to you ("License"). Unless the License provides otherwise, you may
# not use, modify, copy, publish, distribute, disclose or transmit this software
# or the related documents without Intel's prior written permission.
#
# This software and the related documents are provided as is, with no express or
# implied warranties, other than those that are expressly stated in the License.


import importlib
from dev_util import Bitfield_LE, bank_regs
from types import SimpleNamespace
import conf
import simics
import table

import os
import random
random.seed(94210987)

NS = 1 << 63

simmod = "simmod.%s" % os.environ['CMN_MODULE']
cmn_commands = importlib.import_module("%s.cmn_commands" % simmod)
find_nodes = cmn_commands.find_nodes
node_types = cmn_commands.node_types
cmn_regs = importlib.import_module("%s.regs" % simmod).regs
simics.SIM_run_command('output-radix base=16')

region_bf = Bitfield_LE({
    "base":         (30, 9),
    "sz":           (8, 4),
    "target_type":  (3, 2),
    "valid":        (0, 0)})

tgt_bf = Bitfield_LE({
    "nid3": (46, 36),
    "nid2": (34, 24),
    "nid1": (22, 12),
    "nid0": (10, 0)})

gic_bf = Bitfield_LE({
    "nid":          (62, 52),
    "base":         (47, 16),
    "sz":           (6, 4),
    "target_type":  (3, 2),
    "valid":        (0, 0)})

hnf_cfg_bf = Bitfield_LE({"hnf_ocm_allways_en": 10, "hnf_ocm_en": 9})

lock_base_bf = Bitfield_LE({"valid": 63, "base_addr": (47, 0)})

hnf_region_bf = Bitfield_LE({
    "valid":      63,
    "base_addr":  (47, 26),
    "sz":         (16, 12),
    "nodeid":     (10, 0)})

hnf_sam_control_bf = Bitfield_LE({
    "hn_cfg_sam_inv_top_address_bit":  63,
    "hn_cfg_sam_top_address_bit2":     (61, 56),
    "hn_cfg_sam_top_address_bit1":     (53, 48),
    "hn_cfg_sam_top_address_bit0":     (45, 40),
    "hn_cfg_six_sn_en":                37,
    "hn_cfg_three_sn_en":              36,
    "hn_cfg_sn2_nodeid":               (34, 24),
    "hn_cfg_sn1_nodeid":               (22, 12),
    "hn_cfg_sn0_nodeid":               (10, 0)})

sys_cache_grp_hn_count_bf = Bitfield_LE({
    "scg3_num_hnf": (30, 24),
    "scg2_num_hnf": (22, 16),
    "scg1_num_hnf": (14, 8),
    "scg0_num_hnf": (6, 0)})


def sample_target(kind):
    nodes = [n.node_id for n in find_nodes(conf.cmn, node_types[kind])]
    nid = random.sample(nodes, 1)[0]
    targets = list(conf.cmn.sbsx_targets) + list(conf.cmn.hni_regions)
    tgt = dict(targets)[nid]
    return (nid, tgt)


def create_devices(nid):
    return SimpleNamespace(mem=mem, ram=ram, dummy=dummy)


def probe_cmn():
    # create a dummy cmn to probe out the nids that we need later
    cmn = simics.SIM_create_object(os.environ.get('CMN_CLASS'), None, [])
    hni_nids = [n.node_id for n in find_nodes(cmn, node_types['HN-I'])]
    sbsx_nids = [n.node_id for n in find_nodes(cmn, node_types['SBSX'])]
    simics.SIM_delete_objects([cmn])
    return (hni_nids, sbsx_nids)


def create_cmn_600(num_spaces=1):
    """Create a new cmn_600 and some devices used for test"""
    cmn = simics.pre_conf_object('cmn', os.environ.get('CMN_CLASS'))
    hni_nids, sbsx_nids = probe_cmn()
    cmn.hni_regions = []
    for nid in hni_nids:
        mem = simics.SIM_create_object('memory-space', f'hni{nid}_mem', [])
        ram_img = simics.SIM_create_object(
            'image', f'hni{nid}_img', [['size', 1 << 63]])
        ram = simics.SIM_create_object(
            'ram', f'hni{nid}_ram', [['image', ram_img]])
        dummy0 = simics.SIM_create_object('set-memory', f'hni{nid}_dummy0', [])
        dummy1 = simics.SIM_create_object('set-memory', f'hni{nid}_dummy1', [])
        regions = [mem, ram, dummy0, dummy1]
        cmn.hni_regions.append([nid, regions])

    cmn.sbsx_targets = []
    for nid in sbsx_nids:
        ram_img = simics.SIM_create_object(
            'image', f'sbsx{nid}_img', [['size', 1 << 63]])
        ram = simics.SIM_create_object(
            'ram', f'sbsx{nid}_ram', [['image', ram_img]])
        cmn.sbsx_targets.append([nid, ram])

    simics.SIM_add_configuration([cmn], None)
    return conf.cmn


obj_regs = None


def node_regs(obj, nodeid):
    global obj_regs
    if obj_regs is None:
        obj_regs = bank_regs(obj.bank.regs)
    for n in dir(obj_regs):
        if n.endswith(f'nid{nodeid}'):
            regs = getattr(obj_regs, n)
            # Workaround for annoying name-switch between CMN-700 and CMN-600
            for rname in dir(regs):
                if rname.startswith('por_hnf'):
                    reg = getattr(regs, rname)
                    alias = rname.replace('por_hnf', 'cmn_hns')
                    if 'por_hnf_unit_info' in rname:
                        field = reg.bitfield.field_ranges['num_ways']
                        reg.bitfield.field_ranges['slc_num_ways'] = field
                        reg.field.slc_num_ways = reg.field.num_ways
                    if 'por_hnf_cfg_ctl' in rname:
                        field = reg.bitfield.field_ranges['hnf_ocm_allways_en']
                        reg.bitfield.field_ranges['hns_ocm_allways_en'] = field
                        reg.field.hns_ocm_allways_en = reg.field.hnf_ocm_allways_en
                        field = reg.bitfield.field_ranges['hnf_ocm_en']
                        reg.bitfield.field_ranges['hns_ocm_en'] = field
                        reg.field.hns_ocm_en = reg.field.hnf_ocm_en
                    setattr(regs, alias, reg)
            return regs


def print_map(data):
    props = [(table.Table_Key_Columns,
              [[(table.Column_Key_Name, n)] for n in
               ["Base", "Object", "Fn", "Offset", "Length"]])]
    print(
        table.Table(props, data).to_string(rows_printed=0, no_row_column=True))
