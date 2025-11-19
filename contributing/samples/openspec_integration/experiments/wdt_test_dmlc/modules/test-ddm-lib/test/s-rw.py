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

import dev_util
import stest

dev = SIM_create_object('test_ddm_lib', 'dev')
bank = dev_util.bank_regs(dev.bank.test_bank)
r2 = bank.r2
r3 = bank.r3
r5 = bank.r5

def clear(dev):
    dev.clear_all = None

clear(dev)
r2.val = 0x1122334455667788
dev.validate_ret = 0xaaaaaaaa
dev.ret = 0xdeadbeef
r2.write(0xff00ff00)
stest.expect_equal(dev.write_offset, r2.offset)
stest.expect_equal(dev.curr_val, 0x1122334455667788)
stest.expect_equal(dev.written_val, 0xff00ff00)
stest.expect_equal(dev.enabled_bits, 0xffffffffffffffff)
# aux is whatever was passed to default bank.write
stest.expect_equal(dev.aux, 15)
stest.expect_true(dev.impl_called)
# the only thing that matters is what write_impl returns
stest.expect_equal(r2.val, 0xdeadbeef)

clear(dev)

r2.val = 0x12345678
dev.validate_ret = 0xaaaaaaaa
dev.ret = 0xdeadbeef

stest.expect_equal(r2.read(), 0xdeadbeef)
stest.expect_equal(dev.read_offset, r2.offset)
stest.expect_equal(dev.curr_val, 0x12345678)
stest.expect_equal(dev.enabled_bits, 0xffffffffffffffff)
stest.expect_true(dev.impl_called)
# aux is whatever was passed to default bank.read
stest.expect_equal(dev.aux, 14)

part = dev_util.Register_LE(dev.bank.test_bank, r2.offset + 3, size=3)

# impl is only called if enabled_bits and validate_ret overlap
clear(dev)
dev.validate_ret = 0xffff000000ffffff
part.write(0xfedcba)
stest.expect_equal(dev.enabled_bits, 0x0000ffffff000000)
stest.expect_false(dev.impl_called)
stest.expect_equal(part.read(), 0)
stest.expect_false(dev.impl_called)

# one bit of enabled_bits/validate_ret overlap is sufficient for impl to be called
for validate_ret in [1 << 24, 1 << 47]:
    clear(dev)
    r2.val = 0x1122334455667788
    dev.validate_ret = validate_ret
    dev.ret = 0xdeadbeef
    part.write(0xfedcba)
    stest.expect_equal(dev.enabled_bits, 0x0000ffffff000000)
    stest.expect_equal(dev.curr_val, 0x1122334455667788)
    stest.expect_equal(dev.written_val, 0x0000fedcba000000)
    stest.expect_true(dev.impl_called)
    stest.expect_equal(r2.val, 0xdeadbeef)

    clear(dev)
    r2.val = 0x1122334455667788
    dev.validate_ret = validate_ret
    dev.ret = 0xfedcba9876543210
    stest.expect_equal(part.read(), 0xba9876)
    stest.expect_true(dev.impl_called)

dev.validate_ret = 0xffffffffffffffff
dev.ret = 0xdeadbeefdeadbeef
dev.bank.test_bank.r3_hi_f2_set_flag = False
r3.write(0xdeadbeefdeadbeef)
stest.expect_equal(r3.val, 0xdeadbeefdeadbeef)
stest.expect_equal(dev.bank.test_bank.r3_hi_f2_set_flag, True)

clear(dev)

dev.validate_ret = 0xffffffffffffffff
dev.ret = 0xdeadbeefdeadbeef
dev.bank.test_bank.r5_hi_f2_set_flag = False
r5.write(0xdeadbeefdeadbeef)
stest.expect_equal(r5.val, 0xdeadbeefdeadbeef)
stest.expect_equal(dev.bank.test_bank.r5_hi_f2_set_flag, True)

clear(dev)

overlap_bank = dev_util.bank_regs(dev.bank.test_bank_overlap)
o_r0 = overlap_bank.r0
o_r1 = overlap_bank.r1

overlapping = dev_util.Register_LE(dev.bank.test_bank_overlap, 0x2, size=8)
dev.test_overlap_validate_ret[0] = 0xffff0000_ffff0000
dev.test_overlap_ret[0]          = 0xfeed0000_beef0000
dev.test_overlap_validate_ret[1] = 0x0000ffff_0000ffff
dev.test_overlap_ret[1]          = 0x0000face_0000dead

overlapping.write(0xfacefeed_deadbeef)

stest.expect_equal(dev.test_overlap_enabled_bits[0], 0xffffffff_ffff0000)
stest.expect_equal(dev.test_overlap_enabled_bits[1], 0x0000ffff_ffffffff)
stest.expect_equal(dev.test_overlap_written_val[0],  0xfeeddead_beef0000)
stest.expect_equal(dev.test_overlap_written_val[1],  0x0000face_feeddead)
stest.expect_equal(o_r0.val, 0xfeed0000_beef0000)
stest.expect_equal(o_r1.val, 0x0000face_0000dead)

clear(dev)

o_r0.val = 0xfeedface_facefeed
o_r1.val = 0xbeefdead_deadbeef

dev.test_overlap_validate_ret[0] = 0xffff0000_ffff0000
dev.test_overlap_validate_ret[1] = 0x0000ffff_0000ffff
dev.test_overlap_ret[0]          = 0xfeedffff_faceffff
dev.test_overlap_ret[1]          = 0xffffdead_ffffbeef

stest.expect_equal(overlapping.read(), 0xdeadfeed_beefface)
stest.expect_equal(dev.test_overlap_enabled_bits[0], 0xffffffff_ffff0000)
stest.expect_equal(dev.test_overlap_enabled_bits[1], 0x0000ffff_ffffffff)
stest.expect_equal(dev.test_overlap_curr_val[0],  0xfeedface_facefeed)
stest.expect_equal(dev.test_overlap_curr_val[1],  0xbeefdead_deadbeef)

clear(dev)

dev.test_overlap_validate_ret[0] = 0x0000ffff_00000000
dev.test_overlap_validate_ret[1] = 0x00000000_0000ffff
dev.test_overlap_ret[0]          = 0xffffdead_ffffffff
dev.test_overlap_ret[1]          = 0xffffffff_ffffface

dev.bypass_read_asserts = True
class LogCapture(object):
    def __init__(self):
        self.messages = []
        self.filter = sim_commands.logger.filter(self.callback)
    def __enter__(self):
        self.filter.__enter__()
        return self
    def __exit__(self, *args):
        return self.filter.__exit__(*args)
    def callback(self, obj_, kind, msg):
        stest.expect_equal(obj_, dev)
        self.messages.append(msg)

with LogCapture() as capture, stest.expect_log_mgr(dev, 'spec-viol'):
    stest.expect_equal(overlapping.read(), 0xffffffff_faceffff)

messages = capture.messages
stest.expect_equal(len(messages), 1)
stest.expect_true("test_bank_overlap: 8 byte read access at offset 0x2" in messages[0])
stest.expect_true("Registers involved in the access: r0, r1" in messages[0])
