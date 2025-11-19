# INTEL CONFIDENTIAL

# © 2024 Intel Corporation
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
from dev_util import bank_regs

sys.path.append(os.path.join('..', '..', 'cmn-common', 'test'))
from cmn_600_common import *
cmn = create_cmn_600()
regs = bank_regs(cmn.bank.regs)

cmn.bank.regs.f3_is_locked = True
stest.expect_equal(regs.locked.read(), 0)
regs.locked.write(f1=3, f2=0, f3=3)
stest.expect_equal(regs.locked.field.f1.read(), 0)
stest.expect_equal(regs.locked.field.f3.read(), 0)
regs.locked.write(f1=4, f2=1, f3=4)
stest.expect_equal(regs.locked.field.f1.read(), 0)
stest.expect_equal(regs.locked.field.f3.read(), 0)
regs.locked.write(f1=5, f2=2, f3=5)
stest.expect_equal(regs.locked.field.f1.read(), 5)
stest.expect_equal(regs.locked.field.f3.read(), 0)
regs.locked.write(f1=6, f2=2, f3=6)
stest.expect_equal(regs.locked.field.f1.read(), 5)
stest.expect_equal(regs.locked.field.f3.read(), 0)
regs.locked.write(f1=7, f2=1, f3=7)
cmn.bank.regs.f3_is_locked = False
stest.expect_equal(regs.locked.field.f1.read(), 5)
stest.expect_equal(regs.locked.field.f3.read(), 0)
