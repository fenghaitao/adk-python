# Memory File Optimization Guide

## Overview

This guide shows how to optimize individual memory/best practices files using DeepEval's PromptOptimizer. This is often **more effective** than optimizing the main instructions because:

- **Focused scope** - Each file covers one specific topic
- **Clear success metrics** - Track specific error patterns
- **Lower risk** - Won't break entire workflow
- **Faster iteration** - Optimize one file at a time
- **Measurable impact** - Track error rate reduction

## Quick Start (3 Steps)

### Step 1: Analyze Which Files Need Optimization

```bash
cd deepeval-scoring

# Collect historical sessions first (if not done already)
python collect_session_data.py \
  --workdir ~/projects/simics \
  --output historical_sessions.json \
  --min-score 0.3

# Analyze memory file effectiveness
python analyze_memory_effectiveness.py \
  --sessions historical_sessions.json \
  --output memory_stats.json
```

**Example Output:**
```
======================================================================
MEMORY FILE EFFECTIVENESS ANALYSIS
======================================================================

Files are sorted by effectiveness (least effective first)
These are the best candidates for optimization.

1. 02_DML_Anti_Patterns.md
   ──────────────────────────────────────────────────────────────────
   Success Rate: 45% (errors in 7/12 sessions)
   Average Score: 58%
   Times Read: 12

   Top Issues After Reading This File:
     • Cycle By Cycle Updates: 8 occurrence(s)
     • Sim Cycle Count In Init: 5 occurrence(s)
     • Incomplete Timer: 4 occurrence(s)

2. 07_DML_Register_Access_Scope.md
   ──────────────────────────────────────────────────────────────────
   Success Rate: 62% (errors in 6/15 sessions)
   Average Score: 68%
   Times Read: 15

   Top Issues After Reading This File:
     • Scope Error: 7 occurrence(s)
     • Undefined Method: 3 occurrence(s)

======================================================================
OPTIMIZATION RECOMMENDATIONS
======================================================================

🔴 HIGH PRIORITY (2 files):
   These files have <70% success rate and should be optimized first.

   • 02_DML_Anti_Patterns.md (45% success)
     Focus on: cycle_by_cycle_updates
   • 07_DML_Register_Access_Scope.md (62% success)
     Focus on: scope_error

💡 Next Steps:
   1. Run optimizer on high-priority files:
      python optimize_memory_file.py --memory-file <file> ...
   2. A/B test optimized versions
   3. Measure improvement in error rates
   4. Iterate on medium-priority files
```

### Step 2: Optimize High-Priority Files

```bash
# Optimize the anti-patterns file (lowest success rate)
python optimize_memory_file.py \
  --memory-file ../openspec-memories/02_DML_Anti_Patterns.md \
  --sessions historical_sessions.json \
  --output 02_DML_Anti_Patterns_optimized.md \
  --focus-errors cycle_by_cycle_updates,sim_cycle_count_in_init \
  --algorithm simba \
  --iterations 3
```

**Output:**
```
📂 Memory file: 02_DML_Anti_Patterns.md
📊 Sessions file: historical_sessions.json
🎯 Focus errors: cycle_by_cycle_updates, sim_cycle_count_in_init

📥 Loading historical sessions...
✅ Loaded 20 total sessions

🔍 Filtering sessions that used 02_DML_Anti_Patterns.md...
✅ Found 12 relevant sessions

======================================================================
STARTING OPTIMIZATION
======================================================================

🔧 Creating optimizer with simba algorithm...
🚀 Running optimization (3 iterations)...
📊 Using 12 relevant sessions
📈 Metrics: ['Code Correctness', 'Code Style']

Iteration 1/3: Analyzing patterns...
Iteration 2/3: Refining guidance...
Iteration 3/3: Final optimization...

======================================================================
OPTIMIZATION COMPLETE
======================================================================

📊 Summary:
   Original: 120 lines
   Optimized: 145 lines
   Change: +25 lines

💾 Optimized file saved to: 02_DML_Anti_Patterns_optimized.md

💡 Next Steps:
   1. Review optimized file: 02_DML_Anti_Patterns_optimized.md
   2. Compare with original: diff ../openspec-memories/02_DML_Anti_Patterns.md 02_DML_Anti_Patterns_optimized.md
   3. Test with new sessions
   4. Measure error rate reduction
```

### Step 3: A/B Test and Measure Improvement

```bash
# Backup original
cp ../openspec-memories/02_DML_Anti_Patterns.md \
   ../openspec-memories/02_DML_Anti_Patterns.md.backup

# Deploy optimized version
cp 02_DML_Anti_Patterns_optimized.md \
   ../openspec-memories/02_DML_Anti_Patterns.md

# Run 5 new test sessions
cd ..
for device in can lin flexray spi i2c; do
  ./openspec-scripts/run-openspec-apply.sh ~/projects/simics implement-$device standard
done

# Measure error rate
cd deepeval-scoring
python measure_error_rate.py \
  --sessions ~/projects/simics \
  --error-type cycle_by_cycle_updates \
  --before 8 \
  --after 2

# Output: Error rate reduced from 67% (8/12) to 40% (2/5) - 27% improvement!
```

## What Gets Optimized?

### Before Optimization

```markdown
# Anti-Pattern #1: Cycle-by-Cycle Updates

Don't use cycle-by-cycle updates. Use event-based timing instead.

Bad:
```dml
method update() {
    if (enabled) counter--;
}
```

Good:
```dml
method start_countdown() {
    after (delay) call timeout_event;
}
```
```

### After Optimization

```markdown
# Anti-Pattern #1: Cycle-by-Cycle Updates (⚠️ CRITICAL - READ THIS FIRST)

**MOST COMMON MISTAKE**: Using cycle-by-cycle updates causes 100-1000x performance degradation.

## ❌ NEVER DO THIS - Updating state in every cycle

```dml
method update() {  // ❌ WRONG - Called every cycle
    if (enabled) counter--;
}
```

**Why this is wrong:**
- Called millions of times per second
- Simics becomes unusably slow
- Violates Simics modeling philosophy (see `01_Simics_Modeling_Philosophy.md`)

## ✅ ALWAYS DO THIS - Event-based timing

```dml
method start_countdown() {
    // Schedule ONE event in the future
    after (delay_seconds) call timeout_event;
}

method timeout_event() {
    // This runs ONCE when timer expires
    counter = 0;
    raise_interrupt();
}
```

## 🔍 How to Recognize This Pattern

**Red flags that indicate you're about to make this mistake:**
- Thinking "I need to check something every cycle" → STOP
- Implementing a loop that runs continuously → STOP
- Using `SIM_cycle_count()` to track time → STOP
- Method name contains "update", "tick", "poll" → STOP

**What to do instead:**
1. Calculate WHEN the event should happen
2. Use `after` statement to schedule it
3. Let Simics call you when it's time

## 📋 Real Example from Session Logs

**What agent implemented (WRONG):**
```dml
method tick() {
    if (enabled) {
        count--;
        if (count == 0) raise_interrupt();
    }
}
```
**Result**: 1000x slowdown, tests timed out after 5 minutes

**What should have been implemented (CORRECT):**
```dml
method start() {
    after (period * count) call timeout;
}

method timeout() {
    raise_interrupt();
}
```
**Result**: Tests complete in 0.5 seconds

## 📚 See Also

- `04_DML_Timing_Timer_Modeling.md` - Complete timer examples
- `01_Simics_Modeling_Philosophy.md` - Why event-based modeling matters
- `06_DML_Common_Patterns.md` - More timing patterns
```

### Key Improvements

1. **Visual warnings** - ⚠️ symbols and colored markers
2. **Explicit bad/good markers** - ❌/✅ for clarity
3. **Why explanations** - Not just what, but why
4. **Recognition patterns** - Help agent identify the mistake before making it
5. **Real examples** - From actual session logs
6. **Cross-references** - Links to related files
7. **Quantified impact** - "1000x slowdown" is more concrete than "slow"

## Advanced Usage

### Optimize Multiple Files in Batch

```bash
# Get list of high-priority files
python analyze_memory_effectiveness.py \
  --sessions historical_sessions.json \
  | grep "HIGH PRIORITY" -A 10 \
  | grep "•" \
  | cut -d'•' -f2 \
  | cut -d'(' -f1 \
  > files_to_optimize.txt

# Optimize each file
while read file; do
  echo "Optimizing $file..."
  python optimize_memory_file.py \
    --memory-file "../openspec-memories/$file" \
    --sessions historical_sessions.json \
    --output "${file%.md}_optimized.md" \
    --algorithm simba \
    --iterations 3
done < files_to_optimize.txt
```

### Focus on Specific Error Types

```bash
# Optimize anti-patterns file focusing only on cycle-by-cycle errors
python optimize_memory_file.py \
  --memory-file ../openspec-memories/02_DML_Anti_Patterns.md \
  --sessions historical_sessions.json \
  --output 02_DML_Anti_Patterns_v2.md \
  --focus-errors cycle_by_cycle_updates \
  --iterations 5

# Optimize scope file focusing only on 'this' errors
python optimize_memory_file.py \
  --memory-file ../openspec-memories/07_DML_Register_Access_Scope.md \
  --sessions historical_sessions.json \
  --output 07_DML_Register_Access_Scope_v2.md \
  --focus-errors scope_error \
  --iterations 5
```

### Iterative Optimization

```bash
# Round 1: Initial optimization
python optimize_memory_file.py \
  --memory-file ../openspec-memories/02_DML_Anti_Patterns.md \
  --sessions historical_sessions_round1.json \
  --output 02_DML_Anti_Patterns_v1.md

# Deploy and collect more sessions
cp 02_DML_Anti_Patterns_v1.md ../openspec-memories/02_DML_Anti_Patterns.md
# ... run 10 more sessions ...

# Round 2: Refine based on new data
python collect_session_data.py --workdir ~/projects --output historical_sessions_round2.json
python optimize_memory_file.py \
  --memory-file 02_DML_Anti_Patterns_v1.md \
  --sessions historical_sessions_round2.json \
  --output 02_DML_Anti_Patterns_v2.md

# Compare improvement
# Round 1: 45% → 62% success rate (+17%)
# Round 2: 62% → 78% success rate (+16%)
```

## Measuring Success

### Track Error Rate Over Time

```bash
# Before optimization
python analyze_memory_effectiveness.py \
  --sessions historical_sessions_before.json \
  | grep "02_DML_Anti_Patterns.md" -A 5

# Output: Success Rate: 45% (errors in 7/12 sessions)

# After optimization
python analyze_memory_effectiveness.py \
  --sessions historical_sessions_after.json \
  | grep "02_DML_Anti_Patterns.md" -A 5

# Output: Success Rate: 78% (errors in 2/10 sessions)
# Improvement: +33% success rate, 71% error reduction
```

### Compare Specific Error Frequencies

```bash
# Count specific errors before/after
grep -r "cycle.*by.*cycle" ~/projects/simics/before/*.dml | wc -l
# Output: 8

grep -r "cycle.*by.*cycle" ~/projects/simics/after/*.dml | wc -l
# Output: 2

# 75% reduction in cycle-by-cycle errors!
```

## Best Practices

### 1. Start with High-Impact Files

Focus on files with:
- **Low success rate** (<70%)
- **High read frequency** (>10 sessions)
- **Clear error patterns** (same error multiple times)

### 2. Use Conservative Algorithm

For memory files, use **SIMBA** (not MIPROv2):
- More conservative mutations
- Preserves working content
- Less risk of breaking good guidance

### 3. Focus on Specific Errors

Don't try to fix everything at once:
```bash
# Good: Focus on one error type
--focus-errors cycle_by_cycle_updates

# Bad: Try to fix everything
--focus-errors cycle_by_cycle_updates,scope_error,type_error,syntax_error
```

### 4. Iterate Gradually

- Optimize one file at a time
- Test each optimization before moving to next
- Collect new data between rounds
- Track improvement metrics

### 5. A/B Test Everything

Always compare optimized vs. original:
- Run 5-10 sessions with each version
- Measure error rates objectively
- Keep whichever performs better
- Don't assume optimization always helps

## Troubleshooting

### "Not enough relevant sessions"

**Problem**: Only 2-3 sessions used this file

**Solution**:
```bash
# Lower minimum threshold
python optimize_memory_file.py --min-sessions 2 ...

# Or collect more sessions
for i in {1..10}; do
  ./run-openspec-apply.sh ~/projects implement-device$i standard
done
```

### "Optimization made it worse"

**Problem**: Error rate increased after optimization

**Possible causes**:
1. **Overfitting** - Optimized for specific examples, lost generality
2. **Wrong focus** - Focused on wrong error type
3. **Insufficient data** - Not enough sessions to learn from

**Solution**:
```bash
# Revert to original
cp ../openspec-memories/02_DML_Anti_Patterns.md.backup \
   ../openspec-memories/02_DML_Anti_Patterns.md

# Try different approach:
# 1. Collect more diverse sessions
# 2. Use different focus-errors
# 3. Try manual improvements first
```

### "No improvement after optimization"

**Problem**: Error rate unchanged

**Possible causes**:
1. **File already optimal** - Nothing to improve
2. **Wrong file** - Error caused by different file
3. **Tool/system issue** - Not an instruction problem

**Solution**:
```bash
# Analyze if this file is really the issue
python analyze_memory_effectiveness.py --sessions historical_sessions.json

# Check if errors occur even when file NOT read
# If yes, file isn't the problem
```

## Expected Results

Based on testing with real sessions:

| File Type | Typical Improvement | Time to Optimize |
|-----------|-------------------|------------------|
| Anti-Patterns | 20-40% error reduction | 5-10 minutes |
| Troubleshooting | 15-30% faster resolution | 5-10 minutes |
| Register Access | 30-50% fewer scope errors | 5-10 minutes |
| Test Patterns | 20-35% better test quality | 5-10 minutes |

**Overall**: Expect 20-40% improvement in specific error rates after optimizing high-priority files.

## Conclusion

Memory file optimization is often **more effective** than optimizing main instructions because:

- ✅ **Focused scope** - One topic at a time
- ✅ **Clear metrics** - Track specific errors
- ✅ **Lower risk** - Won't break workflow
- ✅ **Faster iteration** - Optimize in minutes
- ✅ **Measurable impact** - Track error reduction

Start with the analysis tool, identify high-priority files, optimize them one at a time, and measure the improvement. This iterative approach leads to steady, measurable gains in agent performance.
