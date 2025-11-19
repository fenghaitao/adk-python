# Project Context

## Overview

Simics device modeling project for ARM SP805 Watchdog Timer. Implements register behavior and side effects for hardware simulation.

## Specifications

This project implements Watchdog Timer as defined in the hardware specification.

## Development Workflow

1. **Specification**: Hardware behavior is defined in `specs/` directory
2. **Changes**: Proposed changes are tracked in `changes/` directory  
3. **Implementation**: Code changes are implemented in the main project
4. **Testing**: Each change includes test cases to verify behavior

## AI Agent Instructions

When implementing changes:
- Read the hardware specification carefully
- Implement register behavior with proper side effects
- Create comprehensive test cases
- Compile and verify the implementation works

## Project Structure

- `modules/`: Device model implementation (DML files)
- `openspec/specs/`: Hardware specifications
- `openspec/changes/`: Change proposals and tasks
- `test/`: Test files for verification
