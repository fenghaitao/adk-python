# © 2010 Intel Corporation

import stest
import info_status
import simics
import wdt_common

# Verify that info/status commands have been registered for all
# classes in this module.
info_status.check_for_info_status(['wdt'])

# Create an instance of each object defined in this module
dev = wdt_common.create_wdt()

# Run info on each object. It is difficult to test whether
# the output is informative, so we just check that the commands
# complete nicely.
for obj in [dev]:
    try:
        simics.SIM_run_command(obj.name + '.info')
    except simics.SimExc_General as e:
        stest.fail('info command failed: ' + str(e))