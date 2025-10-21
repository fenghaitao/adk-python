# Interface Behavior Contracts

## Clock Interface (wclk)

### Signal Behavior
- The working clock drives the timer countdown
- Each rising edge of wclk decrements the timer counter by 1
- When wclk_en is low, the clock is gated and timer stops
- When wclk_en is high, the clock is active and timer runs

### Timing Requirements
- Clock frequency: Variable, defined by system design
- Setup and hold times: As specified in the hardware documentation
- Clock domain: wclk working clock domain

## Clock Enable Interface (wclk_en)

### Signal Raise Behavior
- When signal is raised (1), enables the working clock
- Timer operation resumes if enabled
- No immediate effect on timer counter value

### Signal Lower Behavior
- When signal is lowered (0), disables the working clock
- Timer operation pauses
- No effect on interrupt or reset outputs

## Reset Input Interface (wrst_n)

### Signal Lower Behavior (Active Low)
- When signal is lowered (0), resets the watchdog timer
- All registers reset to their default values
- Timer counter resets to load value
- Interrupt and reset outputs are deasserted
- Lock status resets to locked (1)

### Signal Raise Behavior
- When signal is raised (1), normal operation resumes
- Timer starts counting from the load value
- Register values are restored to reset defaults

## Interrupt Output Interface (wdogint)

### Signal Raise Behavior
- Asserted when timer reaches zero and interrupt is enabled
- Output remains asserted until cleared by writing to WDOGINTCLR
- Signal is in wclk working clock domain
- Follows the interrupt enable and mask settings

### Signal Lower Behavior
- Deasserted when interrupt is cleared by writing to WDOGINTCLR
- Deasserted when reset signal is asserted
- Deasserted during device reset

## Reset Output Interface (wdogres)

### Signal Raise Behavior
- Asserted when timer reaches zero again after interrupt was not cleared
- Output remains asserted until system reset occurs
- Only asserted if reset enable bit is set
- Signal is in wclk working clock domain

### Signal Lower Behavior
- Deasserted only when system reset occurs
- Not deasserted by writing to any register
- Requires external system reset to clear