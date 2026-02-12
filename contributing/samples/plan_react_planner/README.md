# PlanReActPlanner Example

This sample demonstrates how to use `PlanReActPlanner` to create agents with structured planning and reasoning capabilities.

## What is PlanReActPlanner?

`PlanReActPlanner` is a planner that implements the Plan-ReAct pattern, which constrains the LLM to:

1. **Plan** - Create an explicit plan before taking actions
2. **Reason** - Provide reasoning between tool executions
3. **Act** - Execute tools based on the plan
4. **Replan** - Adapt the plan based on tool results if needed
5. **Answer** - Provide a final answer after gathering information

## Key Features

### Structured Output with Tags

The planner uses special tags to organize the agent's response:

- `/*PLANNING*/` - Initial plan for answering the query
- `/*REASONING*/` - Reasoning about current state and next steps
- `/*ACTION*/` - Tool execution code
- `/*REPLANNING*/` - Revised plan if initial plan fails
- `/*FINAL_ANSWER*/` - Final answer to the user's query

### Thought Separation

Parts marked with planning/reasoning tags are labeled as `thought=True`, allowing you to:
- Filter out internal reasoning from user-facing responses
- Display reasoning separately for debugging
- Track the agent's decision-making process

### No Special Model Requirements

Unlike `BuiltInPlanner`, `PlanReActPlanner` works with any LLM - it uses prompt engineering rather than model-native thinking features.

## When to Use PlanReActPlanner

✅ **Good use cases:**
- Complex multi-step workflows requiring coordination
- Tasks where planning before acting improves outcomes
- Scenarios with iterative tool use (build → test → fix cycles)
- When you need to debug agent reasoning
- Tasks requiring adaptation based on intermediate results
- **Using Gemini models** (best compatibility with structured outputs)

❌ **Not ideal for:**
- Simple, single-step queries
- Highly structured workflows already enforced by instructions
- When you need maximum control over exact output format
- Token-sensitive applications (planning adds overhead)
- **Models that struggle with structured formats** (may output tags without actions)

## Comparison with Other Approaches

| Approach | Planning Method | Model Requirements | Transparency | Control |
|----------|----------------|-------------------|--------------|---------|
| **No Planner** | Implicit in instructions | Any | High | Maximum |
| **PlanReActPlanner** | Explicit with tags | Any | High | Medium |
| **BuiltInPlanner** | Native model thinking | Gemini 2.0+ | Low-Medium | Low |

## Running the Example

### Model Configuration

This example uses `iflow/qwen3-coder-plus`, the same model used by OpenSpec agents. This demonstrates that PlanReActPlanner works with any LLM, not just Gemini models.

### Demo Scripts

The example includes separate demo scripts to avoid async event loop conflicts:

```bash
# Run demo WITHOUT planner (baseline)
python contributing/samples/plan_react_planner/demo_without_planner.py

# Run demo WITH planner
python contributing/samples/plan_react_planner/demo_with_planner.py
```

Each demo runs independently and shows:
- Event structure and count
- Tool calls made
- Final response
- Key characteristics of the approach

### Interactive Usage

```bash
# Run the agent interactively
adk run contributing/samples/plan_react_planner

# Example queries to try:
# 1. "What are the most impactful recent papers on machine learning?"
# 2. "Analyze the research trends in quantum computing and identify the most cited work"
# 3. "Compare the research impact between machine learning and quantum computing"
```

**Note:** When using `adk run`, you'll see `/*PLANNING*/`, `/*REASONING*/`, and `/*ACTION*/` tags, but the actual function calls won't be displayed in the terminal. This is normal - the tools are still being called. To see full event details including function calls, run the demo scripts instead.

### What to Observe

When you run queries, notice how the agent:

1. **Creates a plan first** (under `/*PLANNING*/`):
   ```
   /*PLANNING*/
   To answer this question, I will:
   1. Search for recent papers on machine learning
   2. Get citation counts for the top papers
   3. Analyze research trends in the field
   4. Calculate overall research impact
   5. Synthesize findings into a comprehensive answer
   ```

2. **Reasons between actions** (under `/*REASONING*/`):
   ```
   /*REASONING*/
   I found 3 papers on machine learning. The most cited is "Transformer 
   Architectures in NLP" with 890 citations. Now I need to get detailed 
   citation data for this paper to understand its impact better.
   ```

3. **Executes tools** (under `/*ACTION*/`):
   ```
   /*ACTION*/
   get_citation_count("Transformer Architectures in NLP")
   ```

4. **Provides final answer** (under `/*FINAL_ANSWER*/`):
   ```
   /*FINAL_ANSWER*/
   Based on my analysis, the most impactful recent papers on machine learning are...
   ```

## Code Structure

```python
from google.adk.agents.llm_agent import Agent
from google.adk.planners.plan_re_act_planner import PlanReActPlanner

root_agent = Agent(
    model='iflow/qwen3-coder-plus',  # Works with any LLM
    name='research_assistant',
    instruction="...",  # Your agent instructions
    tools=[...],        # Your tools
    planner=PlanReActPlanner(),  # Enable structured planning
)
```

## Advanced: Accessing Thoughts

You can access the planning and reasoning parts programmatically:

```python
from google.adk.runners import Runner

runner = Runner()
result = runner.run(root_agent, "Your query here")

# Access all events
for event in result.events:
    if hasattr(event, 'response_parts'):
        for part in event.response_parts:
            if hasattr(part, 'thought') and part.thought:
                print(f"Thought: {part.text}")
            elif part.text:
                print(f"Output: {part.text}")
```

## Customizing the Planner

The `PlanReActPlanner` uses built-in instructions, but you can complement them with your own agent instructions:

```python
root_agent = Agent(
    model='iflow/qwen3-coder-plus',
    instruction="""
    Your domain-specific instructions here.
    
    The planner will add structured planning on top of these instructions.
    Focus on WHAT the agent should do, and let the planner handle HOW to structure it.
    """,
    planner=PlanReActPlanner(),
)
```

## Tips for Best Results

1. **Clear tool descriptions** - The planner needs to understand what each tool does to plan effectively
2. **Complementary instructions** - Your instructions should focus on domain knowledge, not planning structure
3. **Complex queries** - The planner shines with multi-step queries that benefit from explicit planning
4. **Monitor token usage** - Planning adds overhead; use for tasks where it provides clear value

## Troubleshooting

### Agent not following the plan

- Ensure your instructions don't conflict with the planner's structure
- Try simpler queries first to verify the planner is working
- Check that tools are properly described

### Too much planning overhead

- Consider if your task really needs explicit planning
- For simple tasks, no planner or custom instructions may be better
- Use `BuiltInPlanner` if you want thinking without visible planning tags

### Plan doesn't adapt to failures

- Ensure tool error messages are informative
- The agent will replan if tools fail, but needs clear error signals
- Check that your tools return meaningful error messages

### `adk run` doesn't show function calls after `/*ACTION*/`

When using `adk run`, you may see `/*ACTION*/` tags but not the actual function calls in the terminal output:

**What you see:**
```
[research_assistant]: /*REASONING*/.../*ACTION*/
[research_assistant]: /*REASONING*/.../*ACTION*/
```

**This is normal!** This is a display/logging behavior of `adk run`, not a bug. The function calls ARE happening (you can tell because the agent continues reasoning with new information), but `adk run` doesn't display them in the terminal by default.

**To verify tools are being called:**
1. Check that the agent's reasoning changes after each `/*ACTION*/` (it gets new information)
2. Look at the final answer - it should contain specific data from tool calls
3. Run the demo scripts (`demo_with_planner.py`) which show full event details including tool calls

**This is different from a real problem** where the model outputs `/*ACTION*/` but doesn't actually generate a function call. Signs of that issue:
- Agent gets stuck in a loop repeating the same reasoning
- Final answer is generic without specific data
- Agent says it will call a tool but never does

### Agent truly not calling tools (rare issue)

This can happen with some models that don't fully follow the structured format:

**Symptoms:**
- Agent repeats the same reasoning without progress
- Final answer lacks specific data that tools would provide
- Agent acknowledges it should use tools but doesn't

**Causes:**
- The model understands it should act but doesn't generate the function call
- Some models work better without explicit planning structure

**Solutions:**
1. **Try without planner first**: Remove `planner=PlanReActPlanner()` to see if the agent calls tools naturally
2. **Use a different model**: Gemini models are specifically trained for structured outputs
3. **Simplify the query**: Start with direct tool-calling queries like "Search for papers on X"
4. **Check tool descriptions**: Ensure your tool docstrings clearly explain when to use each tool

If you consistently see this issue, the model may not be well-suited for PlanReActPlanner. Consider using the agent without a planner, or try a Gemini model which has better support for structured outputs.

## Related Samples

- `fields_planner/` - Example using `BuiltInPlanner` with native model thinking
- `tool_agent_tool_config/` - Basic tool usage without planning
- `callbacks/` - Using callbacks to observe agent execution

## Learn More

- [ADK Planners Documentation](https://github.com/google/adk-python/blob/main/docs/planners.md)
- [Plan-ReAct Pattern](https://arxiv.org/abs/2210.03629)
- [ReAct: Reasoning and Acting](https://arxiv.org/abs/2210.03629)
