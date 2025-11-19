# DEMO_WATCHDOG Device Module

This module was generated from an IP-XACT specification using the DDM (Data-Driven Modeling) library template generator.

## Overview

The `demo_watchdog` module demonstrates how to:
1. Parse IP-XACT XML files containing register specifications
2. Generate DDM data models from the parsed specifications
3. Create Simics device models with the DDM library
4. Use glue configuration to map IP-XACT structures to DML code

## Files

- **demo_watchdog.xml** - IP-XACT register specification
- **parse_ipxact.py** - Parser to extract register information from IP-XACT XML
- **model_spec.py** - DDM data model specification (banks, registers, fields)
- **demo_watchdog-dia.dml** - Device Interface Abstract (DIA) definitions
- **demo_watchdog.dml** - Main device model implementation (with TODO placeholders)
- **Makefile** - Build configuration for the module
- **MODULEINFO** - Module metadata
- **MODULEDEPS** - Module dependencies

## Building

To build the module:

```bash
cd simics-project
make demo_watchdog
```

The build process will:
1. Parse `demo_watchdog.xml` using `parse_ipxact.py`
2. Generate data model DML from `model_spec.py`
3. Generate glue DML code automatically
4. Compile the complete device model

## Generated Files

During build, the following files are generated:
- **demo_watchdog-data-model.dml** - DDM data structures
- **demo_watchdog-glue.dml** - Glue code connecting IP-XACT to DDM
- **glue_config_generated.yaml** - Generated glue configuration

## Usage

Once built, you can create an instance of the device in Simics:

```simics
create demo_watchdog name = my_device
```

## Implementation

The main device file `demo_watchdog.dml` contains TODO comments indicating where you should implement:

1. **Device state variables** - Add session variables for your device's internal state
2. **Initialization logic** - Set up initial register values and state in the `init()` method
3. **Register side effects** - Implement write_register() and read_register() methods for each register that needs special behavior
4. **Custom methods** - Add any device-specific functionality

### Example Register Implementation

```dml
register MY_CONTROL {
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        default(value, enabled_bytes, aux);

        // Check if enable bit is set
        if (this.val & 0x1) {
            // Enable functionality
            start_operation();
        } else {
            // Disable functionality
            stop_operation();
        }
    }
}
```

## Dependencies

This module depends on:
- **ddm-lib** - Data-Driven Modeling library for Simics

## References

- IP-XACT Standard: http://www.accellera.org/downloads/standards/ip-xact
- DDM Library documentation in `modules/ddm-lib/`
- Simics DML 1.4 documentation
