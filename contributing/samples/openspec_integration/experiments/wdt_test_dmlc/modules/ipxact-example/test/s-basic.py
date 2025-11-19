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

"""
Basic tests for the IP-XACT example device
"""

import dev_util
import stest

# Create device
dev = SIM_create_object('ipxact_example', 'test_device')
stest.expect_equal(dev.classname, "ipxact_example")

# Access registers
bank = dev_util.bank_regs(dev.bank.watchdog_memap)
WDOGLOAD = bank.WDOGLOAD

# Simple read/write test
WDOGLOAD.write(0x12345678)
stest.expect_equal(WDOGLOAD.read(), 0x12345678)
