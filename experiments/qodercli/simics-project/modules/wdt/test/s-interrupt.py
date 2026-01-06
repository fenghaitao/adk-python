import dev_util
import simics
import conf
import stest
import wdt_common

def test_interrupt_generation():
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    regs.WDOGLOCK.write(0x1ACCE551)
    
    load_value = 100
    regs.WDOGLOAD.write(load_value)
    
    regs.WDOGCONTROL.write(0x1)
    
    initial_raised = pic_int.raised
    stest.expect_equal(initial_raised, 0, "Interrupt should not be raised initially")
    
    simics.SIM_continue(150)
    
    ris_status = regs.WDOGRIS.read()
    stest.expect_equal(ris_status & 0x1, 1, "RIS should be set after timeout")
    
    mis_status = regs.WDOGMIS.read()
    stest.expect_equal(mis_status & 0x1, 1, "MIS should be set (RIS AND INTEN)")
    
    after_timeout_raised = pic_int.raised
    stest.expect_equal(after_timeout_raised, 1, "Interrupt should be raised after timeout")
    
    print("Interrupt generation test passed!")

def test_interrupt_clearing():
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    regs.WDOGLOCK.write(0x1ACCE551)
    
    load_value = 100
    regs.WDOGLOAD.write(load_value)
    
    regs.WDOGCONTROL.write(0x1)
    
    simics.SIM_continue(150)
    
    ris_before_clear = regs.WDOGRIS.read()
    stest.expect_equal(ris_before_clear & 0x1, 1, "RIS should be set before clear")
    
    raised_before_clear = pic_int.raised
    stest.expect_equal(raised_before_clear, 1, "Interrupt should be raised before clear")
    
    regs.WDOGINTCLR.write(0x1)
    
    ris_after_clear = regs.WDOGRIS.read()
    stest.expect_equal(ris_after_clear & 0x1, 0, "RIS should be cleared after writing INTCLR")
    
    mis_after_clear = regs.WDOGMIS.read()
    stest.expect_equal(mis_after_clear & 0x1, 0, "MIS should be cleared after writing INTCLR")
    
    raised_after_clear = pic_int.raised
    stest.expect_equal(raised_after_clear, 0, "Interrupt should be lowered after clear")
    
    value_after_clear = regs.WDOGVALUE.read()
    stest.expect_equal(value_after_clear, load_value, "Counter should reload from LOAD after INTCLR")
    
    print("Interrupt clearing test passed!")

def test_interrupt_persistence():
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    regs.WDOGLOCK.write(0x1ACCE551)
    
    load_value = 100
    regs.WDOGLOAD.write(load_value)
    
    regs.WDOGCONTROL.write(0x1)
    
    simics.SIM_continue(150)
    
    raised_after_first_timeout = pic_int.raised
    stest.expect_equal(raised_after_first_timeout, 1, "Interrupt should be raised after first timeout")
    
    simics.SIM_continue(500)
    
    raised_after_delay = pic_int.raised
    stest.expect_equal(raised_after_delay, 1, "Interrupt should remain raised without clear")
    
    ris_status = regs.WDOGRIS.read()
    stest.expect_equal(ris_status & 0x1, 1, "RIS should remain set without clear")
    
    print("Interrupt persistence test passed!")

if __name__ == "__main__":
    test_interrupt_generation()
    test_interrupt_clearing()
    test_interrupt_persistence()
