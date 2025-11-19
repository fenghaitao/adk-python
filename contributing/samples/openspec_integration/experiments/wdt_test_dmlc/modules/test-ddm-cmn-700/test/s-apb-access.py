# INTEL CONFIDENTIAL

# © 2023 Intel Corporation
#
# This software and the related documents are Intel copyrighted materials, and
# your use of them is governed by the express license under which they were
# provided to you ("License"). Unless the License provides otherwise, you may
# not use, modify, copy, publish, distribute, disclose or transmit this software
# or the related documents without Intel's prior written permission.
#
# This software and the related documents are provided as is, with no express or
# implied warranties, other than those that are expressly stated in the License.

import os
import sys
import conf
import stest

sys.path.append(os.path.join('..', '..', 'cmn-common', 'test'))
from cmn_600_common import *

cmn = create_cmn_600()
apb_mt = simics.SIM_new_map_target(cmn.bank.apb_regs, None, None)
chi_mt = simics.SIM_new_map_target(cmn.bank.chi_axi_regs, None, None)


# APB access

# no atoms
t = simics.transaction_t(size=8)
exc = simics.SIM_issue_transaction(apb_mt, t, 0x10000)
stest.expect_equal(exc, simics.Sim_PE_No_Exception)
exc = simics.SIM_issue_transaction(apb_mt, t, 0x10980)
stest.expect_equal(exc, simics.Sim_PE_No_Exception)
stest.expect_equal(t.value_le, 0x0)

# S transaction
t = simics.transaction_t(size=8, arm_nonsecure=False)
exc = simics.SIM_issue_transaction(apb_mt, t, 0x10000)
stest.expect_equal(exc, simics.Sim_PE_No_Exception)
exc = simics.SIM_issue_transaction(apb_mt, t, 0x10980)
stest.expect_equal(exc, simics.Sim_PE_No_Exception)
stest.expect_equal(t.value_le, 0x0)

# NS transaction
t = simics.transaction_t(size=8, arm_nonsecure=True)
exc = simics.SIM_issue_transaction(apb_mt, t, 0x10000)
stest.expect_equal(exc, simics.Sim_PE_No_Exception)
exc = simics.SIM_issue_transaction(apb_mt, t, 0x10980)
stest.expect_equal(exc, Sim_PE_IO_Not_Taken)

# NS inquiry transaction
t = simics.transaction_t(size=8, arm_nonsecure=True, inquiry=True)
exc = simics.SIM_issue_transaction(apb_mt, t, 0x10000)
stest.expect_equal(exc, simics.Sim_PE_No_Exception)
exc = simics.SIM_issue_transaction(apb_mt, t, 0x10980)
stest.expect_equal(exc, simics.Sim_PE_No_Exception)
stest.expect_equal(t.value_le, 0x0)


# CHI/AXI access

t = simics.transaction_t(size=8)
with stest.allow_log_mgr(cmn.bank.regs, 'spec-viol'):
    exc = simics.SIM_issue_transaction(chi_mt, t, 0x10000)
    stest.expect_equal(exc, Sim_PE_IO_Not_Taken)
    exc = simics.SIM_issue_transaction(chi_mt, t, 0x10980)
    stest.expect_equal(exc, Sim_PE_IO_Not_Taken)
exc = simics.SIM_issue_transaction(chi_mt, t, 0x20000)
stest.expect_equal(exc, simics.Sim_PE_No_Exception)

# set cmn_apb_only
t = simics.transaction_t(write=True, size=8, value_le=0x1)
exc = simics.SIM_issue_transaction(apb_mt, t, 0x10980)
stest.expect_equal(exc, simics.Sim_PE_No_Exception)

# RAZ
t = simics.transaction_t(size=8)
exc = simics.SIM_issue_transaction(chi_mt, t, 0x20000)
stest.expect_equal(exc, simics.Sim_PE_No_Exception)
stest.expect_equal(t.value_le, 0x0)

# write dropped
t = simics.transaction_t(write=True, size=8, value_le=0xff)
exc = simics.SIM_issue_transaction(chi_mt, t, 0x20980)
stest.expect_equal(exc, Sim_PE_IO_Not_Taken)


# Inquiry during reset
cmn.port.HRESET.iface.signal.signal_raise()

t = simics.transaction_t(size=8)
exc = simics.SIM_issue_transaction(apb_mt, t, 0x10980)
stest.expect_equal(exc, simics.Sim_PE_No_Exception)
# por_apb_only_access should be clean after reset
stest.expect_equal(t.value_le, 0x0)

t = simics.transaction_t(size=8)
exc = simics.SIM_issue_transaction(chi_mt, t, 0x20000)
stest.expect_equal(exc, simics.Sim_PE_No_Exception)
# RAZ
stest.expect_equal(t.value_le, 0x0)
t = simics.transaction_t(size=8, inquiry=True)
exc = simics.SIM_issue_transaction(chi_mt, t, 0x20000)
stest.expect_equal(exc, simics.Sim_PE_No_Exception)
stest.expect_true(t.value_le != 0x0)
