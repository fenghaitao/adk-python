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


import stest
from dev_util import READ
from cmn_600_common import (create_cmn_600, find_nodes, node_types, node_regs, print_map)
import random
import simics
random.seed(5313545496926614570)
from unittest import TestCase
tc = TestCase()

cmn = create_cmn_600()

rnsam_nids = [r.node_id for r in find_nodes(cmn, node_types["RN-SAM"])]
hni_nids = [r.node_id for r in find_nodes(cmn, node_types["HN-I"])]

rnsam = node_regs(cmn, random.sample(rnsam_nids, 1)[0])
phys_mem = cmn.memory_space[rnsam.por_rnsam_node_info.field.node_id.read()]
default_map = [me[:5] for me in phys_mem.map]
hni = node_regs(cmn, random.sample(hni_nids, 1)[0])
hni_regions = dict(list(cmn.hni_regions))[
    hni.por_hni_node_info.field.node_id.read()]

sz = random.randrange(23)
length = 0x4000000 * (1 << sz)
base = length * random.randrange((1 << 48) // length)

if rnsam.non_hash_mem_region_reg0.size == 4:
    base_shift = 26  # CMN-600
else:
    base_shift = 16  # CMN-700

rnsam.non_hash_mem_region_reg0.write(
    READ, region0_base_addr=base >> base_shift, region0_size=sz,
    region0_target_type=1, region0_valid=1)
rnsam.non_hash_tgt_nodeid0.write(
    READ, nodeid_0=hni.por_hni_node_info.field.node_id.read())

############################
# default + 3 discrete regions
max_size = ((length // 4) >> 12).bit_length() - 1
rsz = random.randrange(max_size)
rbase = base
region_length = 0x1000 << rsz
rstep = length // 4

for i in range(4):
    r = getattr(hni, f'por_hni_sam_addrregion{i}_cfg')
    if i == 0:
        print("region %d @ 0x%012x size 0x%x" % (i, base, length))
        continue
    rbase += rstep
    r.write(READ, valid=1, base_addr=rbase >> 12, addr_region_size=rsz)

# Unstall and enable
rnsam.rnsam_status.write(READ, nstall_req=1, use_default_node=0)
simics.SIM_run_command(f'{phys_mem.name}.map')

expected_map = sorted([
    [base,             hni_regions[0], 0, base,             length],
    [base + rstep * 1, hni_regions[1], 0, base + rstep * 1, region_length],
    [base + rstep * 2, hni_regions[2], 0, base + rstep * 2, region_length],
    [base + rstep * 3, hni_regions[3], 0, base + rstep * 3, region_length],
] + default_map)
got_map = sorted([m[:5] for m in phys_mem.map])

try:
    tc.assertListEqual(got_map, expected_map)
except AssertionError:
    print("expected map")
    print_map(list(expected_map))
    print("actual map")
    print_map(list(got_map))
    raise

cmn.ports.HRESET.signal.signal_raise()
cmn.ports.HRESET.signal.signal_lower()

############################
# default + 1 region larger than mapping
sz = random.randrange(20)
length = 0x4000000 * (1 << sz)
base = length * random.randrange((1 << 48) // length)
rnsam.non_hash_mem_region_reg0.write(
    READ, region0_base_addr=base >> base_shift, region0_size=sz,
    region0_target_type=1, region0_valid=1)
rnsam.non_hash_tgt_nodeid0.write(
    READ, nodeid_0=hni.por_hni_node_info.field.node_id.read())

rsz = sz + 14 + 1  # double the size of the mapping
region_length = (0x1000 << rsz)
rbase = max(base - (region_length // 4), 0)
print("map region 1 @ 0x%012x size 0x%x" % (rbase, region_length))
hni.por_hni_sam_addrregion1_cfg.write(
    READ, valid=1, base_addr=rbase >> 12, addr_region_size=rsz)

# Unstall and enable
rnsam.rnsam_status.write(READ, nstall_req=1, use_default_node=0)
simics.SIM_run_command(f'{phys_mem.name}.map')

expected_map = sorted([
    [base, hni_regions[0], 0, base, length],
    [base, hni_regions[1], 0, base, length],
] + default_map)
got_map = sorted([m[:5] for m in phys_mem.map])
try:
    tc.assertListEqual(got_map, expected_map)
except AssertionError:
    print("expected map")
    print_map(list(expected_map))
    print("actual map")
    print_map(list(got_map))
    raise

cmn.ports.HRESET.signal.signal_raise()
cmn.ports.HRESET.signal.signal_lower()

############################
# default + 2 regions partly outside mapping
sz = random.randrange(20)
length = 0x4000000 * (1 << sz)
base = length * random.randrange(1, (1 << 48) // length)
rnsam.non_hash_mem_region_reg0.write(
    READ, region0_base_addr=base >> base_shift, region0_size=sz,
    region0_target_type=1, region0_valid=1)
rnsam.non_hash_tgt_nodeid0.write(
    READ, nodeid_0=hni.por_hni_node_info.field.node_id.read())

rsz = sz + 14  # same size as the mapping
region_length = (0x1000 << rsz)
base1 = base - (region_length // 2)
print("map region 1 @ 0x%012x size 0x%x" % (base1, region_length))
hni.por_hni_sam_addrregion1_cfg.write(
    READ, valid=1, base_addr=base1 >> 12, addr_region_size=rsz)

base2 = base + (region_length // 2)
print("map region 1 @ 0x%012x size 0x%x" % (base2, region_length))
hni.por_hni_sam_addrregion2_cfg.write(
    READ, valid=1, base_addr=base2 >> 12, addr_region_size=rsz)

# Unstall and enable
rnsam.rnsam_status.write(READ, nstall_req=1, use_default_node=0)
simics.SIM_run_command(f'{phys_mem.name}.map')

expected_map = sorted([
    [base,  hni_regions[0], 0, base,  length],
    [base,  hni_regions[1], 0, base,  length // 2],
    [base2, hni_regions[2], 0, base2, length // 2],
] + default_map)
got_map = sorted([m[:5] for m in phys_mem.map])
stest.expect_equal(got_map, expected_map)

cmn.ports.HRESET.signal.signal_raise()
cmn.ports.HRESET.signal.signal_lower()

############################
# default + 2 regions completely outside mapping
sz = random.randrange(2, 20)
length = 0x4000000 * (1 << sz)
base = length * random.randrange(1, (1 << 47) // length)

rnsam.non_hash_mem_region_reg0.write(
    READ, region0_base_addr=base >> base_shift, region0_size=sz,
    region0_target_type=1, region0_valid=1)
rnsam.non_hash_tgt_nodeid0.write(
    READ, nodeid_0=hni.por_hni_node_info.field.node_id.read())


rsz = 1
region_length = (0x1000 << rsz)
rbase = base - region_length
print("map region 1 @ 0x%012x size 0x%x" % (rbase, region_length))
hni.por_hni_sam_addrregion1_cfg.write(
    READ, valid=1, base_addr=rbase >> 12, addr_region_size=rsz)

rbase = base + length
hni.por_hni_sam_addrregion2_cfg.write(
    READ, valid=1, base_addr=rbase >> 12, addr_region_size=rsz)

# Unstall and enable
rnsam.rnsam_status.write(READ, nstall_req=1, use_default_node=0)
simics.SIM_run_command(f'{phys_mem.name}.map')

expected_map = sorted([[base, hni_regions[0], 0, base, length]] + default_map)
got_map = sorted([m[:5] for m in phys_mem.map])
stest.expect_equal(got_map, expected_map)

cmn.ports.HRESET.signal.signal_raise()
cmn.ports.HRESET.signal.signal_lower()

############################
# default only
# Test with only one region "connected"
new_regions = []
for (nid, regions) in cmn.hni_regions:
    new_regions.append([nid, regions[0]])
cmn.hni_regions = new_regions

sz = random.randrange(23)
length = 0x4000000 * (1 << sz)
base = length * random.randrange((1 << 48) // length)

rnsam.non_hash_mem_region_reg0.write(
    READ, region0_base_addr=base >> base_shift, region0_size=sz,
    region0_target_type=1, region0_valid=1)
rnsam.non_hash_tgt_nodeid0.write(
    READ, nodeid_0=hni.por_hni_node_info.field.node_id.read())

# Unstall and enable
rnsam.rnsam_status.write(READ, nstall_req=1, use_default_node=0)
simics.SIM_run_command(f'{phys_mem.name}.map')

expected_map = sorted([[base, hni_regions[0], 0, base, length]] + default_map)
got_map = sorted([m[:5] for m in phys_mem.map])
stest.expect_equal(got_map, expected_map)

cmn.ports.HRESET.signal.signal_raise()
cmn.ports.HRESET.signal.signal_lower()
