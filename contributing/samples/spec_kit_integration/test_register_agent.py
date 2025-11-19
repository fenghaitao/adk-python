#!/usr/bin/env python3
"""
Test script for RegisterAgent - demonstrates register analysis capabilities.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from register_agent import register_agent


def test_basic_usage():
    """Test basic RegisterAgent usage."""
    print("=" * 80)
    print("RegisterAgent Test - Basic Usage")
    print("=" * 80)

    # Example: Analyze a hypothetical watchdog timer specification
    prompt = """
I have a watchdog timer device with the following registers:

1. WDOGLOAD (0x000, RW, 32-bit): Load value for countdown timer
   - Reset value: 0xFFFFFFFF
   - Writing sets the value to load into counter

2. WDOGVALUE (0x004, RO, 32-bit): Current counter value
   - Reset value: 0xFFFFFFFF
   - Decrements each clock cycle when enabled

3. WDOGCONTROL (0x008, RW, 32-bit): Control register
   - Reset value: 0x00000000
   - Bit 0 (INTEN): Enable interrupt on timeout
   - Bit 1 (RESEN): Enable system reset on timeout

4. WDOGINTCLR (0x00C, WO, 32-bit): Interrupt clear
   - Write any value to clear interrupt

5. WDOGRIS (0x010, RO, 32-bit): Raw interrupt status
   - Bit 0: Set when counter reaches zero

6. WDOGMIS (0x014, RO, 32-bit): Masked interrupt status
   - Bit 0: WDOGRIS.bit0 AND WDOGCONTROL.INTEN

7. WDOGLOCK (0xC00, RW, 32-bit): Lock register
   - Write 0x1ACCE551 to unlock
   - Any other write locks
   - When locked, all registers except WDOGLOCK are read-only

Please analyze these registers and:
1. Identify the hardware functions they implement
2. Document all read/write side-effects
3. Explain register relationships and dependencies
4. Provide simulation implementation guidance

Focus on creating a clear, implementable guide for a Simics DML device model.
"""

    print("\nPrompt:")
    print("-" * 80)
    print(prompt)
    print("-" * 80)

    print("\nSending to RegisterAgent...")
    response = register_agent.send_message(prompt)

    print("\nResponse:")
    print("-" * 80)
    print(response)
    print("-" * 80)

    return response


def test_ipxact_analysis():
    """Test analyzing an IP-XACT specification (if available)."""
    print("\n" + "=" * 80)
    print("RegisterAgent Test - IP-XACT Analysis")
    print("=" * 80)

    # Check if we have example IP-XACT files
    example_paths = [
        "../../ipxact/simics-mcp-server/modules/wdt/wdt.xml",
        "../../../ipxact/simics-mcp-server/modules/wdt/wdt.xml",
        "/nfs/site/disks/ssm_lwang85_002/AI/workspace/ipxact/simics-mcp-server/modules/wdt/wdt.xml"
    ]

    ipxact_file = None
    for path in example_paths:
        if Path(path).exists():
            ipxact_file = path
            break

    if not ipxact_file:
        print("No IP-XACT example file found. Skipping this test.")
        return None

    prompt = f"""
Please analyze the IP-XACT register specification in the file:
{ipxact_file}

Provide:
1. Complete register map with all fields
2. Hardware function groupings
3. Detailed read/write side-effects for each register
4. Register interaction patterns
5. Simulation implementation guide with required state variables
6. Example implementation code patterns

Store the analysis in .specify/register-analysis.md
"""

    print("\nPrompt:")
    print("-" * 80)
    print(prompt)
    print("-" * 80)

    print("\nSending to RegisterAgent...")
    response = register_agent.send_message(prompt)

    print("\nResponse:")
    print("-" * 80)
    print(response)
    print("-" * 80)

    return response


def test_compare_devices():
    """Test comparing register patterns across devices."""
    print("\n" + "=" * 80)
    print("RegisterAgent Test - Device Comparison")
    print("=" * 80)

    prompt = """
Compare the register organization patterns between two common peripheral types:

1. Watchdog Timer (WDT):
   - Load register (set countdown value)
   - Value register (current countdown)
   - Control register (enable/disable, interrupt/reset mode)
   - Interrupt clear register
   - Status registers (raw and masked)
   - Lock register (write protection)

2. General Purpose Timer (GPT):
   - Load register (set initial value)
   - Counter register (current value)
   - Control register (enable, mode, prescaler)
   - Interrupt enable register
   - Interrupt status register
   - Compare registers (for match interrupts)

Identify:
- Common patterns between these device types
- Differences in register organization
- Side-effect similarities and differences
- Best practices for implementing each type in a simulator
"""

    print("\nPrompt:")
    print("-" * 80)
    print(prompt)
    print("-" * 80)

    print("\nSending to RegisterAgent...")
    response = register_agent.send_message(prompt)

    print("\nResponse:")
    print("-" * 80)
    print(response)
    print("-" * 80)

    return response


def test_side_effect_patterns():
    """Test identifying common side-effect patterns."""
    print("\n" + "=" * 80)
    print("RegisterAgent Test - Side-Effect Pattern Recognition")
    print("=" * 80)

    prompt = """
Explain and provide implementation examples for these common register side-effect patterns:

1. Write-One-to-Clear (W1C):
   - What it means
   - When to use it
   - Implementation pattern
   - Example: Interrupt status register

2. Write-One-to-Set (W1S):
   - What it means
   - When to use it
   - Implementation pattern
   - Example: Interrupt enable register

3. Read-to-Clear:
   - What it means
   - When to use it
   - Implementation pattern
   - Example: FIFO status register

4. Lock-Unlock Sequence:
   - What it means
   - When to use it
   - Implementation pattern
   - Example: Configuration protection

5. Auto-Reload:
   - What it means
   - When to use it
   - Implementation pattern
   - Example: Periodic timer

For each pattern, provide:
- Hardware behavior description
- Typical use cases
- DML implementation code example
- Simulation state variables needed
"""

    print("\nPrompt:")
    print("-" * 80)
    print(prompt)
    print("-" * 80)

    print("\nSending to RegisterAgent...")
    response = register_agent.send_message(prompt)

    print("\nResponse:")
    print("-" * 80)
    print(response)
    print("-" * 80)

    return response


def main():
    """Run all tests."""
    print("\n")
    print("*" * 80)
    print("RegisterAgent Test Suite")
    print("*" * 80)

    try:
        # Test 1: Basic usage with inline specification
        test_basic_usage()

        # Test 2: IP-XACT analysis (if file available)
        test_ipxact_analysis()

        # Test 3: Device comparison
        test_compare_devices()

        # Test 4: Side-effect patterns
        test_side_effect_patterns()

        print("\n" + "*" * 80)
        print("All tests completed!")
        print("*" * 80)

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
