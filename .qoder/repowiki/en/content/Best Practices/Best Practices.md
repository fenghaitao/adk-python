# Best Practices

<cite>
**Referenced Files in This Document**   
- [README.md](file://README.md)
- [CONTRIBUTING.md](file://CONTRIBUTING.md)
- [src\google\adk\__init__.py](file://src\google\adk\__init__.py)
- [src\google\adk\agents\base_agent.py](file://src\google\adk\agents\base_agent.py)
- [src\google\adk\agents\llm_agent.py](file://src\google\adk\agents\llm_agent.py)
- [src\google\adk\runners.py](file://src\google\adk\runners.py)
- [src\google\adk\tools\base_tool.py](file://src\google\adk\tools\base_tool.py)
- [src\google\adk\models\base_llm.py](file://src\google\adk\models\base_llm.py)
- [contributing\samples\adk_answering_agent\agent.py](file://contributing\samples\adk_answering_agent\agent.py)
- [contributing\samples\hello_world\agent.py](file://contributing\samples\hello_world\agent.py)
- [contributing\samples\bigquery\agent.py](file://contributing\samples\bigquery\agent.py)
- [tests\unittests\agents\test_base_agent.py](file://tests\unittests\agents\test_base_agent.py)
- [tests\integration\test_single_agent.py](file://tests\integration\test_single_agent.py)
- [src\google\adk\evaluation\agent_evaluator.py](file://src\google\adk\evaluation\agent_evaluator.py)
- [src\google\adk\telemetry.py](file://src\google\adk\telemetry.py)
- [contributing\samples\context_management\advanced_context_manager.py](file://contributing\samples\context_management\advanced_context_manager.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Design Patterns for Maintainable and Scalable Agents](#design-patterns-for-maintainable-and-scalable-agents)
3. [Performance Optimization](#performance-optimization)
4. [Security Considerations](#security-considerations)
5. [Testing Strategies](#testing-strategies)
6. [Error Handling](#error-handling)
7. [Monitoring and Observability](#monitoring-and-observability)
8. [Cost Optimization](#cost-optimization)
9. [Real-World Implementation Examples](#real-world-implementation-examples)
10. [Conclusion](#conclusion)

## Introduction
The Agent Development Kit (ADK) is a flexible and modular framework designed to simplify the development, evaluation, and deployment of sophisticated AI agents. Optimized for Gemini and the Google ecosystem while remaining model-agnostic and deployment-agnostic, ADK enables developers to build agentic architectures ranging from simple tasks to complex workflows. This document provides comprehensive best practices for optimizing agent development and deployment with the ADK framework, covering design patterns, performance optimization, security, testing, error handling, monitoring, and cost optimization. The guidance is derived from the analysis of the ADK codebase, sample implementations, and contributing guidelines, ensuring practical and proven approaches for building robust agent systems.

## Design Patterns for Maintainable and Scalable Agents
Building maintainable and scalable agent systems with the ADK framework involves leveraging its modular architecture and hierarchical agent composition. The framework's design patterns promote code reusability, separation of concerns, and flexible orchestration of complex workflows.

### Hierarchical Agent Composition
The ADK framework supports a hierarchical agent composition pattern, where a parent agent can coordinate multiple specialized sub-agents. This pattern enables the creation of scalable applications by decomposing complex tasks into manageable components. The parent agent, often referred to as a coordinator, delegates tasks to sub-agents based on their capabilities and the current context. This approach is exemplified in the framework's API, where a coordinator agent can be defined with greeter and task executor sub-agents, allowing the ADK engine and the model to guide the agents in working together to accomplish a task. This hierarchical structure not only enhances scalability but also improves maintainability by isolating agent logic and responsibilities.

### Modular Multi-Agent Systems
The modular multi-agent system pattern is a cornerstone of the ADK framework, allowing developers to design applications by composing multiple specialized agents into flexible hierarchies. Each agent in the system is responsible for a specific domain or task, such as handling user greetings, executing specific functions, or managing data retrieval. This modularity enables developers to update or replace individual agents without affecting the entire system, promoting code reusability and reducing the risk of introducing bugs. The framework's support for agent cloning and configuration further enhances this pattern, allowing for the creation of agent instances with identical configurations but different names, which can be added to the agent tree as needed.

### Code-First Development
The ADK framework emphasizes a code-first development approach, where agent logic, tools, and orchestration are defined directly in Python. This approach provides ultimate flexibility, testability, and versioning, making it easier for developers to create, deploy, and maintain agent systems. By defining agents in code, developers can leverage the full power of the Python programming language, including object-oriented programming, functional programming, and advanced data structures. This approach also facilitates integration with existing development workflows and tools, such as version control systems, testing frameworks, and continuous integration/continuous deployment (CI/CD) pipelines.

### Agent Configuration and Cloning
The ADK framework provides mechanisms for agent configuration and cloning, which are essential for building maintainable and scalable agent systems. The `clone` method allows developers to create copies of agent instances with identical configurations, enabling the reuse of agent logic across different parts of the application. This is particularly useful in scenarios where multiple instances of the same agent type are needed, such as in a multi-agent system where each agent has a unique name but shares the same underlying logic. The framework also supports agent configuration through YAML files, allowing developers to define agent properties and behaviors without writing code, which can be particularly useful for non-technical stakeholders.

**Section sources**
- [README.md](file://README.md#L88-L125)
- [src\google\adk\agents\base_agent.py](file://src\google\adk\agents\base_agent.py#L151-L211)

## Performance Optimization
Optimizing the performance of agent systems built with the ADK framework involves reducing latency, improving throughput, and ensuring efficient resource utilization. The framework provides several features and best practices that can be leveraged to achieve these goals.

### Efficient Context Management
Efficient context management is critical for maintaining high performance in agent systems, especially when dealing with long conversations or complex workflows. The ADK framework supports advanced context management techniques, such as intelligent context window management, which can help reduce the amount of data that needs to be processed by the LLM. By summarizing and condensing conversation history, the framework can significantly reduce the token count of the input, leading to faster processing times and lower costs. This is particularly important in scenarios where the conversation history grows large, as it prevents the system from exceeding the context window limits of the LLM.

### Parallel Function Calling
The ADK framework supports parallel function calling, allowing agents to execute multiple tools in parallel within a single request and round. This feature can significantly improve throughput by reducing the number of round trips between the agent and the LLM. For example, an agent can be instructed to roll a die and check prime numbers in parallel, rather than sequentially, which can lead to faster response times and a more efficient use of resources. This pattern is particularly useful in scenarios where multiple independent tasks need to be executed, such as retrieving data from different sources or performing multiple calculations.

### Model and Tool Optimization
Optimizing the choice of LLM and tools is another key aspect of performance optimization in the ADK framework. Developers should carefully select the LLM based on the specific requirements of their application, considering factors such as speed, accuracy, and cost. The framework supports a variety of LLMs, including Gemini and other models, allowing developers to choose the best fit for their use case. Additionally, developers should optimize the use of tools by ensuring that they are only called when necessary and that their parameters are properly configured to minimize processing time and resource usage.

### Caching and State Management
Caching and state management are essential for improving the performance of agent systems. The ADK framework provides mechanisms for storing and retrieving session state, which can be used to cache the results of expensive operations, such as database queries or API calls. By storing the results of these operations in the session state, the framework can avoid redundant processing and reduce latency. Additionally, the framework supports the use of memory services, such as in-memory memory service and Vertex AI memory bank service, which can be used to store and retrieve data across multiple agent invocations, further improving performance.

**Section sources**
- [contributing\samples\context_management\advanced_context_manager.py](file://contributing\samples\context_management\advanced_context_manager.py#L1-L407)
- [contributing\samples\hello_world\agent.py](file://contributing\samples\hello_world\agent.py#L74-L88)

## Security Considerations
Security is a critical aspect of agent development and deployment, and the ADK framework provides several features and best practices to protect against common threats such as prompt injection, unauthorized tool access, and data leakage.

### Prompt Injection Protection
Prompt injection is a significant security risk in agent systems, where malicious inputs can be used to manipulate the behavior of the LLM. The ADK framework mitigates this risk by providing a structured approach to defining agent instructions and system prompts. Developers should ensure that agent instructions are clear, specific, and focused on the intended behavior, avoiding ambiguous or open-ended prompts that could be exploited. Additionally, the framework supports the use of safety settings, such as HarmBlockThreshold, which can be configured to block or filter out harmful content. For example, in the hello_world agent, the safety settings are configured to avoid false alarms about rolling dice, demonstrating how developers can fine-tune these settings to balance security and functionality.

### Unauthorized Tool Access
Unauthorized tool access is another critical security concern, as it can lead to data breaches or other malicious activities. The ADK framework addresses this issue by providing a robust tool management system that allows developers to define and control the tools available to each agent. Developers should carefully configure the tools available to each agent, ensuring that they have only the permissions necessary to perform their intended tasks. For example, in the bigquery agent, the write mode is set to allowed, but in production, it may be more appropriate to change this to blocked or protected to prevent unauthorized writes. Additionally, the framework supports the use of authentication and authorization mechanisms, such as OAuth2, to ensure that only authorized users can access sensitive tools and data.

### Data Leakage Prevention
Data leakage is a significant risk in agent systems, particularly when dealing with sensitive or confidential information. The ADK framework provides several features to help prevent data leakage, including the use of secure data storage and transmission mechanisms. Developers should ensure that sensitive data is encrypted both at rest and in transit, using industry-standard encryption protocols. Additionally, the framework supports the use of artifact services, such as GCS artifact service, which can be used to securely store and manage data. Developers should also implement proper access controls and audit logging to monitor and track data access and usage, helping to detect and prevent unauthorized access.

### Secure Authentication and Authorization
Secure authentication and authorization are essential for protecting agent systems from unauthorized access. The ADK framework supports a variety of authentication and authorization mechanisms, including OAuth2 and service account credentials. Developers should use these mechanisms to ensure that only authorized users and agents can access the system. For example, in the bigquery agent, OAuth2 credentials are used to authenticate the agent and grant it access to the BigQuery service. Additionally, the framework supports the use of credential services, such as in-memory credential service and session state credential service, which can be used to manage and store credentials securely.

**Section sources**
- [contributing\samples\bigquery\agent.py](file://contributing\samples\bigquery\agent.py#L29-L33)
- [contributing\samples\hello_world\agent.py](file://contributing\samples\hello_world\agent.py#L100-L106)

## Testing Strategies
Effective testing is essential for ensuring the reliability and correctness of agent systems built with the ADK framework. The framework provides several tools and best practices for unit testing, integration testing, and end-to-end evaluation.

### Unit Testing
Unit testing is a critical component of the testing strategy for agent systems, as it allows developers to verify the correctness of individual agent components and functions. The ADK framework supports unit testing through the use of the pytest framework, which provides a comprehensive set of tools for writing and running tests. Developers should write unit tests for all agent components, including agent logic, tools, and callbacks, to ensure that they behave as expected. The framework's support for mocking and fixtures makes it easy to isolate and test individual components, reducing the risk of introducing bugs. For example, the test_base_agent.py file contains a suite of unit tests for the BaseAgent class, covering various scenarios such as agent name validation, callback execution, and sub-agent management.

### Integration Testing
Integration testing is essential for verifying the correctness of the interactions between different components of the agent system. The ADK framework supports integration testing through the use of the InMemoryRunner and other testing utilities, which allow developers to simulate the execution of agent workflows in a controlled environment. Developers should write integration tests for all agent workflows, ensuring that the agents work together as expected and that the system behaves correctly under various conditions. The framework's support for session management and state tracking makes it easy to test complex workflows involving multiple agents and tools. For example, the test_single_agent.py file contains an integration test for a single agent, demonstrating how developers can use the AgentEvaluator to evaluate the performance of an agent against a test dataset.

### End-to-End Evaluation
End-to-end evaluation is a comprehensive testing approach that involves testing the entire agent system from start to finish, simulating real-world usage scenarios. The ADK framework provides the AgentEvaluator class, which can be used to perform end-to-end evaluations of agent systems. Developers should use the AgentEvaluator to evaluate the performance of their agents against a variety of test cases, ensuring that the system behaves correctly and meets the desired performance and accuracy requirements. The framework's support for evaluation metrics, such as tool trajectory score and response match score, makes it easy to measure and compare the performance of different agents. Additionally, the framework supports the use of test_config.json files to define evaluation criteria, allowing developers to customize the evaluation process to meet their specific needs.

### Automated Testing and CI/CD
Automated testing and continuous integration/continuous deployment (CI/CD) are essential for maintaining the quality and reliability of agent systems. The ADK framework supports automated testing through the use of GitHub Actions and other CI/CD tools, which can be used to automatically run tests and deploy agents whenever changes are made to the codebase. Developers should set up automated testing and CI/CD pipelines to ensure that all changes are thoroughly tested before being deployed to production. This helps to catch bugs early and reduce the risk of introducing regressions. The framework's support for unit testing, integration testing, and end-to-end evaluation makes it easy to integrate these testing practices into a CI/CD pipeline.

**Section sources**
- [tests\unittests\agents\test_base_agent.py](file://tests\unittests\agents\test_base_agent.py#L1-L800)
- [tests\integration\test_single_agent.py](file://tests\integration\test_single_agent.py#L1-L26)
- [src\google\adk\evaluation\agent_evaluator.py](file://src\google\adk\evaluation\agent_evaluator.py#L1-L661)

## Error Handling
Effective error handling is essential for building robust and reliable agent systems. The ADK framework provides several mechanisms for handling errors and ensuring graceful degradation in the event of failures.

### Graceful Degradation
Graceful degradation is a key principle of error handling in agent systems, where the system continues to function, albeit with reduced capabilities, in the event of a failure. The ADK framework supports graceful degradation through the use of callbacks and error handling mechanisms. For example, the before_agent_callback and after_agent_callback can be used to intercept and handle errors before and after the agent run, allowing the system to provide meaningful feedback to the user and take corrective actions. Additionally, the framework supports the use of fallback mechanisms, such as the _create_fallback_summary function in the advanced_context_manager.py file, which can be used to provide a simplified summary when the LLM summarization fails.

### Meaningful User Feedback
Providing meaningful user feedback is essential for maintaining a positive user experience, even in the event of errors. The ADK framework supports the use of callbacks to generate user-friendly error messages and explanations. For example, in the test_base_agent.py file, the after_agent_callback_append_reply function is used to append a user-friendly message to the agent response when an error occurs. This approach helps to keep the user informed and engaged, reducing frustration and improving the overall user experience. Additionally, the framework supports the use of state tracking and logging, which can be used to provide detailed information about the error and its context, helping users to understand what went wrong and how to resolve it.

### Error Recovery and Retry Mechanisms
Error recovery and retry mechanisms are essential for ensuring the reliability and availability of agent systems. The ADK framework supports the use of retry mechanisms, such as the asyncio.wait_for function in the runners.py file, which can be used to add timeout protection to toolset cleanup operations. This helps to prevent the system from getting stuck in a failed state and ensures that it can recover from transient errors. Additionally, the framework supports the use of error handling patterns, such as try-except blocks, which can be used to catch and handle specific types of errors, allowing the system to take appropriate corrective actions. For example, in the runners.py file, the _cleanup_toolsets function includes error handling for timeout and other exceptions, ensuring that the system can gracefully handle failures during cleanup.

### Logging and Monitoring
Logging and monitoring are essential for detecting and diagnosing errors in agent systems. The ADK framework provides comprehensive logging and monitoring capabilities, including the use of OpenTelemetry for tracing and logging. Developers should use these capabilities to log important events and errors, providing a detailed record of the system's behavior. This information can be used to identify and diagnose issues, as well as to improve the system's performance and reliability over time. Additionally, the framework supports the use of telemetry, which can be used to monitor the system's performance and health in real-time, allowing developers to detect and respond to issues quickly.

**Section sources**
- [contributing\samples\context_management\advanced_context_manager.py](file://contributing\samples\context_management\advanced_context_manager.py#L205-L207)
- [src\google\adk\runners.py](file://src\google\adk\runners.py#L625-L635)

## Monitoring and Observability
Monitoring and observability are critical for maintaining the health and performance of agent systems in production. The ADK framework provides several features and best practices for monitoring and observability, enabling developers to gain insights into the system's behavior and performance.

### Telemetry and Tracing
Telemetry and tracing are essential for monitoring the performance and health of agent systems. The ADK framework supports the use of OpenTelemetry for tracing and logging, providing a comprehensive set of tools for monitoring the system's behavior. Developers should use these capabilities to trace the execution of agent workflows, capturing detailed information about the LLM requests, responses, and tool calls. This information can be used to identify performance bottlenecks, diagnose issues, and optimize the system's performance. For example, the telemetry.py file contains functions for tracing tool calls, LLM requests, and data sending, providing a detailed view of the system's behavior.

### Performance Metrics
Performance metrics are essential for measuring and monitoring the performance of agent systems. The ADK framework supports the use of various performance metrics, such as token usage, response time, and throughput, which can be used to evaluate the system's performance and identify areas for improvement. Developers should use these metrics to monitor the system's performance over time, setting up alerts and notifications to detect and respond to issues quickly. Additionally, the framework supports the use of evaluation metrics, such as tool trajectory score and response match score, which can be used to measure the accuracy and effectiveness of the agents.

### Logging and Auditing
Logging and auditing are essential for maintaining the security and compliance of agent systems. The ADK framework provides comprehensive logging and auditing capabilities, allowing developers to log important events and actions, such as user interactions, tool calls, and data access. This information can be used to detect and prevent unauthorized access, as well as to comply with regulatory requirements. Developers should use these capabilities to log all relevant events and actions, ensuring that they have a complete and accurate record of the system's behavior. Additionally, the framework supports the use of audit logging, which can be used to track changes to the system's configuration and state, helping to ensure the integrity and security of the system.

### Real-Time Monitoring
Real-time monitoring is essential for detecting and responding to issues in agent systems. The ADK framework supports the use of real-time monitoring tools, such as the development UI, which can be used to monitor the system's behavior in real-time. Developers should use these tools to monitor the system's performance and health, setting up alerts and notifications to detect and respond to issues quickly. Additionally, the framework supports the use of monitoring dashboards, which can be used to visualize the system's performance and health, providing a comprehensive view of the system's behavior.

**Section sources**
- [src\google\adk\telemetry.py](file://src\google\adk\telemetry.py#L1-L289)

## Cost Optimization
Cost optimization is a critical consideration for deploying agent systems in production, as the costs of LLM usage and cloud resources can quickly add up. The ADK framework provides several features and best practices for cost optimization, enabling developers to build efficient and cost-effective agent systems.

### LLM Usage Optimization
Optimizing LLM usage is essential for reducing costs in agent systems. The ADK framework supports the use of various LLMs, including Gemini and other models, allowing developers to choose the most cost-effective option for their use case. Developers should carefully select the LLM based on the specific requirements of their application, considering factors such as speed, accuracy, and cost. Additionally, the framework supports the use of model configuration options, such as temperature and max_output_tokens, which can be used to fine-tune the LLM's behavior and reduce costs. For example, in the hello_world agent, the generate_content_config is used to configure the safety settings, demonstrating how developers can optimize the LLM's behavior to reduce costs.

### Cloud Resource Optimization
Optimizing cloud resource usage is another key aspect of cost optimization in agent systems. The ADK framework supports deployment on various cloud platforms, including Cloud Run and Vertex AI Agent Engine, allowing developers to choose the most cost-effective option for their use case. Developers should carefully configure the cloud resources, such as CPU, memory, and storage, to ensure that they are using the minimum necessary resources to meet their performance requirements. Additionally, the framework supports the use of auto-scaling and load balancing, which can be used to dynamically adjust the resources based on the workload, further reducing costs.

### Caching and Data Management
Caching and data management are essential for reducing costs in agent systems. The ADK framework supports the use of caching mechanisms, such as in-memory artifact service and GCS artifact service, which can be used to cache the results of expensive operations, such as database queries or API calls. By storing the results of these operations in the cache, the framework can avoid redundant processing and reduce costs. Additionally, the framework supports the use of data management tools, such as Vertex AI memory bank service, which can be used to store and retrieve data efficiently, further reducing costs.

### Efficient Tool Usage
Efficient tool usage is another key aspect of cost optimization in agent systems. The ADK framework supports the use of various tools, such as Google Search, BigQuery, and code execution, which can be used to perform specific tasks. Developers should carefully configure the tools to ensure that they are only called when necessary and that their parameters are properly configured to minimize processing time and resource usage. Additionally, the framework supports the use of parallel function calling, which can be used to execute multiple tools in parallel, reducing the number of round trips and improving efficiency.

**Section sources**
- [contributing\samples\hello_world\agent.py](file://contributing\samples\hello_world\agent.py#L100-L107)
- [src\google\adk\runners.py](file://src\google\adk\runners.py#L38-L50)

## Real-World Implementation Examples
The ADK framework has been used to build a variety of real-world agent systems, demonstrating its versatility and effectiveness in different domains. These examples provide valuable insights into the practical application of the best practices discussed in this document.

### ADK Answering Agent
The ADK answering agent is a real-world example of an agent system built with the ADK framework. This agent is designed to answer questions about the ADK repository, using a combination of tools such as Vertex AI Search Tool and Agent Tool to retrieve and process information. The agent is configured with a detailed instruction that guides its behavior, ensuring that it provides accurate and relevant responses. The agent also uses a combination of tools to handle different types of queries, such as retrieving discussion details and adding comments to discussions. This example demonstrates how the ADK framework can be used to build a sophisticated agent system that integrates multiple tools and services to provide a comprehensive solution.

### Hello World Agent
The hello world agent is a simple example of an agent system built with the ADK framework. This agent is designed to roll a die and check prime numbers, demonstrating the basic capabilities of the framework. The agent is configured with a simple instruction and a set of tools, such as roll_die and check_prime, which are used to perform the required tasks. The agent also uses the generate_content_config to configure the safety settings, ensuring that it can handle queries about rolling dice without triggering false alarms. This example demonstrates how the ADK framework can be used to build a simple agent system that performs specific tasks, providing a foundation for more complex applications.

### BigQuery Agent
The BigQuery agent is a real-world example of an agent system built with the ADK framework. This agent is designed to answer questions about BigQuery data and models, using a combination of tools such as BigQueryToolset to execute SQL queries. The agent is configured with a detailed instruction that guides its behavior, ensuring that it provides accurate and relevant responses. The agent also uses a combination of tools to handle different types of queries, such as retrieving data and executing SQL queries. This example demonstrates how the ADK framework can be used to build a sophisticated agent system that integrates with external services and databases to provide a comprehensive solution.

### Context Management Agent
The context management agent is a real-world example of an agent system built with the ADK framework. This agent is designed to manage the context of long conversations, using advanced techniques such as intelligent context window management to reduce the token count of the input. The agent is configured with a detailed instruction that guides its behavior, ensuring that it can handle long conversations without exceeding the context window limits of the LLM. The agent also uses a combination of tools to handle different types of queries, such as summarizing conversation history and storing summaries in memory. This example demonstrates how the ADK framework can be used to build a sophisticated agent system that manages complex workflows and maintains continuity across multiple interactions.

**Section sources**
- [contributing\samples\adk_answering_agent\agent.py](file://contributing\samples\adk_answering_agent\agent.py#L1-L88)
- [contributing\samples\hello_world\agent.py](file://contributing\samples\hello_world\agent.py#L1-L109)
- [contributing\samples\bigquery\agent.py](file://contributing\samples\bigquery\agent.py#L1-L78)
- [contributing\samples\context_management\advanced_context_manager.py](file://contributing\samples\context_management\advanced_context_manager.py#L1-L407)

## Conclusion
The Agent Development Kit (ADK) framework provides a powerful and flexible platform for building, evaluating, and deploying sophisticated AI agents. By following the best practices outlined in this document, developers can create maintainable, scalable, and secure agent systems that deliver high performance and value. The framework's support for hierarchical agent composition, modular multi-agent systems, and code-first development enables developers to build complex workflows with ease. Additionally, the framework's comprehensive testing, error handling, monitoring, and cost optimization features ensure that agent systems are reliable, efficient, and cost-effective. The real-world examples provided in this document demonstrate the practical application of these best practices, offering valuable insights into the successful implementation of agent systems with the ADK framework. By leveraging these best practices, developers can unlock the full potential of the ADK framework and build agent systems that meet the needs of their users and organizations.