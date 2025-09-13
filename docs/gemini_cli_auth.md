# Gemini CLI Authentication in ADK Python

This document describes how to use Gemini CLI-compatible authentication methods in ADK Python.

## Overview

The ADK Python library now supports the same authentication methods as the Gemini CLI, allowing you to seamlessly use Gemini models with various authentication approaches:

- **OAuth (LOGIN_WITH_GOOGLE)**: Interactive OAuth flow using your Google account
- **API Key (USE_GEMINI)**: Direct API key authentication with Gemini API
- **Vertex AI (USE_VERTEX_AI)**: Vertex AI authentication with project/location or API key
- **Cloud Shell (CLOUD_SHELL)**: Automatic authentication in Google Cloud Shell

## Quick Start

```python
from google.adk.agents import Agent
from google.adk.auth import AuthType
from google.adk.models import GeminiCLI

# Auto-detect authentication method
agent = Agent(
    model=GeminiCLI(model="gemini-2.5-flash"),
    system_instruction="You are a helpful assistant."
)

# Or specify explicit authentication
agent = Agent(
    model=GeminiCLI(
        model="gemini-2.5-flash",
        auth_type=AuthType.LOGIN_WITH_GOOGLE
    ),
    system_instruction="You are a helpful assistant."
)

response = await agent.run("Hello!")
```

## Authentication Methods

### 1. OAuth Authentication (LOGIN_WITH_GOOGLE)

Uses OAuth 2.0 flow to authenticate with your Google account. This is the most secure method for personal use.

```python
from google.adk.models import GeminiCLI
from google.adk.auth import AuthType

model = GeminiCLI(
    model="gemini-2.5-flash",
    auth_type=AuthType.LOGIN_WITH_GOOGLE,
    no_browser=False  # Set to True for device code flow
)
```

**Environment Variables:**
- `NO_BROWSER=true`: Use device code flow instead of opening browser
- `OAUTH_CALLBACK_PORT`: Specify custom port for OAuth callback (optional)

**Credentials Storage:**
- Cached in `~/.gemini/oauth_creds.json`
- Automatically refreshed when expired

### 2. API Key Authentication (USE_GEMINI)

Uses a Gemini API key for direct authentication with the Gemini API.

```python
model = GeminiCLI(
    model="gemini-2.5-flash",
    auth_type=AuthType.USE_GEMINI
)
```

**Environment Variables:**
- `GEMINI_API_KEY`: Your Gemini API key (required)

**How to get an API key:**
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key
3. Set the `GEMINI_API_KEY` environment variable

### 3. Vertex AI Authentication (USE_VERTEX_AI)

Uses Vertex AI for authentication, supporting both project-based and express mode.

```python
model = GeminiCLI(
    model="gemini-2.5-flash",
    auth_type=AuthType.USE_VERTEX_AI
)
```

**Environment Variables (Option 1 - Project Mode):**
- `GOOGLE_CLOUD_PROJECT`: Your Google Cloud project ID
- `GOOGLE_CLOUD_LOCATION`: Your preferred location (e.g., "us-central1")

**Environment Variables (Option 2 - Express Mode):**
- `GOOGLE_API_KEY`: Your Google API key

**Authentication:**
- Uses Application Default Credentials (ADC)
- Run `gcloud auth application-default login` to set up ADC

### 4. Cloud Shell Authentication (CLOUD_SHELL)

Automatically uses Cloud Shell's built-in authentication when running in Google Cloud Shell.

```python
model = GeminiCLI(
    model="gemini-2.5-flash",
    auth_type=AuthType.CLOUD_SHELL
)
```

**Requirements:**
- Must be running in Google Cloud Shell
- No additional setup required

## Auto-Detection

If you don't specify an `auth_type`, the library will automatically detect the best authentication method based on your environment:

1. **Cloud Shell**: If `GOOGLE_CLOUD_SHELL` environment variable is set
2. **Gemini API**: If `GEMINI_API_KEY` environment variable is set
3. **Vertex AI**: If `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` are set, or if `GOOGLE_API_KEY` is set
4. **OAuth**: Default fallback method

```python
# Auto-detection
model = GeminiCLI(model="gemini-2.5-flash")
```

## Configuration Options

### Model Selection

All Gemini models are supported:

```python
# Latest models
model = GeminiCLI(model="gemini-2.5-pro")
model = GeminiCLI(model="gemini-2.5-flash")
model = GeminiCLI(model="gemini-2.5-flash-lite")

# Older models
model = GeminiCLI(model="gemini-1.5-pro")
model = GeminiCLI(model="gemini-1.5-flash")
```

### Retry Options

Configure HTTP retry behavior:

```python
from google.genai import types

model = GeminiCLI(
    model="gemini-2.5-flash",
    retry_options=types.HttpRetryOptions(
        initial_delay=1,
        attempts=3
    )
)
```

### Proxy Support

Configure proxy settings via environment variables:

```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=https://proxy.example.com:8080
```

## Error Handling

The library provides clear error messages for authentication issues:

```python
from google.adk.auth import GeminiAuthValidator, AuthType

# Validate authentication before creating model
error = GeminiAuthValidator.validate_auth_method(AuthType.USE_GEMINI)
if error:
    print(f"Authentication error: {error}")
else:
    model = GeminiCLI(auth_type=AuthType.USE_GEMINI)
```

## Migration from Gemini CLI

If you're already using the Gemini CLI, your existing authentication setup will work seamlessly:

1. **OAuth credentials**: Automatically detected from `~/.gemini/oauth_creds.json`
2. **Environment variables**: Same variable names and behavior
3. **API keys**: Use the same `GEMINI_API_KEY` variable

## Examples

See `examples/gemini_cli_auth_example.py` for a complete working example demonstrating all authentication methods.

## Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY environment variable not found"**
   - Set the `GEMINI_API_KEY` environment variable
   - Get an API key from [Google AI Studio](https://aistudio.google.com/)

2. **"When using Vertex AI, you must specify..."**
   - Set `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` for project mode
   - Or set `GOOGLE_API_KEY` for express mode
   - Run `gcloud auth application-default login` for ADC

3. **OAuth browser issues**
   - Set `NO_BROWSER=true` to use device code flow
   - Check firewall settings for localhost connections
   - Ensure port 8080 (or custom port) is available

4. **"Could not authenticate using Cloud Shell credentials"**
   - Ensure you're running in Google Cloud Shell
   - Check that the Cloud Shell environment is properly configured

### Debug Mode

Enable debug logging to troubleshoot authentication issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Considerations

1. **API Keys**: Store securely and never commit to version control
2. **OAuth Credentials**: Cached credentials are stored with restricted permissions (600)
3. **Environment Variables**: Use `.env` files or secure environment management
4. **Proxy Settings**: Ensure proxy servers are trusted when configured

## Compatibility

- **Python**: 3.8+
- **Dependencies**: `google-genai`, `google-auth`, `google-auth-oauthlib`, `httpx`
- **Platforms**: Linux, macOS, Windows
- **Cloud Environments**: Google Cloud Shell, Vertex AI Workbench, local development