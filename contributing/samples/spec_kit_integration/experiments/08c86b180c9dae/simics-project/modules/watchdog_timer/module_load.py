# © 2010 Intel Corporation

import cli

class_name = 'watchdog_timer'

#
# ------------------------ info -----------------------
#
def get_info(obj):
    # Return information about the watchdog timer
    return [
        ("Description", "ARM PrimeCell Watchdog Timer"),
        ("Timer Enabled", str(obj.timer_enabled)),
        ("Lock Status", "Unlocked" if not obj.lock_status else "Locked"),
        ("Countdown Value", str(obj.countdown_value))
    ]

cli.new_info_command(class_name, get_info)

#
# ------------------------ status -----------------------
#
def get_status(obj):
    # Return status information about the watchdog timer
    return [
        ("Configuration", [
            ("Control Register", hex(obj.regs_wdogcontrol.val)),
            ("Load Register", hex(obj.regs_wdogload.val)),
            ("Lock Register", hex(obj.regs_wdoglock.val))
        ]),
        ("Status", [
            ("Interrupt Status", "Pending" if obj.interrupt_status else "Clear"),
            ("Reset Status", "Pending" if obj.reset_status else "Clear"),
            ("Timer Enabled", "Yes" if obj.timer_enabled else "No")
        ])
    ]

cli.new_status_command(class_name, get_status)