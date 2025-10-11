# Steps of using adk-python + spec-kit + PageIndexCopilot for Simics modeling work

## Code checkout

- git submodule init
- git submodule update

## Installation

- recommend to use python 3.12 and bash

- install python dependency for all the modules:
    - cd [module_path]
    - uv venv, or python -m venv .venv
    - source .venv/bin/activate
    - (uv) pip install -e ., or (uv) pip install -r ./requirements.txt
    - deactivate

- modules include:
    - adk-python
    - contributing/samples/spec_kit_integration/simics-mcp-server
    - spec-kit
    - PageIndexCopilot

- the `simics-mcp-server` module needs to install ispm tools:
    - refer to `adk-python/contributing/samples/spec_kit_integration/simics-mcp-server/README.md`

## Run

- config the environment:
    - export ADK_ROOT=`pwd`
    - export PAGEINDEX_RAG_MODEL=github_copilot/gpt-5-mini
    - export TMPDIR=./tmp

- config the model for adk agents if needed, by default it will use iflow/Qwen3-Coder:
    - export SPEC_KIT_MODEL=github_copilot/gpt-5-mini

- use the venv to run the adk command:
    - cd [test_folder]
    - source $ADK_ROOT/.venv/bin/activate
    - $ADK_ROOT/run_spec_kit_phased.sh [project_name] "/specify <task string>"

- Note: [test_folder] could be an empty folder dedicate for placing your test examples, it will create a folder named [project_name] under [test_folder] and put all the outputs into that folder.

- An example for testing wdt modeling:
    - cd ~/wp/tests
    - ~/wp/adk-python/run_spec_kit_phased.sh wdt_run0  "/specify Build a Simics watchdog device model in DML code from this spec, ~/wp/specs/wdt.md, implement the model and its python tests as the spec, run the tests for the modeled device to make sure it is matching the spec requirements" 2>&1 |tee wdt_run0.log
