# © 2010 Intel Corporation

import stest
import simics
import watchdog_timer_common

# Create an instance of the watchdog timer
dev = watchdog_timer_common.create_watchdog_timer()

# Test that the device was created successfully
stest.expect_true(dev is not None)
stest.expect_equal(dev.classname, 'watchdog_timer')

print("Info-status test completed successfully")