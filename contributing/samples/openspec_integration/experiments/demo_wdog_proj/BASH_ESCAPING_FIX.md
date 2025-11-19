# Bash Script Escaping Fix

## Error Found in test.log

```
test_first_task.sh: line 204: dml: command not found
test_first_task.sh: line 205: register: command not found
test_first_task.sh: command substitution: line 206: syntax error near unexpected token `('
test_first_task.sh: command substitution: line 206: `    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {'
```

## Root Cause

The TASK_PROMPT variable in the bash script contained triple backticks (```) for code fencing:

```bash
TASK_PROMPT="... 
```dml
register WDOGLOAD {
    method write_register(...) {
        ...
    }
}
```
..."
```

**Problem**: Bash interprets backticks (`) as command substitution, attempting to execute the text inside as shell commands.

## Solution

Replaced triple backtick code fences with simple indentation:

**Before (BROKEN)**:
```bash
TASK_PROMPT="...
```dml
register WDOGLOAD {
    method write_register(...) {
        ...
    }
}
```
..."
```

**After (FIXED)**:
```bash
TASK_PROMPT="...
Required DML code structure (follow existing register pattern in the file):

    register WDOGLOAD {
        method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
            log info, 1: \">>> WDOGLOAD write_register() CALLED with value=0x%x\", value;
            ...
        }
    }
..."
```

## Why This Works

1. **No backticks**: Indented code blocks don't use backticks, so bash doesn't try to execute them
2. **Still readable**: The LLM agent can still clearly see it's code due to indentation
3. **Markdown compatible**: Many markdown parsers recognize indented blocks as code
4. **Safe escaping**: Only need to escape quotes (\"), not worry about backticks

## Testing

Verified the fix with:
```bash
bash -c 'TASK_PROMPT="text with indented code"; echo "$TASK_PROMPT"'
```

Result: ✅ Works correctly, no command substitution errors

## Files Fixed

- ✅ `test_first_task.sh` - Removed backtick code fences, used indentation instead
- ✅ `run_openspec_from_ddm.py` - Already doesn't use backtick code fences (verified)

## Lesson Learned

When embedding code examples in bash string literals:
- ❌ Avoid: Triple backticks (\`\`\`) - bash interprets as command substitution
- ✅ Use: Indented blocks (4 spaces) - safe and LLM-readable
- ✅ Alternative: Escape backticks as \\\` (but harder to read)
- ✅ Alternative: Use heredoc syntax for multi-line strings

## Next Steps

The test_first_task.sh script should now run without syntax errors. The agent will receive a properly formatted prompt with readable DML code examples.
