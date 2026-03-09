# Authentication Schemes

<cite>
**Referenced Files in This Document**
- [auth_schemes.py](file://src/google/adk/auth/auth_schemes.py)
- [oauth2_discovery.py](file://src/google/adk/auth/oauth2_discovery.py)
- [auth_credential.py](file://src/google/adk/auth/auth_credential.py)
- [oauth2_credential_util.py](file://src/google/adk/auth/oauth2_credential_util.py)
- [oauth2_credential_exchanger.py](file://src/google/adk/auth/exchanger/oauth2_credential_exchanger.py)
- [oauth2_credential_refresher.py](file://src/google/adk/auth/refresher/oauth2_credential_refresher.py)
- [oauth2_exchanger.py](file://src/google/adk/tools/openapi_tool/auth/credential_exchangers/oauth2_exchanger.py)
- [__init__.py](file://src/google/adk/auth/__init__.py)
- [agent.py](file://contributing/samples/oauth2_client_credentials/agent.py)
- [main.py](file://contributing/samples/oauth2_client_credentials/main.py)
- [test_oauth2_discovery.py](file://tests/unittests/auth/test_oauth2_discovery.py)
- [test_oauth2_credential_util.py](file://tests/unittests/auth/test_oauth2_credential_util.py)
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
10. [Appendices](#appendices)

## Introduction
This document explains the authentication schemes supported in ADK with a focus on OAuth2, OpenID Connect, and custom schemes. It covers the AuthSchemeType enumeration, the OpenIdConnectWithConfig class, OAuth2 flows (authorization code, implicit, client credentials, and password), the OAuth2 discovery mechanism for dynamic endpoint and scope discovery, validation and error handling, practical configuration examples, environment-specific considerations, and troubleshooting guidance.

## Project Structure
ADK’s authentication capabilities are primarily located under the auth package, with supporting utilities and flows under tools and tests. The key areas include:
- Authentication schemes and types
- OAuth2 discovery and metadata handling
- Credential models and utilities
- Credential exchange and refresh flows
- OpenAPI tool integration for OAuth2/OpenID Connect
- Sample usage for client credentials flow

```mermaid
graph TB
subgraph "Auth Core"
AS["auth_schemes.py"]
AC["auth_credential.py"]
OU["oauth2_credential_util.py"]
EX["oauth2_credential_exchanger.py"]
RF["oauth2_credential_refresher.py"]
OD["oauth2_discovery.py"]
end
subgraph "Tools Integration"
OE["tools/openapi_tool/.../oauth2_exchanger.py"]
end
subgraph "Samples"
SA["samples/oauth2_client_credentials/agent.py"]
SM["samples/oauth2_client_credentials/main.py"]
end
AS --> OU
OU --> EX
OU --> RF
AS --> OE
OD --> OE
SA --> OE
SA --> EX
SM --> SA
```

**Diagram sources**
- [auth_schemes.py](file://src/google/adk/auth/auth_schemes.py#L32-L80)
- [oauth2_discovery.py](file://src/google/adk/auth/oauth2_discovery.py#L52-L149)
- [auth_credential.py](file://src/google/adk/auth/auth_credential.py#L68-L95)
- [oauth2_credential_util.py](file://src/google/adk/auth/oauth2_credential_util.py#L34-L120)
- [oauth2_credential_exchanger.py](file://src/google/adk/auth/exchanger/oauth2_credential_exchanger.py#L47-L212)
- [oauth2_credential_refresher.py](file://src/google/adk/auth/refresher/oauth2_credential_refresher.py#L45-L127)
- [oauth2_exchanger.py](file://src/google/adk/tools/openapi_tool/auth/credential_exchangers/oauth2_exchanger.py#L30-L120)
- [agent.py](file://contributing/samples/oauth2_client_credentials/agent.py#L35-L64)

**Section sources**
- [auth_schemes.py](file://src/google/adk/auth/auth_schemes.py#L32-L80)
- [oauth2_discovery.py](file://src/google/adk/auth/oauth2_discovery.py#L52-L149)
- [auth_credential.py](file://src/google/adk/auth/auth_credential.py#L68-L95)
- [oauth2_credential_util.py](file://src/google/adk/auth/oauth2_credential_util.py#L34-L120)
- [oauth2_credential_exchanger.py](file://src/google/adk/auth/exchanger/oauth2_credential_exchanger.py#L47-L212)
- [oauth2_credential_refresher.py](file://src/google/adk/auth/refresher/oauth2_credential_refresher.py#L45-L127)
- [oauth2_exchanger.py](file://src/google/adk/tools/openapi_tool/auth/credential_exchangers/oauth2_exchanger.py#L30-L120)
- [agent.py](file://contributing/samples/oauth2_client_credentials/agent.py#L35-L64)
- [main.py](file://contributing/samples/oauth2_client_credentials/main.py#L98-L127)

## Core Components
- AuthSchemeType: Re-export of OpenAPI SecuritySchemeType for standardized security scheme classification.
- OpenIdConnectWithConfig: A flattened OpenAPI security scheme tailored for OpenID Connect with explicit endpoints and optional metadata.
- OAuthGrantType: Enumeration of supported OAuth2 flows (client_credentials, authorization_code, implicit, password).
- ExtendedOAuth2: OAuth2 scheme with optional issuer_url to enable auto-discovery.
- OAuth2DiscoveryManager: Discovers authorization server and protected resource metadata via well-known endpoints.
- AuthCredential: Unified credential model supporting HTTP, OAuth2, OpenID Connect, and service accounts.
- OAuth2CredentialExchanger: Exchanges authorization responses into usable access tokens for supported flows.
- OAuth2CredentialRefresher: Refreshes expired tokens when applicable.
- OAuth2CredentialExchanger (OpenAPI tool): Converts credentials into HTTP bearer tokens for outbound requests.

**Section sources**
- [auth_schemes.py](file://src/google/adk/auth/auth_schemes.py#L32-L80)
- [oauth2_discovery.py](file://src/google/adk/auth/oauth2_discovery.py#L52-L149)
- [auth_credential.py](file://src/google/adk/auth/auth_credential.py#L68-L95)
- [oauth2_credential_util.py](file://src/google/adk/auth/oauth2_credential_util.py#L34-L120)
- [oauth2_credential_exchanger.py](file://src/google/adk/auth/exchanger/oauth2_credential_exchanger.py#L47-L212)
- [oauth2_credential_refresher.py](file://src/google/adk/auth/refresher/oauth2_credential_refresher.py#L45-L127)
- [oauth2_exchanger.py](file://src/google/adk/tools/openapi_tool/auth/credential_exchangers/oauth2_exchanger.py#L30-L120)

## Architecture Overview
The authentication architecture integrates scheme definitions, discovery, credential modeling, exchange, and refresh flows. OpenAPI tooling consumes the resulting HTTP bearer tokens for authenticated requests.

```mermaid
sequenceDiagram
participant Dev as "Developer"
participant Tool as "OpenAPI Tool"
participant Ex as "OAuth2CredentialExchanger"
participant Util as "OAuth2CredentialUtil"
participant Ref as "OAuth2CredentialRefresher"
participant Disc as "OAuth2DiscoveryManager"
Dev->>Tool : Configure AuthScheme and AuthCredential
Tool->>Disc : Optional issuer_url discovery
Disc-->>Tool : AuthorizationServerMetadata
Tool->>Ex : exchange_credential(auth_scheme, auth_credential)
Ex->>Util : create_oauth2_session(...)
Util-->>Ex : OAuth2Session, token_endpoint
Ex->>Ex : fetch_token(...) for selected grant
Ex-->>Tool : ExchangeResult(updated credential)
Tool->>Ref : refresh_credential(...) if needed
Ref-->>Tool : AuthCredential (refreshed)
Tool-->>Dev : HTTP Bearer token for requests
```

**Diagram sources**
- [oauth2_exchanger.py](file://src/google/adk/tools/openapi_tool/auth/credential_exchangers/oauth2_exchanger.py#L89-L120)
- [oauth2_credential_exchanger.py](file://src/google/adk/auth/exchanger/oauth2_credential_exchanger.py#L50-L102)
- [oauth2_credential_util.py](file://src/google/adk/auth/oauth2_credential_util.py#L34-L97)
- [oauth2_credential_refresher.py](file://src/google/adk/auth/refresher/oauth2_credential_refresher.py#L77-L126)
- [oauth2_discovery.py](file://src/google/adk/auth/oauth2_discovery.py#L55-L104)

## Detailed Component Analysis

### AuthSchemeType and OpenIdConnectWithConfig
- AuthSchemeType re-exports OpenAPI SecuritySchemeType for consistent classification.
- OpenIdConnectWithConfig extends SecurityBase with:
  - type_: fixed to openIdConnect
  - authorization_endpoint and token_endpoint (required)
  - userinfo_endpoint and revocation_endpoint (optional)
  - token_endpoint_auth_methods_supported, grant_types_supported, scopes (optional)

```mermaid
classDiagram
class SecuritySchemeType {
<<enum>>
}
class OpenIdConnectWithConfig {
+type_ : SecuritySchemeType
+authorization_endpoint : string
+token_endpoint : string
+userinfo_endpoint : string?
+revocation_endpoint : string?
+token_endpoint_auth_methods_supported : list<string>?
+grant_types_supported : list<string>?
+scopes : list<string>?
}
class AuthSchemeType {
<<alias>>
}
OpenIdConnectWithConfig --> SecuritySchemeType : "type_"
AuthSchemeType <.. SecuritySchemeType : "re-export"
```

**Diagram sources**
- [auth_schemes.py](file://src/google/adk/auth/auth_schemes.py#L32-L46)
- [auth_schemes.py](file://src/google/adk/auth/auth_schemes.py#L71-L72)

**Section sources**
- [auth_schemes.py](file://src/google/adk/auth/auth_schemes.py#L32-L46)
- [auth_schemes.py](file://src/google/adk/auth/auth_schemes.py#L71-L72)

### OAuthGrantType and ExtendedOAuth2
- OAuthGrantType enumerates supported flows: client_credentials, authorization_code, implicit, password.
- ExtendedOAuth2 adds issuer_url to support discovery-driven configuration.

```mermaid
classDiagram
class OAuthGrantType {
+CLIENT_CREDENTIALS
+AUTHORIZATION_CODE
+IMPLICIT
+PASSWORD
+from_flow(flow) OAuthGrantType?
}
class ExtendedOAuth2 {
+issuer_url : string?
}
OAuthGrantType <.. ExtendedOAuth2 : "used by flows"
```

**Diagram sources**
- [auth_schemes.py](file://src/google/adk/auth/auth_schemes.py#L49-L68)
- [auth_schemes.py](file://src/google/adk/auth/auth_schemes.py#L75-L80)

**Section sources**
- [auth_schemes.py](file://src/google/adk/auth/auth_schemes.py#L49-L68)
- [auth_schemes.py](file://src/google/adk/auth/auth_schemes.py#L75-L80)

### OAuth2 Discovery Mechanism
OAuth2DiscoveryManager implements RFC8414 and RFC9728 discovery:
- Authorization server metadata discovery via .well-known endpoints with fallbacks and path-aware logic.
- Protected resource metadata discovery via .well-known/oauth-protected-resource.
- Issuer/resource validation to prevent MIX-UP attacks.
- Robust error handling for network failures and malformed responses.

```mermaid
flowchart TD
Start(["discover_auth_server_metadata(issuer_url)"]) --> Parse["Parse URL and split base_url/path"]
Parse --> PathCheck{"Path present?"}
PathCheck --> |Yes| TryPath["Try path-insertion and path-appending endpoints"]
PathCheck --> |No| TryBase["Try base .well-known endpoints"]
TryPath --> Fetch["HTTP GET with timeout"]
TryBase --> Fetch
Fetch --> Status{"HTTP 200 & JSON?"}
Status --> |No| Next["Try next endpoint"]
Next --> Fetch
Status --> |Yes| Validate["Validate issuer matches issuer_url"]
Validate --> Match{"Match?"}
Match --> |No| Warn["Log warning and continue"]
Warn --> Fetch
Match --> |Yes| ReturnMeta["Return AuthorizationServerMetadata"]
ReturnMeta --> End(["Done"])
```

**Diagram sources**
- [oauth2_discovery.py](file://src/google/adk/auth/oauth2_discovery.py#L55-L104)

**Section sources**
- [oauth2_discovery.py](file://src/google/adk/auth/oauth2_discovery.py#L52-L149)
- [test_oauth2_discovery.py](file://tests/unittests/auth/test_oauth2_discovery.py#L27-L285)

### OAuth2 Credential Utilities
- create_oauth2_session builds an Authlib OAuth2Session from:
  - OpenIdConnectWithConfig: uses token_endpoint and scopes
  - OAuth2: selects tokenUrl from authorizationCode or clientCredentials flows
  - Validates presence of client_id and client_secret
- update_credential_with_tokens updates access_token, refresh_token, id_token, expires_at, expires_in

```mermaid
flowchart TD
Start(["create_oauth2_session(auth_scheme, auth_credential)"]) --> TypeCheck{"Scheme type?"}
TypeCheck --> |OpenIdConnectWithConfig| OIDC["Use token_endpoint and scopes"]
TypeCheck --> |OAuth2| FlowSel{"authorizationCode or clientCredentials?"}
FlowSel --> |authorizationCode| AC["Use tokenUrl and scopes"]
FlowSel --> |clientCredentials| CC["Use tokenUrl and scopes"]
FlowSel --> |None| Warn["Log warning and return None"]
OIDC --> CredsCheck{"client_id/client_secret present?"}
AC --> CredsCheck
CC --> CredsCheck
CredsCheck --> |No| Warn
CredsCheck --> |Yes| Build["Build OAuth2Session with client_id, secret, scope, redirect_uri, state, token_endpoint_auth_method"]
Build --> Return(["Return (OAuth2Session, token_endpoint)"])
```

**Diagram sources**
- [oauth2_credential_util.py](file://src/google/adk/auth/oauth2_credential_util.py#L34-L97)

**Section sources**
- [oauth2_credential_util.py](file://src/google/adk/auth/oauth2_credential_util.py#L34-L120)
- [test_oauth2_credential_util.py](file://tests/unittests/auth/test_oauth2_credential_util.py#L64-L139)

### OAuth2 Credential Exchange
- Determines grant type from scheme (OAuth2 flows or OIDC supported grant types).
- Supports client_credentials and authorization_code exchanges.
- Uses create_oauth2_session and update_credential_with_tokens.
- Handles missing authlib gracefully by returning original credential.

```mermaid
sequenceDiagram
participant Tool as "Tool"
participant Ex as "OAuth2CredentialExchanger"
participant Util as "OAuth2CredentialUtil"
Tool->>Ex : exchange(auth_credential, auth_scheme)
Ex->>Ex : _determine_grant_type(auth_scheme)
alt client_credentials
Ex->>Util : create_oauth2_session(...)
Util-->>Ex : OAuth2Session, token_endpoint
Ex->>Ex : fetch_token(grant_type=client_credentials)
Ex->>Util : update_credential_with_tokens(...)
Ex-->>Tool : ExchangeResult(true)
else authorization_code
Ex->>Util : create_oauth2_session(...)
Util-->>Ex : OAuth2Session, token_endpoint
Ex->>Ex : fetch_token(authorization_response, code, client_id)
Ex->>Util : update_credential_with_tokens(...)
Ex-->>Tool : ExchangeResult(true)
else unsupported
Ex-->>Tool : ExchangeResult(false)
end
```

**Diagram sources**
- [oauth2_credential_exchanger.py](file://src/google/adk/auth/exchanger/oauth2_credential_exchanger.py#L50-L102)
- [oauth2_credential_util.py](file://src/google/adk/auth/oauth2_credential_util.py#L34-L97)

**Section sources**
- [oauth2_credential_exchanger.py](file://src/google/adk/auth/exchanger/oauth2_credential_exchanger.py#L47-L212)

### OAuth2 Credential Refresh
- Checks expiration using OAuth2Token.is_expired.
- Refreshes tokens via OAuth2Session.refresh_token when applicable.
- Returns original credential on failure.

```mermaid
flowchart TD
Start(["is_refresh_needed(auth_credential, auth_scheme)"]) --> HasOAuth2{"Has oauth2 fields?"}
HasOAuth2 --> |No| ReturnFalse["Return False"]
HasOAuth2 --> |Yes| Expired{"OAuth2Token.is_expired()?"}
Expired --> |No| ReturnFalse
Expired --> |Yes| Refresh(["refresh(auth_credential, auth_scheme)"])
Refresh --> Session["create_oauth2_session(...)"]
Session --> Token["client.refresh_token(refresh_token)"]
Token --> Update["update_credential_with_tokens(...)"]
Update --> Done(["Return refreshed credential"])
```

**Diagram sources**
- [oauth2_credential_refresher.py](file://src/google/adk/auth/refresher/oauth2_credential_refresher.py#L48-L126)
- [oauth2_credential_util.py](file://src/google/adk/auth/oauth2_credential_util.py#L100-L120)

**Section sources**
- [oauth2_credential_refresher.py](file://src/google/adk/auth/refresher/oauth2_credential_refresher.py#L45-L127)

### OpenAPI Tool OAuth2 Integration
- Validates scheme type (oauth2 or openIdConnect).
- Generates HTTP bearer token from existing access_token.
- Returns original credential if already HTTP bearer or no token available.

```mermaid
flowchart TD
Start(["exchange_credential(auth_scheme, auth_credential)"]) --> Validate["Validate scheme type and credential presence"]
Validate --> AccessToken{"Has access_token?"}
AccessToken --> |No| ReturnOrig["Return original credential"]
AccessToken --> |Yes| BuildBearer["Build HTTP bearer credential"]
BuildBearer --> ReturnNew["Return updated credential"]
```

**Diagram sources**
- [oauth2_exchanger.py](file://src/google/adk/tools/openapi_tool/auth/credential_exchangers/oauth2_exchanger.py#L89-L120)

**Section sources**
- [oauth2_exchanger.py](file://src/google/adk/tools/openapi_tool/auth/credential_exchangers/oauth2_exchanger.py#L30-L120)

### Practical Configuration Examples
- Client Credentials Flow (sample):
  - Define OAuth2 scheme with clientCredentials flow and tokenUrl/scopes.
  - Provide client_id and client_secret in AuthCredential.
  - Use AuthenticatedFunctionTool to invoke APIs with automatic bearer token injection.

```mermaid
sequenceDiagram
participant Sample as "Sample Agent"
participant Tool as "AuthenticatedFunctionTool"
participant Ex as "OAuth2CredentialExchanger"
participant Util as "OAuth2CredentialUtil"
Sample->>Tool : create_auth_config() defines OAuth2(clientCredentials)
Sample->>Tool : AuthConfig(raw_auth_credential with client_id/secret)
Tool->>Ex : exchange_credential(...)
Ex->>Util : create_oauth2_session(...)
Util-->>Ex : OAuth2Session, token_endpoint
Ex->>Ex : fetch_token(grant_type=client_credentials)
Ex-->>Tool : ExchangeResult with access_token
Tool-->>Sample : Bearer token for API calls
```

**Diagram sources**
- [agent.py](file://contributing/samples/oauth2_client_credentials/agent.py#L35-L64)
- [oauth2_credential_exchanger.py](file://src/google/adk/auth/exchanger/oauth2_credential_exchanger.py#L130-L163)
- [oauth2_credential_util.py](file://src/google/adk/auth/oauth2_credential_util.py#L34-L97)

**Section sources**
- [agent.py](file://contributing/samples/oauth2_client_credentials/agent.py#L35-L64)
- [main.py](file://contributing/samples/oauth2_client_credentials/main.py#L98-L127)

## Dependency Analysis
- auth_schemes.py defines the foundational scheme types and grant enumeration.
- oauth2_credential_util.py depends on Authlib OAuth2Session and FastAPI OAuth2 models.
- oauth2_credential_exchanger.py orchestrates exchange logic and delegates to utilities.
- oauth2_credential_refresher.py depends on OAuth2Token and Google credentials for refresh checks.
- oauth2_discovery.py provides asynchronous discovery with robust error handling.
- oauth2_exchanger.py (OpenAPI tool) depends on auth_credential models and scheme types.

```mermaid
graph LR
AS["auth_schemes.py"] --> OU["oauth2_credential_util.py"]
OU --> EX["oauth2_credential_exchanger.py"]
OU --> RF["oauth2_credential_refresher.py"]
AS --> OE["tools/.../oauth2_exchanger.py"]
OD["oauth2_discovery.py"] --> OE
AC["auth_credential.py"] --> OU
AC --> EX
AC --> RF
```

**Diagram sources**
- [auth_schemes.py](file://src/google/adk/auth/auth_schemes.py#L32-L80)
- [oauth2_credential_util.py](file://src/google/adk/auth/oauth2_credential_util.py#L34-L120)
- [oauth2_credential_exchanger.py](file://src/google/adk/auth/exchanger/oauth2_credential_exchanger.py#L47-L212)
- [oauth2_credential_refresher.py](file://src/google/adk/auth/refresher/oauth2_credential_refresher.py#L45-L127)
- [oauth2_discovery.py](file://src/google/adk/auth/oauth2_discovery.py#L52-L149)
- [oauth2_exchanger.py](file://src/google/adk/tools/openapi_tool/auth/credential_exchangers/oauth2_exchanger.py#L30-L120)
- [auth_credential.py](file://src/google/adk/auth/auth_credential.py#L68-L95)

**Section sources**
- [__init__.py](file://src/google/adk/auth/__init__.py#L15-L23)

## Performance Considerations
- Discovery uses asynchronous HTTP requests with timeouts; configure issuer_url carefully to minimize retries.
- Token operations rely on Authlib; ensure client_id/client_secret are provided to avoid repeated session creation failures.
- Refresh checks use token expiration; avoid unnecessary refresh calls by leveraging cached credentials.
- Prefer client_credentials for machine-to-machine scenarios to reduce latency compared to authorization_code flows.

## Troubleshooting Guide
Common issues and resolutions:
- Missing authlib:
  - Symptom: Exchange returns original credential without exchange.
  - Resolution: Install Authlib or handle exchange externally.
- Unsupported grant type:
  - Symptom: ExchangeResult indicates no exchange performed.
  - Resolution: Ensure scheme supports client_credentials or authorization_code.
- Invalid or missing endpoints:
  - Symptom: Session creation returns None.
  - Resolution: Verify token_endpoint or flows.authorizationCode.tokenUrl are present.
- Discovery failures:
  - Symptom: No metadata discovered.
  - Resolution: Confirm issuer_url correctness, network connectivity, and well-known endpoint availability.
- Mismatched issuer/resource:
  - Symptom: Discovery logs warnings and returns None.
  - Resolution: Ensure issuer/resource matches the discovered metadata.

**Section sources**
- [oauth2_credential_exchanger.py](file://src/google/adk/auth/exchanger/oauth2_credential_exchanger.py#L76-L84)
- [oauth2_credential_exchanger.py](file://src/google/adk/auth/exchanger/oauth2_credential_exchanger.py#L100-L102)
- [oauth2_credential_util.py](file://src/google/adk/auth/oauth2_credential_util.py#L75-L77)
- [oauth2_discovery.py](file://src/google/adk/auth/oauth2_discovery.py#L91-L100)
- [oauth2_discovery.py](file://src/google/adk/auth/oauth2_discovery.py#L130-L138)
- [test_oauth2_discovery.py](file://tests/unittests/auth/test_oauth2_discovery.py#L181-L209)

## Conclusion
ADK provides a comprehensive, extensible authentication framework supporting OAuth2 and OpenID Connect with dynamic discovery, robust credential exchange and refresh, and seamless integration with OpenAPI tools. By leveraging the provided schemes, utilities, and flows, developers can configure secure and portable authentication across diverse environments and service providers.

## Appendices
- Supported authentication methods summary:
  - OAuth2 flows: client_credentials, authorization_code, implicit, password
  - OpenID Connect: via OpenIdConnectWithConfig and discovery-managed endpoints
  - Custom schemes: Any OpenAPI-compatible SecuritySchemeType via AuthSchemeType