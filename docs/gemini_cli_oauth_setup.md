# Gemini CLI OAuth Setup

## OAuth Client Configuration

To use Gemini CLI OAuth authentication, you need to configure the OAuth client credentials.

### Option 1: Use Default Gemini CLI Credentials (Recommended)

The ADK uses the same OAuth client credentials as the official Gemini CLI by default. These are public client credentials that are safe to use.

No additional setup is required - the default credentials will be used automatically.

### Option 2: Use Custom OAuth Credentials

If you want to use your own OAuth client credentials:

1. Create a Google Cloud project and enable the necessary APIs
2. Create OAuth 2.0 credentials in the Google Cloud Console
3. Set the following environment variables:

```bash
export GEMINI_CLI_CLIENT_ID="your-client-id.apps.googleusercontent.com"
export GEMINI_CLI_CLIENT_SECRET="your-client-secret"
```

### Security Note

The default OAuth client credentials are the same public credentials used by the official Gemini CLI. These are designed to be used by the public and are not considered secrets in the traditional sense, similar to how mobile apps and desktop applications handle OAuth.

For production use cases or enterprise environments, it's recommended to use your own OAuth client credentials via environment variables.

## Usage

```python
from google.adk.agents import Agent
from google.adk.auth import AuthType
from google.adk.models import GeminiCLI

# Uses default Gemini CLI credentials
agent = Agent(
    model=GeminiCLI(auth_type=AuthType.LOGIN_WITH_GOOGLE),
    system_instruction="You are a helpful assistant."
)

# Or specify custom credentials via environment variables
# GEMINI_CLI_CLIENT_ID and GEMINI_CLI_CLIENT_SECRET
```

The authentication flow will use Google's device code flow, which doesn't require opening browser windows or ports.