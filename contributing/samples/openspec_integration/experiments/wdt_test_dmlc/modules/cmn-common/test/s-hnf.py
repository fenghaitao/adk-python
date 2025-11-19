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


import conf
import stest
from cmn_600_common import (
    create_cmn_600, find_nodes, node_regs, node_types, sample_target)
from dev_util import Register_LE, Bitfield_LE, READ
import random
random.seed(3252)
from unittest import TestCase
tc = TestCase()

cmn = create_cmn_600()

rnsam = node_regs(cmn, find_nodes(cmn, node_types["RN-SAM"])[0].node_id)
ms = cmn.memory_space[rnsam.por_rnsam_node_info.field.node_id.read()]
nsmap = list(ms.map)

hnf_nids = [r.field.node_id.read() for r in find_nodes(cmn, node_types["HN-F"])]
hnf_nodes = [node_regs(cmn, nid) for nid in hnf_nids]
hnd_nid = [r.node_id for r in find_nodes(cmn, node_types["DVM"])][0]
hnd_regions = dict(list(conf.cmn.hni_regions))[hnd_nid]
ocm = [getattr(cmn.bank.regs, f'hnf_nid{nid}').ocm.ram for nid in hnf_nids]

# Map entire On-Chip Memory
cmn_600_sizes = [0, 0x020000, 0x040000, 0x080000,
                 0x100000, 0x200000, 0x300000, 0x400000]
ocm_size = cmn_600_sizes[hnf_nodes[0].cmn_hns_unit_info.field.slc_size.read()]
way_size = ocm_size // hnf_nodes[0].cmn_hns_unit_info.field.slc_num_ways.read()
ocm_total = ocm_size * len(hnf_nodes)

# Setup all SCG HN nodeid targets
nids = list(sorted(hnf_nids))
for s, scg in rnsam.sys_cache_grp_hn_nodeid.items():
    args = {}
    for n in range(4):
        nid = nids.pop()
        if nid & 1:  # must enable CAL2 mode
            rnsam.sys_cache_grp_cal_mode_reg.write(
                READ, **{f"scg{s}_hnf_cal_mode_en": 1})
            nid = nids.pop()  # upper NID isn't explicitly listed in CAL2
        args[f"nid[{n}]"] = nid
    scg.write(**args)
    if not nids:
        break

# Lock all cache ways in all HN-F's
for regs in hnf_nodes:
    regs.cmn_hns_cfg_ctl.write(READ, hns_ocm_allways_en=1, hns_ocm_en=1)
    # write an unaligned base, should be corrected by hw, model should complain
    regs.cmn_hns_slc_lock_base[0].write(READ, valid=1, base=1)

rnsam.sys_cache_group_hn_count.write(len(hnf_nids))  # Number of HNs in first SCG
rnsam.sys_cache_grp_region[0].write(
    READ, base_addr=0, sz=0, target_type=0, valid=1)

with stest.expect_log_mgr(obj=cmn.bank.regs,
                          log_type="spec-viol", regex="unaligned"):
    rnsam.rnsam_status.write(READ, nstall_req=1, use_default_node=0)

# check that the HN-D is default target
tc.assertListEqual(ms.default_target[:4], [hnd_regions[0], 0, 0, None])

# Check that all OCM's got mapped with full size
got_map = set([(m[1], m[4]) for m in ms.map if m[1] in ocm])
exp_map = set([(o, ocm_size) for o in ocm])
tc.assertSetEqual(got_map, exp_map)

# Check that the base's (Secure and Non-Secure) align
got_bases = [m[0] for m in ms.map if m[1] in ocm]
exp_bases = list(range(0, ocm_size * len(hnf_nodes), ocm_size))
tc.assertListEqual(got_bases, exp_bases)

# Check that we can write
# fill silently quits when it reaches a non-ram target so we
# check the count
cnt = ms.iface.memory_space.fill(0, ocm_total + 1, 0xaa, False)
tc.assertEqual(cnt, ocm_total)

# Check that what we wrote reached all images
for o in ocm:
    got  = o.image.iface.image.get(0, 1)
    got += o.image.iface.image.get(ocm_size - 1, 1)
    tc.assertEqual(got, b'\xaa\xaa')
    o.image.iface.image.clear_range(0, ocm_size)

cmn.ports.HRESET.signal.signal_raise()
cmn.ports.HRESET.signal.signal_lower()

tc.assertEqual(ms.default_target, None)
tc.assertListEqual(list(ms.map), nsmap)

# Map partial OCM
region_sizes = {
    1:   [1 * way_size,             0,             0,             0],
    2:   [1 * way_size,  1 * way_size,             0,             0],
    4:   [1 * way_size,  1 * way_size,  1 * way_size,  1 * way_size],
    8:   [2 * way_size,  2 * way_size,  2 * way_size,  2 * way_size],
    12:  [2 * way_size,  2 * way_size,  4 * way_size,  4 * way_size],
}


(ram_nid, dev) = sample_target("SBSX")


hnf_regs = {r.cmn_hns_node_info.field.node_id.read(): r for r in hnf_nodes}


def setup_hnf(nid, lock_ways, rgn_base):
    regs = hnf_regs[nid]
    regs.cmn_hns_sam_control.write(ram_nid)
    regs.cmn_hns_cfg_ctl.write(READ, hns_ocm_en=1)
    regs.cmn_hns_slc_lock_ways.write(lock_ways)
    for rgn, sz in enumerate(region_sizes[lock_ways]):
        if sz == 0:
            break
        regs.cmn_hns_slc_lock_base[rgn].write(
            READ, valid=1, base=rgn_base)
        rgn_base += sz * len(hnf_nodes)


def xp_info_reg(offset):
    return Register_LE(conf.cmn.bank.regs, offset, 8,
                       bitfield=Bitfield_LE({'num_device_ports': (51, 48)}))


xp_nodes = (xp_info_reg(r.ofs)
            for r in find_nodes(conf.cmn, node_types['XP']))
if any(r.num_device_ports > 2 for r in xp_nodes):
    print("Extra device ports detected, CAL4 not possible")
    cal4_possible = False
else:
    cal4_possible = True

for lock_ways in [1, 2, 4, 8, 12]:
    base = 0
    # map all HNs to SCG0
    i = 0
    for nid in sorted(hnf_nids):
        setup_hnf(nid, lock_ways, base)
        if nid & 1:
            # must enable CAL2
            rnsam.sys_cache_grp_cal_mode_reg.write(READ, scg0_hnf_cal_mode_en=1)
            if cal4_possible and nid & 2:
                # must enable CAL4
                rnsam.sys_cache_grp_cal_mode_reg.write(READ, scg0_hnf_cal_type=1)
        else:
            reg = i // 4
            fld = i % 4
            rnsam.sys_cache_grp_hn_nodeid[reg].write(READ, nid={fld: nid})
            i += 1

    ocm_total = sum(region_sizes[lock_ways]) * len(hnf_nodes)

    rnsam.sys_cache_group_hn_count.write(len(hnf_nodes))
    rnsam.sys_cache_grp_region[0].write(
        READ, base_addr=0, sz=0, target_type=0, valid=1)
    rnsam.rnsam_status.write(READ, nstall_req=1, use_default_node=0)

    # Check that we have an SN0 map
    exp_map = [[0, dev, 0, 0, 64 * 1024 * 1024]]
    sn0_map = [m[:5] for m in ms.map if m[1] == dev]
    tc.assertListEqual(sn0_map, exp_map)

    # Check that we have the expected OCM size
    total_mapped = sum([m[4] for m in ms.map if m[1] in ocm])
    tc.assertEqual(total_mapped, ocm_total)

    # use fill to check that we have a continuous block of RAM
    # corresponding to the entire locked OCM
    cnt = ms.iface.memory_space.fill(0, ocm_total, 0xaa, False)
    tc.assertEqual(cnt, ocm_total)

    # Check that we can write
    test_writes = list((addr, (random.randrange(256),))
                       for addr in range(0, ocm_total, way_size))
    for addr, val in test_writes:
        ms.iface.memory_space.write(None, addr, val, False)
    for addr, exp in test_writes:
        got = ms.iface.memory_space.read(None, addr, 1, False)
        tc.assertEqual(got, exp)

    cmn.ports.HRESET.signal.signal_raise()
    cmn.ports.HRESET.signal.signal_lower()
