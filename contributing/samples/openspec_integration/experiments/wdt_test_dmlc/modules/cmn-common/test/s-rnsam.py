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


if regs.non_hash_mem_region[0].size == 4:
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

for i, r in regs.non_hash_mem_region.items():
    sz = random.randint(0, 22)
    length = 0x4000000 * (1 << sz)
    base = length * random.randrange((1 << 48) // length)
    r.write(READ, base_addr=base >> base_shift, sz=sz, target_type=1, valid=1)
    nid, tgt = sample_target("HN-I")
    args = {"nid[%d]" % (i % 4): nid}
    regs.non_hash_tgt_nodeid[i // 4].write(READ, **args)
    expected_map += exp_map(nid, tgt, base, length)


hnfs = [(n.node_id, node_regs(conf.cmn, n.node_id))
        for n in find_nodes(conf.cmn, node_types["HN-F"])]
nid_regs = len(regs.sys_cache_grp_hn_nodeid)
scg_regs = len(regs.sys_cache_grp_region)
nid_regs_per_scg = nid_regs // scg_regs

regs.sys_cache_group_hn_count.write(0x2020202)  # 2 HN-F's per SCG
sample_hnfs = random.sample(hnfs, len(regs.sys_cache_grp_region))
for i, r in regs.sys_cache_grp_region.items():
    ram_nid, ram_obj = sample_target("SBSX")
    hnf_nid, hnf_regs = sample_hnfs.pop()
    hnf_regs.cmn_hns_sam_control.write(ram_nid)

    j = i * nid_regs_per_scg
    # Design Limitation: Hashed regions always hit the first nodeid,
    # so it doesn't matter what we program in nid[x > 0]
    regs.sys_cache_grp_hn_nodeid[j].write(
        READ, nid={n: hnf_nid for n in range(4)})

    sz = random.randint(0, 22)
    length = 0x4000000 * (1 << sz)
    base = length * random.randrange((1 << 48) // length)
    r.write(READ, base_addr=base >> base_shift, sz=sz, target_type=0, valid=1)
    expected_map += exp_map(ram_nid, ram_obj, base, length)

for i, r in regs.sys_cache_grp_secondary.items():
    # Secondary SCG use same targets as primary
    j = i * nid_regs_per_scg
    hnf_nid = regs.sys_cache_grp_hn_nodeid[j].field.nid[0].read()
    hnf_regs = node_regs(conf.cmn, hnf_nid)
    ram_nid = hnf_regs.cmn_hns_sam_control.read()
    ram_obj = dict(list(cmn.sbsx_targets))[ram_nid]

    sz = random.randint(0, 22)
    length = 0x4000000 * (1 << sz)
    base = length * random.randrange((1 << 48) // length)
    r.write(base_addr=base >> base_shift, sz=sz, target_type=0, valid=1)
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
