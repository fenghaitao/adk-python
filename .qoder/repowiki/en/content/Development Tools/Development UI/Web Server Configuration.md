# Web Server Configuration

<cite>
**Referenced Files in This Document**   
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py)
- [fast_api.py](file://src/google/adk/cli/fast_api.py)
- [runners.py](file://src/google/adk/runners.py)
- [session.py](file://src/google/adk/sessions/session.py)
- [envs.py](file://src/google/adk/cli/utils/envs.py)
- [logs.py](file://src/google/adk/cli/utils/logs.py)
- [index.html](file://src/google/adk/cli/browser/index.html)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)

## Introduction
The ADK Development Web Server is a FastAPI-based server that powers the development UI for agent orchestration and session management. This documentation provides comprehensive details about the server's architecture, implementation, configuration, and integration with the Runner and Session systems. The server enables bidirectional communication through WebSocket endpoints for real-time streaming of agent responses and supports various customization options for server behavior, environment variables, logging, and telemetry.

## Project Structure
The ADK Development Web Server is organized within the `src/google/adk/cli` directory, with key components including the web server implementation, FastAPI configuration, and supporting utilities. The server serves both API endpoints and static assets for the development UI, with a clear separation between server logic, session management, and agent orchestration components.

```mermaid
graph TD
subgraph "Web Server Components"
adk_web_server[adk_web_server.py]
fast_api[fast_api.py]
browser[browser/]
end
subgraph "Core Services"
runners[runners.py]
sessions[session.py]
utils[utils/]
end
adk_web_server --> fast_api
fast_api --> runners
fast_api --> sessions
fast_api --> browser
adk_web_server --> envs
adk_web_server --> logs
```

**Diagram sources**
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py)
- [fast_api.py](file://src/google/adk/cli/fast_api.py)
- [runners.py](file://src/google/adk/runners.py)
- [session.py](file://src/google/adk/sessions/session.py)

**Section sources**
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py)
- [fast_api.py](file://src/google/adk/cli/fast_api.py)

## Core Components
The ADK Development Web Server consists of several core components that work together to provide a robust platform for agent development and testing. The main components include the AdkWebServer class, which manages the FastAPI application and various services, and the FastAPI configuration that handles server initialization and endpoint routing.

**Section sources**
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py)
- [fast_api.py](file://src/google/adk/cli/fast_api.py)

## Architecture Overview
The ADK Development Web Server follows a modular architecture with clear separation of concerns between the web server layer, agent orchestration layer, and data management layer. The server is built on FastAPI, leveraging its asynchronous capabilities for handling concurrent requests and real-time communication.

```mermaid
graph TD
Client[Client Application]
DevUI[Development UI]
subgraph "Web Server Layer"
FastAPI[FastAPI Application]
CORS[CORS Middleware]
StaticFiles[Static Files Server]
end
subgraph "Orchestration Layer"
AdkWebServer[AdkWebServer]
Runner[Runner]
Agent[Agent]
end
subgraph "Data Management Layer"
SessionService[Session Service]
MemoryService[Memory Service]
ArtifactService[Artifact Service]
CredentialService[Credential Service]
end
Client --> FastAPI
DevUI --> FastAPI
FastAPI --> AdkWebServer
AdkWebServer --> Runner
Runner --> Agent
AdkWebServer --> SessionService
AdkWebServer --> MemoryService
AdkWebServer --> ArtifactService
AdkWebServer --> CredentialService
CORS --> FastAPI
StaticFiles --> FastAPI
style FastAPI fill:#4CAF50,stroke:#388E3C
style AdkWebServer fill:#2196F3,stroke:#1976D2
style Runner fill:#FF9800,stroke:#F57C00
style SessionService fill:#9C27B0,stroke:#7B1FA2
```

**Diagram sources**
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py)
- [fast_api.py](file://src/google/adk/cli/fast_api.py)
- [runners.py](file://src/google/adk/runners.py)

## Detailed Component Analysis
This section provides an in-depth analysis of the key components that make up the ADK Development Web Server, focusing on their implementation, interactions, and responsibilities.

### AdkWebServer Analysis
The AdkWebServer class is the central component that orchestrates the web server functionality, managing the FastAPI application and coordinating between various services.

#### Class Diagram
```mermaid
classDiagram
class AdkWebServer {
+agent_loader : BaseAgentLoader
+session_service : BaseSessionService
+memory_service : BaseMemoryService
+artifact_service : BaseArtifactService
+credential_service : BaseCredentialService
+eval_sets_manager : EvalSetsManager
+eval_set_results_manager : EvalSetResultsManager
+agents_dir : str
+runners_to_clean : set[str]
+current_app_name_ref : SharedValue[str]
+runner_dict : dict
+__init__(...)
+get_runner_async(app_name : str) Runner
+get_fast_api_app(...) FastAPI
}
class BaseAgentLoader {
<<interface>>
+load_agent(app_name : str) Agent
+list_agents() list[str]
}
class BaseSessionService {
<<interface>>
+get_session(app_name : str, user_id : str, session_id : str) Session
+list_sessions(app_name : str, user_id : str) list[Session]
+create_session(app_name : str, user_id : str, state : dict, session_id : str) Session
+delete_session(app_name : str, user_id : str, session_id : str) None
+append_event(session : Session, event : Event) None
}
class BaseMemoryService {
<<interface>>
+get_memory_entry(session_id : str, key : str) MemoryEntry
+set_memory_entry(session_id : str, key : str, value : Any) None
}
class BaseArtifactService {
<<interface>>
+save_artifact(app_name : str, user_id : str, session_id : str, filename : str, artifact : Any) None
+load_artifact(app_name : str, user_id : str, session_id : str, filename : str, version : int) Any
+list_artifact_keys(app_name : str, user_id : str, session_id : str) list[str]
+delete_artifact(app_name : str, user_id : str, session_id : str, filename : str) None
}
class BaseCredentialService {
<<interface>>
+get_credentials(user_id : str) Credentials
+save_credentials(user_id : str, credentials : Credentials) None
}
AdkWebServer --> BaseAgentLoader : "uses"
AdkWebServer --> BaseSessionService : "uses"
AdkWebServer --> BaseMemoryService : "uses"
AdkWebServer --> BaseArtifactService : "uses"
AdkWebServer --> BaseCredentialService : "uses"
```

**Diagram sources**
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py)

### FastAPI Configuration Analysis
The FastAPI configuration handles server initialization, endpoint routing, and integration with various services. It provides a flexible interface for customizing server behavior and supports both API endpoints and static file serving.

#### Sequence Diagram
```mermaid
sequenceDiagram
participant Client as "Client"
participant FastAPI as "FastAPI"
participant AdkWebServer as "AdkWebServer"
participant Runner as "Runner"
participant SessionService as "SessionService"
Client->>FastAPI : HTTP Request
FastAPI->>AdkWebServer : Route to appropriate endpoint
AdkWebServer->>SessionService : Get session data
SessionService-->>AdkWebServer : Return session
AdkWebServer->>Runner : Execute agent logic
Runner->>AdkWebServer : Stream events
AdkWebServer->>FastAPI : Format response
FastAPI->>Client : Return response
Note over FastAPI,AdkWebServer : Server processes requests through<br/>a well-defined pipeline
```

**Diagram sources**
- [fast_api.py](file://src/google/adk/cli/fast_api.py)
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py)

### Session Management Analysis
The session management system provides persistent storage for agent interactions, maintaining state across multiple requests and enabling continuity in agent conversations.

#### Flowchart
```mermaid
flowchart TD
Start([Start]) --> CheckSession{"Session exists?"}
CheckSession --> |Yes| LoadSession["Load existing session"]
CheckSession --> |No| CreateSession["Create new session"]
LoadSession --> ProcessRequest["Process request with session context"]
CreateSession --> ProcessRequest
ProcessRequest --> UpdateSession["Update session with new events"]
UpdateSession --> SaveSession["Save session state"]
SaveSession --> End([End])
style Start fill:#4CAF50,stroke:#388E3C
style End fill:#F44336,stroke:#D32F2F
```

**Diagram sources**
- [session.py](file://src/google/adk/sessions/session.py)
- [runners.py](file://src/google/adk/runners.py)

**Section sources**
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py)
- [fast_api.py](file://src/google/adk/cli/fast_api.py)
- [runners.py](file://src/google/adk/runners.py)
- [session.py](file://src/google/adk/sessions/session.py)

## Dependency Analysis
The ADK Development Web Server has a well-defined dependency structure that ensures modularity and separation of concerns. The server depends on various services for agent loading, session management, memory storage, artifact handling, and credential management.

```mermaid
graph TD
adk_web_server --> fast_api
fast_api --> runners
fast_api --> sessions
fast_api --> memory
fast_api --> artifacts
fast_api --> credentials
fast_api --> agents
fast_api --> browser
style adk_web_server fill:#2196F3,stroke:#1976D2
style fast_api fill:#4CAF50,stroke:#388E3C
style runners fill:#FF9800,stroke:#F57C00
style sessions fill:#9C27B0,stroke:#7B1FA2
style memory fill:#00BCD4,stroke:#0097A7
style artifacts fill:#8BC34A,stroke:#689F38
style credentials fill:#FF5722,stroke:#D84315
style agents fill:#673AB7,stroke:#512DA8
style browser fill:#795548,stroke:#5D4037
```

**Diagram sources**
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py)
- [fast_api.py](file://src/google/adk/cli/fast_api.py)

## Performance Considerations
The ADK Development Web Server is designed to handle concurrent sessions and large payloads efficiently. The server leverages FastAPI's asynchronous capabilities to process multiple requests simultaneously without blocking. For handling large payloads, the server implements streaming responses and efficient memory management to minimize resource consumption.

The WebSocket endpoint for bidirectional communication is optimized for real-time streaming of agent responses, with careful management of connection state and message buffering. The server also includes configuration options for tuning performance parameters such as connection timeouts, buffer sizes, and concurrency limits.

**Section sources**
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py)
- [fast_api.py](file://src/google/adk/cli/fast_api.py)

## Troubleshooting Guide
When configuring the ADK Development Web Server, several common issues may arise. Port conflicts can occur when the specified port is already in use by another process; this can be resolved by changing the port number in the server configuration. CORS policies may prevent the development UI from accessing the API endpoints; this can be addressed by configuring the allowed origins in the server settings.

For SSL/TLS setup, ensure that valid certificates are provided and properly configured in the server settings. Issues with agent loading or session management may indicate problems with the agent directory structure or configuration files; verify that the agents directory is correctly specified and that all required configuration files are present.

**Section sources**
- [adk_web_server.py](file://src/google/adk/cli/adk_web_server.py)
- [fast_api.py](file://src/google/adk/cli/fast_api.py)
- [envs.py](file://src/google/adk/cli/utils/envs.py)
- [logs.py](file://src/google/adk/cli/utils/logs.py)

## Conclusion
The ADK Development Web Server provides a comprehensive platform for agent development and testing, with robust support for agent orchestration, session management, and real-time communication. The server's modular architecture and flexible configuration options make it suitable for a wide range of development scenarios, from simple agent testing to complex multi-agent systems.