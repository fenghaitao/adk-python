# DML Build Error Fixing Task

## CRITICAL RULES
- You are a SYNTAX FIXER ONLY - preserve existing code and logic
- DO NOT remove methods, TODOs, registers, or implementation details
- Fix BUILD ERRORS only - don't rewrite code
- Use LOOP: fix one error type → build → commit → check for more errors → repeat
- **ABSOLUTE RULE**: NEVER remove import statements to "fix" errors - imports are required

## FORBIDDEN ACTIONS
❌ Removing ANY import statements (even if they appear in error messages)
❌ Removing any existing code/methods/registers
❌ Creating new .dml files to "work around" errors
❌ Changing logic or implementation
❌ Modifying config/XML/Makefiles/other files
❌ Modifying ANY file except: `simics-project/modules/<device_name>/<device_name>.dml`
❌ Editing auto-generated files: `<device_name>-glue.dml`, `<device_name>-dia.dml` (these are auto-generated!)

## MANDATORY STEPS
1. Find device name: `ls simics-project/modules/`
2. Build project: `cd simics-project && gmake <device_name> 2>&1 | tee bld.log`
3. Read build log with `read_file` tool - look for errors
4. If errors exist:
   - Fix syntax errors in `<device_name>.dml` ONLY
   - Add missing method implementations
   - Fix type mismatches
   - **NEVER remove imports** - if import-related errors occur, fix the referenced files or work around them
   - Research with mcp RAG tool for correct DML 1.4 syntax
5. ONLY edit: `simics-project/modules/<device_name>/<device_name>.dml`
6. Build again to validate
7. Commit: `git add simics-project/modules/<device_name>/<device_name>.dml simics-project/bld.log && git commit ...`
8. Loop back to #3 - keep fixing until 0 errors!

## IMPORTANT NOTES
- If `<device_name>-glue.dml` is missing, it will be auto-generated during build - do NOT create it
- If `<device_name>-dia.dml` has errors, do NOT remove its import - it's required for register definitions
- All imports MUST remain in the file even if they cause temporary build errors

## EXIT: When build log shows 0 errors!