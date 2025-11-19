#!/usr/bin/env python3
"""
Simple example demonstrating RegisterAgent JSON output format.

This example shows how RegisterAgent analyzes register specifications
and produces JSON output with read/write side-effects.
"""

import json

# Example: Expected JSON output from RegisterAgent for a simple timer device

example_json_output = {
    "TIMER_LOAD": {
        "read": "Returns the current load register value. No side-effects - reading does not modify hardware state.",
        "write": "Stores the written value to the load register AND immediately copies it to the counter register (TIMER_COUNT), restarting the countdown from the new value. If the timer is enabled (TIMER_CTRL.EN=1), the countdown begins immediately."
    },
    "TIMER_COUNT": {
        "read": "Returns the current counter value, which decrements each clock cycle when the timer is enabled. No side-effects - this is a read-only status register.",
        "write": "Not writable - this is a read-only register. Writes are ignored. The value is automatically updated by hardware as the timer counts down and when TIMER_LOAD is written."
    },
    "TIMER_CTRL": {
        "read": "Returns the control register with bit 0 = timer enable (EN), bit 1 = interrupt enable (IE). No side-effects.",
        "write": "Bit 0 (EN): Writing 1 starts the timer countdown, writing 0 stops it. Bit 1 (IE): Writing 1 enables interrupt generation when counter reaches 0, writing 0 disables interrupts. When EN transitions from 0 to 1, if the counter is non-zero, countdown begins immediately."
    },
    "TIMER_INTCLR": {
        "read": "Not readable - this is a write-only register. Reads return undefined values.",
        "write": "ANY write (value is ignored) clears the pending interrupt status in TIMER_STATUS and deasserts the interrupt signal to the interrupt controller. Does not affect the timer counter or enable state."
    },
    "TIMER_STATUS": {
        "read": "Returns the timer status with bit 0 = interrupt pending flag (set when counter reaches 0). No side-effects - reading does NOT clear the interrupt (use TIMER_INTCLR instead).",
        "write": "Not writable - this is a read-only status register. The interrupt flag is cleared only by writing to TIMER_INTCLR."
    }
}

def main():
    """Demonstrate the JSON output format."""

    print("=" * 80)
    print("RegisterAgent JSON Output Example")
    print("=" * 80)
    print()
    print("This is the expected JSON format for register side-effects analysis:")
    print()

    # Pretty-print the JSON
    json_str = json.dumps(example_json_output, indent=2)
    print(json_str)

    print()
    print("=" * 80)
    print("Key Points:")
    print("=" * 80)
    print()
    print("1. Each register has 'read' and 'write' fields")
    print("2. Read-only registers: write = 'Not writable - ...'")
    print("3. Write-only registers: read = 'Not readable - ...'")
    print("4. No side-effects: Explicitly stated as 'No side-effects'")
    print("5. Descriptions include:")
    print("   - What hardware state changes")
    print("   - Which signals are affected")
    print("   - Register interactions")
    print("   - Field-level behaviors")
    print()

    # Save example to file
    output_file = "example-register-side-effects.json"
    with open(output_file, 'w') as f:
        json.dump(example_json_output, f, indent=2)

    print(f"Example saved to: {output_file}")
    print()

    # Show how to use RegisterAgent
    print("=" * 80)
    print("Using RegisterAgent:")
    print("=" * 80)
    print()
    print("from register_agent import register_agent")
    print()
    print('response = register_agent.send_message("""')
    print('Analyze the IP-XACT specification in /path/to/timer.xml')
    print('and generate a JSON file with register side-effects.')
    print('Save the output to timer-side-effects.json')
    print('""")')
    print()
    print("The agent will:")
    print("  1. Read the IP-XACT XML file")
    print("  2. Analyze hardware functionality")
    print("  3. Document read/write side-effects")
    print("  4. Generate JSON in the format shown above")
    print("  5. Save to the specified file")
    print()

if __name__ == "__main__":
    main()
