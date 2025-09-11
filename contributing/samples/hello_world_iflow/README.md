# Hello World iFlow Agent

This sample demonstrates how to create a simple agent using the iFlow Qwen3-Coder model with ADK. The agent can roll dice and check if numbers are prime.

## Prerequisites

1. **iFlow API Key**: You need an API key from iFlow to use their Qwen3-Coder model.
2. **Environment Setup**: Set the `IFLOW_API_KEY` environment variable with your API key.

## Setup

1. Set your iFlow API key:
   ```bash
   export IFLOW_API_KEY="your-iflow-api-key-here"
   ```

2. Install dependencies (if not already installed):
   ```bash
   pip install google-adk
   ```

## Running the Agent

### Option 1: Run the main script
```bash
cd contributing/samples/hello_world_iflow
python main.py
```

### Option 2: Run the agent directly
```bash
cd contributing/samples/hello_world_iflow
python agent.py
```

## Features

The agent can:
- **Roll dice**: Ask it to roll dice with any number of sides
- **Check prime numbers**: Determine if numbers are prime
- **Combined operations**: Roll dice and check if the results are prime

## Example Interactions

```
You: Roll a 6-sided die
Agent: I'll roll a 6-sided die for you! *rolls* The result is 4.

You: Roll a 20-sided die and check if the result is prime
Agent: I'll roll a 20-sided die and then check if the result is prime.
*rolls* The result is 17.
Now let me check if 17 is prime... 17 is a prime number!

You: Check if 15, 17, and 23 are prime
Agent: Let me check those numbers for you:
17, 23 are prime numbers.
```

## Model Configuration

This sample uses:
- **Model**: `iflow/Qwen3-Coder`
- **Provider**: iFlow via LiteLLM
- **Authentication**: API key via `IFLOW_API_KEY` environment variable
- **Base URL**: `https://apis.iflow.cn/v1/`

## Code Structure

- `agent.py`: Contains the agent definition with tools and configuration
- `main.py`: Main script to run the interactive agent
- `__init__.py`: Package initialization file

## Tools

The agent has access to two tools:

1. **`roll_die(sides: int)`**: Rolls a die with the specified number of sides
2. **`check_prime(nums: list[int])`**: Checks if a list of numbers are prime

## Error Handling

The agent includes proper error handling for:
- Missing API key
- Invalid user input
- Network connectivity issues
- Model response errors

## Notes

- The agent maintains state between interactions (remembers previous dice rolls)
- Safety settings are configured to allow dice rolling content
- The agent uses streaming responses for real-time interaction
- Type 'quit', 'exit', or 'q' to stop the agent

## Troubleshooting

### Common Issues

1. **Missing API Key Error**:
   ```
   ValueError: IFLOW_API_KEY environment variable must be set to use iFlow models
   ```
   **Solution**: Set the `IFLOW_API_KEY` environment variable with your API key.

2. **Network Connection Issues**:
   - Check your internet connection
   - Verify the API key is valid
   - Ensure the iFlow service is accessible

3. **Model Not Found**:
   - Verify you're using the correct model name: `iflow/Qwen3-Coder`
   - Check if the model is available in your iFlow account

For more information about iFlow models and API usage, refer to the iFlow documentation.