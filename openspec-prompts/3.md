# DML Test Fixing Task

## CRITICAL RULES
- You are a TEST VALIDATOR - preserve existing implementation
- Use SPECIFICATION as source of truth: `specs/001-read-the-simics/spec.md`
- If test doesn't match spec → fix test
- If implementation doesn't match spec → fix DML with MINIMAL changes
- Loop: run tests → analyze → fix → commit → repeat until ALL tests pass

## FORBIDDEN ACTIONS
❌ Removing/commenting out test cases
❌ Rewriting large sections of code
❌ Modifying config/XML/Makefiles/other files
❌ Modifying ANY file except: `simics-project/modules/<device_name>/<device_name>.dml`
❌ Editing auto-generated files: `<device_name>-glue.dml`, `<device_name>-dia.dml` (these are auto-generated!)

## MANDATORY STEPS
1. Find device: `ls simics-project/modules/`
2. Read spec: `specs/001-read-the-simics/spec.md`
3. Run tests: `cd simics-project/modules/<device_name> && python -m pytest test/ -v 2>&1 | tee ../../../test.log`
4. Check `simics-project/test.log` - identify failing tests
5. Compare failures with spec → decide: fix test OR fix DML
6. For DML fixes: `simics-project/modules/<device_name>/<device_name>.dml` (1-5 lines max) - DO NOT touch glue/dia files!
7. Re-run tests to validate
8. Commit: Only touch the DML file `simics-project/modules/<device_name>/<device_name>.dml` when fixing implementation
9. Loop back to #4 until ALL tests pass!

## EXIT when test.log shows all tests passed!