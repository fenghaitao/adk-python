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

import simics
import conf
from cmn_600_common import (
    create_cmn_600, find_nodes, node_regs, node_types, print_map, sample_target)
from unittest import TestCase
from dev_util import READ
import stest  # noqa import to trap on error/spec-viol
import random
random.seed(9843252)

tc = TestCase()
cmn = create_cmn_600()


rnsams = find_nodes(cmn, node_types["RN-SAM"])
regs = node_regs(
    cmn, rnsams[random.randrange(len(rnsams))].node_id)

# Check default target
hnd_nid = [r.node_id
           for r in find_nodes(cmn, node_types["DVM"])][0]
hnd_regions = dict(list(conf.cmn.hni_regions))[hnd_nid]
phys_mem = cmn.memory_space[regs.por_rnsam_node_info.field.node_id.read()]
nsmap = [me[:5] for me in phys_mem.map]


def exp_map(nid, tgt, base, length):
    # if target has regions, expect the first one
    dev = tgt if isinstance(tgt, simics.conf_object_t) else tgt[0]
    offs = base
    return [[base, dev, 0, offs, length]]


if regs.non_hash_mem_region_reg0.size == 4:
    base_shift = 26  # CMN-600
else:
    base_shift = 16  # CMN-700

tc.assertEqual(phys_mem.default_target, None)


# Let's do some mappings!
sz = random.randint(0, 3)
length = 0x10000 * (1 << sz)
base = length * random.randint(0, 10)
nid, tgt = sample_target("HN-I")
regs.gic_mem_region_reg.write(gic_region_nodeid=nid, gic_region_base_addr=base,
                              gic_region_size=sz, gic_region_target_type=1,
                              gic_region_valid=1)
expected_map = exp_map(nid, tgt, base, length)

for i in range(8):
    r = getattr(regs, f'non_hash_mem_region_reg{i}')
    sz = random.randint(0, 22)
    length = 0x4000000 * (1 << sz)
    base = length * random.randrange((1 << 48) // length)
    r.write(READ, **{
        f'region{i}_base_addr': base >> base_shift,
        f'region{i}_size': sz,
        f'region{i}_target_type': 1,
        f'region{i}_valid': 1})
    nid, tgt = sample_target("HN-I")
    nodeid_reg = getattr(regs, f'non_hash_tgt_nodeid{i // 4}')
    nodeid_reg.write(READ, **{f'nodeid_{i}': nid})
    expected_map += exp_map(nid, tgt, base, length)


hnfs = [(n.node_id, node_regs(conf.cmn, n.node_id))
        for n in find_nodes(conf.cmn, node_types["HN-F"])]

nid_regs = sum(1 for name in dir(regs)
               if name.startswith('sys_cache_grp_hn_nodeid_reg'))
assert nid_regs
scg_regs = sum(1 for name in dir(regs)
               if name.startswith('sys_cache_grp_region'))
assert scg_regs
nid_regs_per_scg = nid_regs // scg_regs

regs.sys_cache_group_hn_count.write(0x2020202)  # 2 HN-F's per SCG
sample_hnfs = random.sample(hnfs, scg_regs)
for i in range(scg_regs):
    r = getattr(regs, f'sys_cache_grp_region{i}')
    ram_nid, ram_obj = sample_target("SBSX")
    hnf_nid, hnf_regs = sample_hnfs.pop()
    hnf_regs.cmn_hns_sam_control.write(ram_nid)

    j = i * nid_regs_per_scg
    # Design Limitation: Hashed regions always hit the first nodeid,
    # so it doesn't matter what we program in nid[x > 0]
    nodeid_reg = getattr(regs, f'sys_cache_grp_hn_nodeid_reg{j}')
    nodeid_reg.write(READ, **{f'nodeid_{n + 4 * i}': hnf_nid for n in range(4)})

    sz = random.randint(0, 22)
    length = 0x4000000 * (1 << sz)
    base = length * random.randrange((1 << 48) // length)
    r.write(READ, **{
        f'region{i}_base_addr': base >> base_shift,
        f'region{i}_size': sz,
        f'region{i}_target_type': 0,
        f'region{i}_valid': 1})
    expected_map += exp_map(ram_nid, ram_obj, base, length)

num_scg_secondary = sum(1 for name in dir(regs)
                        if name.startswith('sys_cache_grp_secondary_reg'))
assert num_scg_secondary
for i in range(num_scg_secondary):
    r = getattr(regs, f'sys_cache_grp_secondary_reg{i}')
    # Secondary SCG use same targets as primary
    j = i * nid_regs_per_scg
    nodeid_reg = getattr(regs, f'sys_cache_grp_hn_nodeid_reg{j}')
    hnf_nid = getattr(nodeid_reg.field, f'nodeid_{i * 4}').read()
    hnf_regs = node_regs(conf.cmn, hnf_nid)
    ram_nid = hnf_regs.cmn_hns_sam_control.read()
    ram_obj = dict(list(cmn.sbsx_targets))[ram_nid]

    sz = random.randint(0, 22)
    length = 0x4000000 * (1 << sz)
    base = length * random.randrange((1 << 48) // length)
    r.write(**{
        f'region{i}_scndry_base_addr': base >> base_shift,
        f'region{i}_scndry_size': sz,
        f'region{i}_scndry_target_type': 0,
        f'region{i}_scndry_valid': 1})
    expected_map += exp_map(ram_nid, ram_obj, base, length)

expected_map += nsmap
# Unstall and enable
regs.rnsam_status.write(READ, nstall_req=1, use_default_node=0)
tc.assertListEqual(phys_mem.default_target[:4], [hnd_regions[0], 0, 0, None])

# extract, sort and compare maps
gmap = sorted([me[:5] for me in phys_mem.map])
emap = sorted(expected_map)
try:
    tc.assertListEqual(gmap, emap)
except AssertionError:
    print("expected map")
    print_map(list(emap))
    print("actual map")
    print_map(list(gmap))
    raise

cmn.ports.HRESET.signal.signal_raise()
tc.assertListEqual(
    phys_mem.default_target[:4], [cmn.impl.port.IGNORE, 0, 0, None])
cmn.ports.HRESET.signal.signal_lower()

tc.assertEqual(phys_mem.default_target, None)
