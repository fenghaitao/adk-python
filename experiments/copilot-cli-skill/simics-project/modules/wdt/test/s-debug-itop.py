#!/usr/bin/env python3
"""Debug test for WDOGITOP signal control"""

import simics
import stest
import dev_util
import wdt_common

def test_debug():
    # Create device configuration
    devs = wdt_common.create_config()
    dev = devs[0]
    fake_pic_int = devs[1]
    fake_pic_res = devs[2]
    
    print(f"Device: {dev}")
    print(f"INT PIC: {fake_pic_int}, raised={fake_pic_int.raised}")
    print(f"RES PIC: {fake_pic_res}, raised={fake_pic_res.raised}")
    
    regs = dev_util.bank_regs(dev.bank.wdt_map)
    
    # Unlock and enter test mode
    regs.WDOGLOCK.write(0x1ACCE551)
    regs.WDOGITCR.write(0x1)
    
    print(f"\nAfter entering test mode:")
    print(f"INT raised={fake_pic_int.raised}, RES raised={fake_pic_res.raised}")
    
    # Try to raise INT signal
    print(f"\nWriting 0x1 to WDOGITOP (INT=1, RES=0)...")
    regs.WDOGITOP.write(0x1)
    print(f"INT raised={fake_pic_int.raised}, RES raised={fake_pic_res.raised}")
    
    # Try to raise RES signal
    print(f"\nWriting 0x2 to WDOGITOP (INT=0, RES=1)...")
    regs.WDOGITOP.write(0x2)
    print(f"INT raised={fake_pic_int.raised}, RES raised={fake_pic_res.raised}")
    
    # Try both
    print(f"\nWriting 0x3 to WDOGITOP (INT=1, RES=1)...")
    regs.WDOGITOP.write(0x3)
    print(f"INT raised={fake_pic_int.raised}, RES raised={fake_pic_res.raised}")

if __name__ == "__main__":
    test_debug()
