# OpenSpec Prompts

This directory contains prompts for creating OpenSpec specifications and change proposals for the ADK Python + OpenSpec integration project.

## Available Prompts

### Hardware Development (Watchdog Timer)
- `propose-wdt-register-interface.md` - Create register interface specification
- `propose-wdt-timer-behavior.md` - Create timer behavior specification  
- `propose-wdt-platform-integration.md` - Create platform integration specification

### Generic Development
- `1.md` - DML device implementation guidance
- `2.md` - Building and compilation guidance
- `3.md` - Testing and verification guidance
- `compile.md` - Compilation process guidance
- `implement.md` - Implementation guidance
- `verify.md` - Verification and testing guidance

## Usage

1. Choose the appropriate prompt for your development phase
2. Use the prompt with your OpenSpec-enabled ADK agent
3. The agent will create proper OpenSpec change proposals following conventions
4. Review and iterate on the generated specifications
5. Follow the OpenSpec workflow to implement and archive changes

## Prompt Structure

Each OpenSpec proposal prompt includes:
- **Context**: Current project state and existing specifications
- **Leverage**: What to extract from existing comprehensive specs
- **Proposed Change**: Specific requirements for the new specification
- **Instructions**: Follow OpenSpec conventions (proposal.md, tasks.md, spec delta)

## Integration with Spec-Kit

These prompts are designed to work with existing spec-kit generated specifications at:
`/home/hfeng1/demo/adk_openspec_project/specs/001-home-hfeng1-demo/spec.md`

They extract focused aspects from the comprehensive specification into modular OpenSpec changes.