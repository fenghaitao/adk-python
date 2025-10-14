# Message History Management & Token Limit Fixes

## Quick Fix for Token Limit Errors

### The Error You're Seeing

```
Prompt exceed max tokens error!: model max tokens is 262144,
request length is 262656, max_new_tokens is -512
```

### Immediate Solutions (tcsh)

#### Option 1: Token-Based Truncation (RECOMMENDED)

```tcsh
# Clear existing long sessions
rm -rf .adk/sessions/*

# Adjust token-based limits (choose based on your model)
setenv ADK_CONTEXT_WINDOW_TOKENS 128000    # For 128k context models
setenv ADK_CONTEXT_THRESHOLD 0.75          # Trigger truncation at 75%

# Run your agent
adk run contributing/samples/spec_kit_integration
```

#### Option 2: Message-Count Truncation

```tcsh
# Keep last 30 messages (fallback method)
setenv ADK_MAX_HISTORY_MESSAGES 30

# Run your agent
adk run contributing/samples/spec_kit_integration
```

#### Option 3: Clear Session History

```tcsh
# Delete existing sessions
rm -rf .adk/sessions/*

# Run your agent
adk run contributing/samples/spec_kit_integration
```

#### Option 4: Use Model with Larger Context

```tcsh
# Switch to a model with larger context (if available)
setenv SPEC_KIT_MODEL "gpt-4-turbo"

# Run your agent
adk run contributing/samples/spec_kit_integration
```

### For Qwen3-Coder (262k tokens)

```tcsh
# Clear existing long session
rm -rf .adk/sessions/*

# Enable token-based truncation
setenv ADK_CONTEXT_WINDOW_TOKENS 256000
setenv ADK_CONTEXT_THRESHOLD 0.8

# Or use message-count fallback
setenv ADK_MAX_HISTORY_MESSAGES 40

# Run again
adk run contributing/samples/spec_kit_integration
```

---

## Overview

The ADK Runner includes **intelligent, token-aware message history truncation** to prevent exceeding model token limits during long conversations. Unlike simple message-count truncation, this system:

- **Monitors actual token usage** (estimated from content size)
- **Triggers truncation at 80% of context window** by default
- **Removes oldest messages** until reaching a comfortable 60% usage
- **Adds conversation summaries** for removed context

## How It Works

### Token-Based Truncation (Primary)

The system estimates token usage for your entire conversation history and triggers truncation when:
- **Estimated tokens exceed 80% of the model's context window**
- This prevents token limit errors before they occur
- Much smarter than counting messages alone

### Message-Count Fallback (Secondary)

Also maintains a message count limit for additional safety:
- Triggers if message count exceeds `ADK_MAX_HISTORY_MESSAGES`
- Useful for very short messages where token estimation might be less accurate

## Configuration

### Environment Variables

#### `ADK_CONTEXT_WINDOW_TOKENS`
- **Default**: `200000` (200k tokens - suitable for most modern models)
- **Description**: The model's maximum context window size in tokens
- **Example**: `setenv ADK_CONTEXT_WINDOW_TOKENS 128000` (for 128k context models)

#### `ADK_CONTEXT_THRESHOLD`
- **Default**: `0.8` (80% of context window)
- **Description**: Percentage of context window to trigger truncation (0.0-1.0)
- **Example**: `setenv ADK_CONTEXT_THRESHOLD 0.75` (trigger at 75%)

#### `ADK_MAX_HISTORY_MESSAGES`
- **Default**: `50`
- **Description**: Fallback maximum number of messages (secondary check)
- **Example**: `setenv ADK_MAX_HISTORY_MESSAGES 30`

#### `ADK_ENABLE_HISTORY_SUMMARIZATION`
- **Default**: `true`
- **Description**: Whether to add a summary of removed messages
- **Values**: `true` or `false`
- **Example**: `setenv ADK_ENABLE_HISTORY_SUMMARIZATION false`

## Model-Specific Settings

### GPT-4 Turbo (128k context)
```tcsh
setenv ADK_CONTEXT_WINDOW_TOKENS 128000
setenv ADK_CONTEXT_THRESHOLD 0.8
setenv ADK_MAX_HISTORY_MESSAGES 40
```

### Claude 3 Opus/Sonnet (200k context)
```tcsh
setenv ADK_CONTEXT_WINDOW_TOKENS 200000
setenv ADK_CONTEXT_THRESHOLD 0.8
setenv ADK_MAX_HISTORY_MESSAGES 50
```

### Gemini 1.5 Pro (1M context)
```tcsh
setenv ADK_CONTEXT_WINDOW_TOKENS 1000000
setenv ADK_CONTEXT_THRESHOLD 0.85
setenv ADK_MAX_HISTORY_MESSAGES 100
```

### Qwen3-Coder (256k context)
```tcsh
setenv ADK_CONTEXT_WINDOW_TOKENS 256000
setenv ADK_CONTEXT_THRESHOLD 0.8
setenv ADK_MAX_HISTORY_MESSAGES 50
```

### GPT-3.5 Turbo (16k context)
```tcsh
setenv ADK_CONTEXT_WINDOW_TOKENS 16000
setenv ADK_CONTEXT_THRESHOLD 0.75
setenv ADK_MAX_HISTORY_MESSAGES 20
```

## Configuration Presets

### Aggressive Truncation (for small context models)
```tcsh
setenv ADK_CONTEXT_WINDOW_TOKENS 16000
setenv ADK_CONTEXT_THRESHOLD 0.7
setenv ADK_MAX_HISTORY_MESSAGES 20
setenv ADK_ENABLE_HISTORY_SUMMARIZATION true
```

### Balanced (default, recommended)
```tcsh
setenv ADK_CONTEXT_WINDOW_TOKENS 200000
setenv ADK_CONTEXT_THRESHOLD 0.8
setenv ADK_MAX_HISTORY_MESSAGES 50
setenv ADK_ENABLE_HISTORY_SUMMARIZATION true
```

### Generous (for large context models)
```tcsh
setenv ADK_CONTEXT_WINDOW_TOKENS 1000000
setenv ADK_CONTEXT_THRESHOLD 0.85
setenv ADK_MAX_HISTORY_MESSAGES 100
setenv ADK_ENABLE_HISTORY_SUMMARIZATION true
```

### Disable Automatic Truncation (not recommended)
```tcsh
setenv ADK_MAX_HISTORY_MESSAGES 0
setenv ADK_CONTEXT_WINDOW_TOKENS 999999999
```

## Technical Details

### Token Estimation

The system uses a simple but effective character-based heuristic:
- **~4 characters per token** (industry standard approximation)
- Counts tokens in: user messages, assistant responses, function calls, function responses
- Handles all content types: text, function_calls, function_responses

### Truncation Algorithm

1. **Trigger Check**: After each invocation, calculates:
   ```python
   estimated_tokens = _estimate_session_tokens(session)
   token_limit = DEFAULT_CONTEXT_WINDOW * CONTEXT_THRESHOLD

   if estimated_tokens > token_limit:
       # Truncation needed
   ```

2. **Smart Removal**:
   - Iterates from **newest to oldest** messages
   - Keeps messages until reaching **60% of context window** (TARGET_PERCENTAGE)
   - Always preserves the very first message (system context)

3. **Summarization** (if enabled):
   - Counts removed: user messages, assistant responses, tool calls
   - Adds summary: `[Earlier conversation: X user messages, Y assistant responses, Z tool calls]`

4. **Logging**:
   ```
   Session exceeds limits - Estimated tokens: 165000/160000 (82.5%), Messages: 78
   Truncating session history: 78 → 42 messages
   After truncation - Estimated tokens: 118000 (59.0%)
   ```

### Why 80% Trigger → 60% Target?

- **80% Trigger**: Provides early warning, prevents hitting the hard limit
- **60% Target**: Leaves room for:
  - New user message (up to 10% = 20k tokens)
  - Agent response (up to 15% = 30k tokens)
  - Function calls/responses (up to 15% = 30k tokens)
- **Safety Buffer**: Prevents rapid re-truncation cycles

### When Truncation Occurs

- **Timing**: Before creating the invocation context
- **Scope**: Per session, not global
- **Persistence**: Truncated history is saved to the session service

### What Gets Kept

- Most recent messages (up to `MAX_HISTORY_MESSAGES` or 60% of token limit)
- Summary of removed messages (if enabled)
- All message metadata and structure
- Always the first message (system instructions)

### What Gets Removed

- Oldest messages beyond the limit
- Original content of removed messages (replaced by summary)

## Benefits

### 1. **Intelligent Token Management**
   - Monitors actual token usage (not just message count)
   - Triggers truncation at 80% to prevent hitting limits
   - Targets 60% after truncation to leave room for new exchanges

### 2. **Prevents Token Limit Errors**
   - Automatically manages conversation length before errors occur
   - Avoids `Prompt exceed max tokens error!`

### 3. **Maintains Context**
   - Keeps recent conversation intact
   - Summarizes older context for reference
   - Always preserves first message (system instructions)

### 4. **Transparent Operation**
   - Logs truncation events with token counts and percentages
   - Shows exactly what was removed

### 5. **Model-Agnostic**
   - Works with any LLM through configurable context window
   - Adapts to 128k, 200k, or even 1M+ context models

## Verify It's Working

You'll see log messages like:
```
Session exceeds limits - Estimated tokens: 165000/160000 (82.5%), Messages: 78
Truncating session history: 78 → 42 messages
After truncation - Estimated tokens: 118000 (59.0%)
Added conversation summary: [Earlier conversation: 17 user messages, 17 assistant responses, 8 tool calls]
```

## Troubleshooting

### Still Getting Token Limit Errors?

If you still encounter token limit errors after enabling truncation:

1. **Verify your model's actual context window**:
   ```tcsh
   # Example: If using a 128k model but set to 200k
   setenv ADK_CONTEXT_WINDOW_TOKENS 128000
   ```

2. **Lower the trigger threshold**:
   ```tcsh
   # Trigger earlier at 70% instead of 80%
   setenv ADK_CONTEXT_THRESHOLD 0.70
   ```

3. **Reduce message count limit**:
   ```tcsh
   setenv ADK_MAX_HISTORY_MESSAGES 30
   ```

4. **Clear existing sessions** (they may have old long history):
   ```tcsh
   rm -rf .adk/sessions/*
   ```

5. **Check system prompts**: Agent instructions in your agent config may be too long

### Want More History?

If your model has a large context window and you want more history:

```tcsh
# For models with 1M+ context (like Gemini 1.5 Pro)
setenv ADK_CONTEXT_WINDOW_TOKENS 1000000
setenv ADK_CONTEXT_THRESHOLD 0.85
setenv ADK_MAX_HISTORY_MESSAGES 200
```

### Token Estimation Too Conservative?

If you find the character-based estimation too conservative:

- The system uses **4 chars/token** as a safe approximation
- This is intentionally conservative to prevent errors
- Real tokenization varies by model, but this works universally
- If needed, adjust `CONTEXT_THRESHOLD` down (e.g., 0.75) to keep more history

### Logs Showing Frequent Truncation?

If you see truncation happening very frequently:

1. **Increase context window setting** (if your model supports it):
   ```tcsh
   setenv ADK_CONTEXT_WINDOW_TOKENS 300000
   ```

2. **Increase threshold** (trigger later):
   ```tcsh
   setenv ADK_CONTEXT_THRESHOLD 0.85
   ```

3. **Check for extremely long function responses** - consider if they can be shortened

## Best Practices

1. **Set ADK_CONTEXT_WINDOW_TOKENS to match your model**:
   - GPT-4 Turbo: 128,000
   - Claude 3: 200,000
   - Gemini 1.5 Pro: 1,000,000
   - Qwen3-Coder: 256,000
   - Check your model's documentation for accurate values

2. **Use 0.8 threshold as starting point**:
   - Provides good balance between context retention and safety
   - Adjust based on your usage patterns

3. **Clear sessions when changing models**:
   ```tcsh
   rm -rf .adk/sessions/*
   ```
   - Prevents old long sessions from causing issues with smaller-context models

4. **Monitor truncation logs**:
   - Watch for patterns in token usage
   - Adjust settings if truncation happens too frequently or not enough

5. **Keep summarization enabled**:
   - `ADK_ENABLE_HISTORY_SUMMARIZATION=true` (default)
   - Provides valuable context about what was removed

6. **For production deployments**:
   - Set conservative values to prevent errors
   - Example: `CONTEXT_THRESHOLD=0.75` instead of 0.85
   - Better to truncate slightly early than risk hitting limits

7. **Test with your workload**:
   - Different agents produce different message sizes
   - Tune settings based on your specific use case

## Implementation Details

### Code Location

The token-aware truncation is implemented in `src/google/adk/runners.py`:

- `_estimate_token_count()`: Character-based token estimation
- `_estimate_session_tokens()`: Counts tokens across all session events
- `_truncate_session_history()`: Smart truncation with 60% target
- `run_async()` and `run_live()`: Apply truncation before model calls

### Token Counting

The system counts tokens from:
- **Text content**: All text in user/assistant messages
- **Function calls**: Tool invocation parameters
- **Function responses**: Tool execution results
- **System messages**: Agent instructions and context

### Summarization Format

Example summary added when truncation occurs:

```
[Earlier conversation: 15 user messages, 15 assistant responses, 8 tool calls]
```

This helps maintain awareness of the conversation's history without using many tokens.

## Environment Variable Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `ADK_CONTEXT_WINDOW_TOKENS` | `200000` | Model's maximum context window in tokens |
| `ADK_CONTEXT_THRESHOLD` | `0.8` | Percentage (0.0-1.0) to trigger truncation |
| `ADK_MAX_HISTORY_MESSAGES` | `50` | Fallback message count limit (secondary check) |
| `ADK_ENABLE_HISTORY_SUMMARIZATION` | `true` | Whether to add summary of removed messages |

## Quick Reference Commands (tcsh)

```tcsh
# View current settings
printenv | grep ADK_

# Set for current session
setenv ADK_CONTEXT_WINDOW_TOKENS 128000
setenv ADK_CONTEXT_THRESHOLD 0.75
setenv ADK_MAX_HISTORY_MESSAGES 40

# Set permanently (add to ~/.tcshrc)
echo "setenv ADK_CONTEXT_WINDOW_TOKENS 128000" >> ~/.tcshrc
echo "setenv ADK_CONTEXT_THRESHOLD 0.75" >> ~/.tcshrc
echo "setenv ADK_MAX_HISTORY_MESSAGES 40" >> ~/.tcshrc

# Clear all ADK settings
unsetenv ADK_CONTEXT_WINDOW_TOKENS
unsetenv ADK_CONTEXT_THRESHOLD
unsetenv ADK_MAX_HISTORY_MESSAGES
unsetenv ADK_ENABLE_HISTORY_SUMMARIZATION

# Fresh start (clear sessions)
rm -rf .adk/sessions/*
```

## See Also

- [ADK Configuration Guide](./docs/CONFIGURATION.md)
- [Session Management](./docs/SESSIONS.md)
- [Performance Optimization](./docs/PERFORMANCE.md)
- Implementation: `src/google/adk/runners.py`
