# API Endpoints

<cite>
**Referenced Files in This Document**   
- [fast_api.py](file://src/google/adk/cli/fast_api.py)
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py)
- [agent_graph.py](file://src/google/adk/cli/agent_graph.py)
- [auth_handler.py](file://src/google/adk/auth/auth_handler.py)
- [browser](file://src/google/adk/cli/browser)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Core Agent Execution Endpoints](#core-agent-execution-endpoints)
3. [Session Management APIs](#session-management-apis)
4. [Artifact Management Endpoints](#artifact-management-endpoints)
5. [Evaluation System Endpoints](#evaluation-system-endpoints)
6. [Real-Time Streaming Protocol](#real-time-streaming-protocol)
7. [Development UI Integration](#development-ui-integration)
8. [Authentication and Security](#authentication-and-security)
9. [Error Handling and Recovery](#error-handling-and-recovery)
10. [Extending the API](#extending-the-api)

## Introduction

The Agent Development Kit (ADK) provides a comprehensive API for interacting with AI agents through both RESTful and real-time streaming interfaces. This documentation details the endpoints exposed by the FastAPI application, focusing on agent execution, session management, artifact handling, and evaluation capabilities. The API supports multiple interaction patterns including request-response, Server-Sent Events (SSE) for streaming, and WebSocket-based bidirectional communication for live agent interactions.

The API is designed to support both development and production use cases, with endpoints for agent testing, debugging, and evaluation. The Development UI integrates with these endpoints to provide a rich interface for agent development and testing.

**Section sources**
- [fast_api.py](file://src/google/adk/cli/fast_api.py#L56-L387)
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py#L210-L1100)

## Core Agent Execution Endpoints

The core agent execution endpoints enable interaction with AI agents by sending user messages and receiving agent responses. These endpoints support both synchronous and streaming response patterns.

### Run Agent (POST /run)

Executes an agent with a user message and returns the complete response as a list of events.

**Endpoint**: `POST /run`

**Request Body**:
```json
{
  "app_name": "string",
  "user_id": "string",
  "session_id": "string",
  "new_message": {
    "role": "user",
    "parts": [
      {
        "text": "string"
      }
    ]
  },
  "streaming": false,
  "state_delta": {}
}
```

**Parameters**:
- `app_name`: Name of the agent application to execute
- `user_id`: Identifier for the user interacting with the agent
- `session_id`: Identifier for the conversation session
- `new_message`: User message content in Google GenAI format
- `streaming`: Boolean flag (ignored for this endpoint)
- `state_delta`: Optional state changes to apply

**Response**: Array of Event objects containing the complete agent response sequence.

**Error Codes**:
- `404`: Session not found
- `400`: Invalid request parameters

**Section sources**
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py#L894-L912)

### Run Agent Streaming (POST /run_sse)

Executes an agent with a user message and streams the response using Server-Sent Events (SSE). This endpoint provides real-time updates as the agent generates content.

**Endpoint**: `POST /run_sse`

**Request Body**: Same as `/run` endpoint.

**Response**: Streaming response with `text/event-stream` media type. Each event is formatted as:
```
data: {"id": "event-123", "type": "content", "content": {"text": "Hello"}}
```

**Streaming Mode**: When `streaming=true` in the request, the agent generates content incrementally. When `streaming=false`, the response is streamed but generated synchronously.

**Use Case**: Ideal for UI applications that need to display agent responses as they are generated, providing a more interactive experience.

**Section sources**
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py#L914-L957)

## Session Management APIs

The session management endpoints provide CRUD operations for conversation sessions, enabling persistent state across agent interactions.

### List Sessions (GET /apps/{app_name}/users/{user_id}/sessions)

Retrieves a list of active sessions for a specific user and agent application.

**Endpoint**: `GET /apps/{app_name}/users/{user_id}/sessions`

**Parameters**:
- `app_name`: Agent application name
- `user_id`: User identifier

**Response**: Array of Session objects excluding evaluation-generated sessions.

**Section sources**
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py#L410-L423)

### Get Session (GET /apps/{app_name}/users/{user_id}/sessions/{session_id})

Retrieves the details of a specific session.

**Endpoint**: `GET /apps/{app_name}/users/{user_id}/sessions/{session_id}`

**Parameters**:
- `app_name`: Agent application name
- `user_id`: User identifier
- `session_id`: Session identifier

**Response**: Session object containing session state, history, and metadata.

**Error Codes**:
- `404`: Session not found

**Section sources**
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py#L395-L407)

### Create Session (POST /apps/{app_name}/users/{user_id}/sessions)

Creates a new conversation session with optional initial state.

**Endpoint**: `POST /apps/{app_name}/users/{user_id}/sessions`

**Request Body**:
```json
{
  "state": {},
  "events": []
}
```

**Parameters**:
- `app_name`: Agent application name
- `user_id`: User identifier
- `state`: Optional initial session state
- `events`: Optional initial events to seed the session

**Response**: Created Session object with generated session ID.

**Section sources**
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py#L450-L468)

### Create Session with ID (POST /apps/{app_name}/users/{user_id}/sessions/{session_id})

Creates a new session with a specified session ID.

**Endpoint**: `POST /apps/{app_name}/users/{user_id}/sessions/{session_id}`

**Request Body**:
```json
{
  "state": {}
}
```

**Error Codes**:
- `400`: Session already exists with the specified ID

**Section sources**
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py#L425-L447)

### Delete Session (DELETE /apps/{app_name}/users/{user_id}/sessions/{session_id})

Deletes a session and all associated data.

**Endpoint**: `DELETE /apps/{app_name}/users/{user_id}/sessions/{session_id}`

**Parameters**:
- `app_name`: Agent application name
- `user_id`: User identifier
- `session_id`: Session identifier to delete

**Section sources**
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py#L470-L477)

## Artifact Management Endpoints

The artifact management endpoints provide access to files and data generated during agent execution.

### Load Artifact (GET)

Retrieves a specific artifact by name and optional version.

**Endpoint**: `GET /apps/{app_name}/users/{user_id}/sessions/{session_id}/artifacts/{artifact_name}`

**Query Parameters**:
- `version`: Optional version number (defaults to latest)

**Response**: Artifact content as a Part object.

**Error Codes**:
- `404`: Artifact not found

**Section sources**
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py#L813-L832)

### Load Artifact Version (GET)

Retrieves a specific version of an artifact.

**Endpoint**: `GET /apps/{app_name}/users/{user_id}/sessions/{session_id}/artifacts/{artifact_name}/versions/{version_id}`

**Parameters**:
- `version_id`: Specific version to retrieve

**Section sources**
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py#L835-L854)

### List Artifact Names (GET)

Retrieves a list of all artifact names for a session.

**Endpoint**: `GET /apps/{app_name}/users/{user_id}/sessions/{session_id}/artifacts`

**Response**: Array of artifact filenames.

**Section sources**
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py#L857-L865)

### List Artifact Versions (GET)

Retrieves a list of available versions for a specific artifact.

**Endpoint**: `GET /apps/{app_name}/users/{user_id}/sessions/{session_id}/artifacts/{artifact_name}/versions`

**Response**: Array of version numbers.

**Section sources**
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py#L868-L879)

### Delete Artifact (DELETE)

Removes an artifact and all its versions.

**Endpoint**: `DELETE /apps/{app_name}/users/{user_id}/sessions/{session_id}/artifacts/{artifact_name}`

**Section sources**
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py#L882-L893)

## Evaluation System Endpoints

The evaluation system provides endpoints for creating, managing, and running agent evaluations.

### Create Evaluation Set (POST /apps/{app_name}/eval-sets)

Creates a new evaluation set for testing agent performance.

**Endpoint**: `POST /apps/{app_name}/eval-sets`

**Request Body**:
```json
{
  "eval_set": {
    "eval_set_id": "string",
    "eval_cases": []
  }
}
```

**Response**: Created EvalSet object.

**Error Codes**:
- `400`: Invalid evaluation set configuration

**Section sources**
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py#L479-L496)

### List Evaluation Sets (GET /apps/{app_name}/eval-sets)

Retrieves all evaluation sets for an agent application.

**Endpoint**: `GET /apps/{app_name}/eval-sets`

**Response**: List of evaluation set IDs.

**Section sources**
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py#L519-L531)

### Add Session to Evaluation Set (POST)

Converts a conversation session into an evaluation case.

**Endpoint**: `POST /apps/{app_name}/eval-sets/{eval_set_id}/add-session`

**Request Body**:
```json
{
  "eval_id": "string",
  "session_id": "string",
  "user_id": "string"
}
```

**Process**: The session history is converted into evaluation invocations and added to the specified evaluation set.

**Section sources**
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py#L547-L590)

### Run Evaluation (POST /apps/{app_name}/eval_sets/{eval_set_id}/run_eval)

Executes evaluations against the specified evaluation cases.

**Endpoint**: `POST /apps/{app_name}/eval_sets/{eval_set_id}/run_eval`

**Request Body**:
```json
{
  "eval_ids": ["string"],
  "eval_metrics": []
}
```

**Parameters**:
- `eval_ids`: Array of evaluation case IDs to run (empty for all)
- `eval_metrics`: Array of metrics to calculate

**Response**: Array of RunEvalResult objects with evaluation outcomes.

**Section sources**
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py#L694-L763)

### Get Evaluation Result (GET)

Retrieves the results of a completed evaluation.

**Endpoint**: `GET /apps/{app_name}/eval_results/{eval_result_id}`

**Response**: EvalSetResult object containing detailed evaluation metrics and outcomes.

**Section sources**
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py#L766-L782)

## Real-Time Streaming Protocol

The real-time streaming protocol enables bidirectional communication between clients and agents using WebSockets, supporting live interactions with audio, video, and text modalities.

### Live Agent Execution (WebSocket /run_live)

Establishes a WebSocket connection for bidirectional streaming with an agent.

**Endpoint**: `ws://host:port/run_live`

**Query Parameters**:
- `app_name`: Agent application name
- `user_id`: User identifier
- `session_id`: Session identifier
- `modalities`: Array of supported modalities ("TEXT", "AUDIO")

**Connection Flow**:
1. Client sends WebSocket upgrade request with parameters
2. Server validates session and accepts connection
3. Two concurrent tasks are established:
   - Forward events from agent to client
   - Process messages from client to agent

**Message Format**: All messages are JSON-serialized Event objects.

**Section sources**
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py#L1008-L1078)

### Streaming Tools Protocol

Streaming tools enable tools to yield intermediate results during execution, allowing agents to respond to partial outputs.

**Requirements**:
- Tool function must be `async`
- Return type must be `AsyncGenerator`
- Can yield intermediate results (e.g., text updates, progress indicators)

**Use Cases**:
- Monitoring stock prices with real-time updates
- Processing video streams with frame-by-frame analysis
- Long-running operations with progress reporting

**Section sources**
- [live_bidi_streaming_tools_agent/readme.md](file://contributing/samples/live_bidi_streaming_tools_agent/readme.md#L1-L19)

## Development UI Integration

The Development UI provides a web-based interface for agent development and testing, served through the API server.

### UI Endpoints

When the web interface is enabled, the following endpoints are available:

**Root Redirect**: `GET /` redirects to `/dev-ui/`

**UI Base**: `GET /dev-ui` redirects to `/dev-ui/`

**Static Assets**: `GET /dev-ui/{path}` serves static files from the browser directory.

The UI is built with Angular and includes components for:
- Agent selection and configuration
- Conversation interface with message history
- Session management
- Evaluation set creation and management
- Debugging tools and trace visualization

**Section sources**
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py#L1079-L1097)
- [browser](file://src/google/adk/cli/browser)

## Authentication and Security

The API includes authentication mechanisms for securing agent interactions and tool access.

### OAuth2 Integration

The system supports OAuth2 authentication through the AuthHandler class, which manages the credential exchange flow.

**Authentication Flow**:
1. Agent requests authentication via auth tool
2. System generates authorization URL
3. User completes OAuth2 flow
4. Tokens are exchanged and stored
5. Subsequent requests include valid credentials

**Components**:
- `AuthHandler`: Manages the authentication flow
- `OAuth2CredentialExchanger`: Handles token exchange
- `AuthConfig`: Configuration for authentication schemes

**Section sources**
- [auth_handler.py](file://src/google/adk/auth/auth_handler.py#L38-L199)

### Tool Callback Security

Tool callbacks provide security hooks that can validate and potentially block tool executions.

**Security Callbacks**:
- Before-tool callbacks can audit or block tool calls
- After-tool callbacks can enhance or modify responses
- Async callbacks support complex validation logic

**Example**: Blocking weather requests for restricted locations or preventing division by zero in calculations.

**Section sources**
- [live_tool_callbacks_agent/readme.md](file://contributing/samples/live_tool_callbacks_agent/readme.md#L1-L54)
- [callbacks.py](file://contributing/samples/core_callback_config/callbacks.py#L50-L79)

## Error Handling and Recovery

The API implements comprehensive error handling to ensure robust operation and graceful recovery from failures.

### Error Response Format

Standard error responses follow the format:
```json
{
  "detail": "Error description"
}
```

With appropriate HTTP status codes:
- `400`: Bad Request - Invalid parameters
- `404`: Not Found - Resource not found
- `422`: Unprocessable Entity - Validation errors
- `500`: Internal Server Error - Unexpected failures

### Connection Persistence

WebSocket connections include automatic cleanup mechanisms:

**Failure Handling**:
- Tasks are monitored for exceptions
- Resources are cleaned up on disconnect
- Pending tasks are canceled gracefully
- Errors are logged with full traceback

**Reconnection**: Clients should implement exponential backoff when reconnecting after disconnections.

**Section sources**
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py#L1053-L1077)

## Extending the API

The API can be extended with custom endpoints for specialized debugging and development needs.

### Custom Endpoint Registration

Additional endpoints can be added by modifying the FastAPI app instance returned by `get_fast_api_app()`.

**Extension Points**:
- Add new REST endpoints for custom functionality
- Register WebSocket handlers for specialized protocols
- Integrate with external monitoring systems
- Add debugging endpoints for internal state inspection

### MCP Server Integration

The system supports integration with MCP (Model Context Protocol) servers via SSE and Streamable HTTP.

**Configuration**:
- Define connection parameters (URL, headers, timeouts)
- Filter available tools
- Handle authentication
- Implement error recovery

**Example**: Connecting to a local filesystem MCP server at `http://localhost:3000/sse`.

**Section sources**
- [fast_api.py](file://src/google/adk/cli/fast_api.py#L307-L385)
- [spec_kit_integration/spec_kit_tools.py](file://contributing/samples/spec_kit_integration/spec_kit_tools.py#L904-L944)