# IP-XACT Example Device Module

This module demonstrates how to create a Simics device model from an IP-XACT (SPIRIT) register specification using the DDM (Data-Driven Modeling) library.

## Overview

The `ipxact-example` module shows how to:
1. Parse IP-XACT XML files containing register specifications
2. Generate DDM data models from the parsed specifications
3. Create Simics device models with the DDM library
4. Use glue configuration to map IP-XACT structures to DML code

## Files

- **generic_example.xml** - Sample IP-XACT register specification (SPIRIT 1.5 format)
- **parse_ipxact.py** - Parser to extract register information from IP-XACT XML
- **model_spec.py** - DDM data model specification (banks, registers, fields)
- **gen_ddm.py** - Generator script that creates DML glue code from IP-XACT
- **glue_config.yaml** - Configuration mapping IP-XACT entities to DML hierarchies
- **ipxact-example-dia.dml** - Device Interface Abstract (DIA) definitions
- **ipxact-example.dml** - Main device model implementation
- **Makefile** - Build configuration for the module

## Building

To build the module:

```bash
cd simics-project
make ipxact-example
```

The build process will:
1. Parse `generic_example.xml` using `parse_ipxact.py`
2. Generate data model DML from `model_spec.py`
3. Generate glue DML code using `gen_ddm.py` and `glue_config.yaml`
4. Compile the complete device model

## Generated Files

During build, the following files are generated:
- **ipxact-example-data-model.dml** - DDM data structures
- **ipxact-example-glue.dml** - Glue code connecting IP-XACT to DDM

## Usage

Once built, you can create an instance of the device in Simics:

```simics
create ipxact_example name = my_device
```

## IP-XACT Structure

The parser handles the following IP-XACT elements:
- Memory maps and address blocks
- Registers with offset, size, reset values
- Fields with bit offset and width
- Access properties (read-write, read-only)
- Descriptions and documentation

## Extending

To use with your own IP-XACT file:
1. Replace `generic_example.xml` with your IP-XACT file
2. Update `glue_config.yaml` to match your register names
3. Optionally modify `parse_ipxact.py` for custom parsing logic
4. Rebuild the module

## Dependencies

This module depends on:
- **ddm-lib** - Data-Driven Modeling library for Simics

## References

- IP-XACT Standard: http://www.accellera.org/downloads/standards/ip-xact
- DDM Library documentation in `modules/ddm-lib/`
- Simics DML 1.4 documentation
