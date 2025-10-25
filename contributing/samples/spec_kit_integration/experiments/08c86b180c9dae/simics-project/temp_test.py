import dev_util
import simics

dev = simics.SIM_create_object('watchdog_timer', 'test_dev')
control_reg = dev_util.Register_LE(dev.bank.regs, 0x0008, size=4)
print('Initial control register value:', hex(control_reg.read()))