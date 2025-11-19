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
import simics
from cmn_600_common import create_cmn_600, cmn_regs, find_nodes, node_types
import random

cmn = create_cmn_600()
mt = simics.SIM_new_map_target(cmn.default_space, None, None)


def read(offs, sz):
    t = simics.transaction_t(size=sz, read=True)
    if simics.SIM_issue_transaction(mt, t, offs) != simics.Sim_PE_No_Exception:
        raise(simics.SimExc_Memory)
    return t.value_le


def write(offs, sz, val=0):
    t = simics.transaction_t(size=sz, write=True, value_le=val)
    if simics.SIM_issue_transaction(mt, t, offs) != simics.Sim_PE_No_Exception:
        raise(simics.SimExc_Memory)


# Figure out the expected size of the CFGM_PERIPHBASE region
periphid0 = read(cmn.rootnodebase + 8, 8) & 0xff
if periphid0 == 0x3c:  # CMN-700
    if any(n.node_id & (0b11 << 9) for n in find_nodes(cmn, node_types['XP'])):
        size = 0x40000000  # 1GB
    else:
        size = 0x10000000  # 256MB
elif periphid0 == 0x34:  # CMN-600
    size = 0x4000000  # 64MB
else:
    stest.fail("Unknown CMN, periph_id_0 is 0x%x", periphid0)

# Test driving an unaligned PERIPHBASE
with stest.expect_log_mgr(cmn, "spec-viol"):
    cmn.periphbase = random.randrange(1 << 63)
cmn.periphbase = random.randrange(1 << 63) & ~(size - 1)


stest.untrap_log('spec-viol')
simics.SIM_run_command(f'{cmn.name}.log-level 3')
failed = []
read_only = []
for r in cmn_regs:
    (offs, sz, tmpl, name, desc, *dontcare) = r
    addr = offs + cmn.periphbase
    try:
        val = read(addr, sz)
        if tmpl == "read_only":
            with stest.expect_log_mgr(log_type="spec-viol", regex="read-only"):
                write(addr, sz, ~val & ((1 << (sz * 8)) - 1))
            stest.expect_equal(read(addr, sz), val)
        else:
            write(addr, sz)

    except stest.TestFailure:
        read_only.append(r)
    except simics.SimExc_Memory:
        failed.append(r)

for (offs, sz, tmpl, name, desc) in failed:
    print("Failed accessing %s (%s) @ 0x%x : %s" % (name, tmpl, offs, desc))
for (offs, sz, tmpl, name, desc) in read_only:
    print("Expected spec-viol when writing to %s (%s) @ 0x%x : %s"
          % (name, tmpl, offs, desc))

if failed or read_only:
    stest.fail("Register access is not consistent with XML")

with stest.expect_exception_mgr(simics.SimExc_Memory):
    read(min(offs for (offs, *dontcare) in cmn_regs) - 1, 1)
with stest.expect_exception_mgr(simics.SimExc_Memory):
    read(max(offs + sz for (offs, sz, *dontcare) in cmn_regs), 1)

cmn.port.HRESET.iface.signal.signal_raise()
t = simics.transaction_t(size=16)
cmn.bank.regs.log_level = 2
with stest.expect_log_mgr(log_type='info', msg="reset"):
    simics.SIM_issue_transaction(mt, t, 0)
stest.expect_equal(t.data, b'\x00' * t.size)
cmn.bank.regs.log_level = 1
cmn.port.HRESET.iface.signal.signal_lower()


exp = read(cmn.periphbase + cmn.rootnodebase, 8)
cmn.port.CFGM_PERIPHBASE.iface.uint64_state.set(0)
stest.expect_equal(read(cmn.rootnodebase, 8), exp)
