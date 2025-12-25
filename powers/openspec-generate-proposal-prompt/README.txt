# OpenSpec Generate Proposal Prompt Power

A meta-power that analyzes specification files and generates prompts for the openspec-propose power.

## Purpose

Automates the creation of comprehensive task coverage prompts by:
1. Analyzing spec files to identify requirement categories
2. Grouping requirements semantically
3. Generating prompts for the openspec-propose power
4. Enabling systematic requirement extraction → task generation

## Quick Start

```bash
kiro-cli chat -a "Read powers/openspec-generate-proposal-prompt/POWER.md and generate prompts for specs/001-read-the-simics/spec.md"
```

## What It Does

Input: Specification file with requirements (FUNC-XXX, REG-XXX, etc.)
Output: Multiple prompt files (one per category) for openspec-propose
Capability: Semantic understanding and grouping of requirements

## Use Case

When you have a detailed spec and want to demonstrate OpenSpec's capability to generate comprehensive task coverage across all requirement categories.

## See POWER.md for complete documentation
