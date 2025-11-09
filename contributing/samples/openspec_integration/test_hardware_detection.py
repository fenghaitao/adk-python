#!/usr/bin/env python3
"""Test script for hardware detection function."""


def detect_hardware_project(text: str) -> bool:
  """Detect if the project involves hardware device modeling."""
  hardware_keywords = [
    # Hardware terms
    "processor", "cpu", "gpu", "fpga", "microcontroller", "embedded",
    # Simulation terms
    "simulation", "modeling", "hardware validation", "device model",
    # Architecture terms
    "x86", "arm", "risc-v", "mips", "sparc",
    # Hardware components
    "pci", "usb", "memory controller", "peripheral", "watchdog timer",
    "network controller", "storage device", "interrupt controller",
    # Development terms
    "firmware", "bios", "bootloader", "dml", "register map",
    "hardware interface", "device driver"
  ]

  text_lower = text.lower()
  return any(keyword in text_lower for keyword in hardware_keywords)


def test_hardware_detection():
  """Test the hardware detection function."""
  test_cases = [
    # Hardware projects (should return True)
    ("Create a watchdog timer device", True),
    ("Add ARM processor support", True),
    ("Implement DML register map", True),
    ("FPGA simulation model", True),
    ("Build embedded firmware", True),
    ("Design PCI device controller", True),
    ("Microcontroller peripheral driver", True),
    ("x86 CPU simulation", True),
    ("RISC-V processor model", True),
    ("Hardware validation framework", True),
    ("Device model for USB controller", True),
    ("BIOS bootloader implementation", True),
    
    # Software projects (should return False)
    ("Build user authentication", False),
    ("Add search feature", False),
    ("React component library", False),
    ("REST API endpoint", False),
    ("Database migration script", False),
    ("Web application frontend", False),
    ("Machine learning model training", False),
    ("Data processing pipeline", False),
  ]

  print("Testing hardware detection function:")
  print("=" * 70)
  
  passed = 0
  failed = 0
  
  for text, expected in test_cases:
    result = detect_hardware_project(text)
    status = "✓ PASS" if result == expected else "✗ FAIL"
    
    if result == expected:
      passed += 1
    else:
      failed += 1
    
    print(f'{status} | "{text}"')
    print(f'         | Result: {result}, Expected: {expected}')
    print()
  
  print("=" * 70)
  print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
  
  return failed == 0


if __name__ == "__main__":
  success = test_hardware_detection()
  exit(0 if success else 1)
