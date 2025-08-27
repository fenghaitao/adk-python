# Multi-Agent Development Workflow with MCP Server Integration

## 🚀 Overview

This example demonstrates a sophisticated **multi-agent development system** that integrates with **MCP (Model Context Protocol) servers** to handle the complete software development lifecycle with enhanced capabilities.

## 🏗️ System Architecture

### **6 Specialized Agents with MCP Integration:**

1. **📚 MCP Spec Reader Agent** - Analyzes specifications using MCP file operations
2. **💻 MCP Code Generator Agent** - Creates code with MCP development tools
3. **🧪 MCP Test Generator Agent** - Generates tests using MCP testing frameworks
4. **🔨 MCP Build Agent** - Builds projects with MCP build tools
5. **✅ MCP Test Runner Agent** - Executes tests with MCP test runners
6. **📝 MCP Git Agent** - Manages version control with MCP git operations

### **3 MCP Servers Providing Enhanced Capabilities:**

- **MCP Filesystem Server**: Enhanced file operations with validation and security
- **MCP Build Server**: Advanced build tools with timeout protection and quality checks
- **MCP Git Server**: Professional version control with automated workflows

## 🔧 MCP Server Capabilities

### **MCP Filesystem Server**
```python
# Enhanced file operations
- Robust file reading with size limits and encoding detection
- Safe file writing with directory creation and validation
- Directory listing with metadata extraction
- Path validation and access control
- Advanced error handling and recovery
```

### **MCP Build Server**
```python
# Advanced build operations
- Command execution with timeout protection
- Dependency installation and management
- Code quality checks (mypy, black, isort, flake8)
- Test execution with coverage analysis
- Build artifact generation and validation
```

### **MCP Git Server**
```python
# Professional version control
- Repository initialization and configuration
- Intelligent commit message generation
- Branch management and merging strategies
- Automated .gitignore creation
- Repository analysis and reporting
```

## 🚀 How to Use

### **Method 1: Interactive CLI**
```bash
cd mcp_dev_workflow
adk run .

# Example interactions:
"Create a Python calculator with MCP-enhanced development workflow including 
comprehensive testing, code quality checks, and professional git management."
```

### **Method 2: Demo Script**
```bash
cd mcp_dev_workflow
python demo.py

# Choose from scenarios:
# 1. Simple Calculator with MCP
# 2. Web API with MCP Enhancement
# 3. CLI Tool with MCP Workflow
# 4. Data Processing Pipeline with MCP
```

### **Method 3: Web Interface**
```bash
cd mcp_dev_workflow
adk web . --port 8080
# Access enhanced development workflow through web UI
```

## 📋 Key Features

### **Enhanced File Operations**
- **Secure File Access**: Path validation and access control
- **Robust Error Handling**: Comprehensive error recovery and reporting
- **Metadata Extraction**: File size, encoding, and modification tracking
- **Performance Optimization**: Streaming and caching for large files

### **Advanced Build Capabilities**
- **Timeout Protection**: Prevents hanging build processes
- **Quality Assurance**: Automated code formatting and type checking
- **Dependency Management**: Intelligent package installation and validation
- **Coverage Analysis**: Comprehensive test coverage reporting

### **Professional Version Control**
- **Automated Workflows**: Intelligent git operation sequences
- **Commit Standards**: Professional commit message generation
- **Repository Setup**: Automated .gitignore and configuration
- **Branch Management**: Safe branching and merging operations

### **Multi-Agent Coordination**
- **Workflow Orchestration**: Seamless coordination between MCP-enhanced agents
- **State Management**: Persistent workflow state across agent interactions
- **Error Recovery**: Robust error handling and recovery mechanisms
- **Progress Tracking**: Real-time workflow progress and status updates

## 🔄 Workflow Examples

### **Calculator Development with MCP**
```
User Request: "Create a Python calculator with comprehensive testing"

MCP Workflow:
1. MCP Spec Reader → Uses MCP file operations to read specification
2. MCP Code Generator → Creates calculator.py with MCP file validation
3. MCP Test Generator → Generates test_calculator.py with MCP testing tools
4. MCP Build Agent → Runs quality checks with MCP build server
5. MCP Test Runner → Executes tests with MCP test execution
6. MCP Git Agent → Commits code with MCP git operations

Result: Professional calculator with 95%+ test coverage, formatted code, and git history
```

### **Web API Development with MCP**
```
User Request: "Build a FastAPI service with authentication and database"

MCP Enhanced Process:
1. Specification analysis with MCP file operations
2. API code generation with MCP development tools
3. Comprehensive test suite with MCP testing frameworks
4. Database migration testing with MCP build tools
5. Security testing with MCP test runners
6. Professional git workflow with MCP version control

Result: Production-ready API with comprehensive testing and documentation
```

## 🛠️ MCP Server Configuration

### **Filesystem Server Setup**
```python
filesystem_config = {
    "allowed_directories": ["/project", "/workspace"],
    "max_file_size": "10MB",
    "encoding_detection": True,
    "metadata_extraction": True
}
```

### **Build Server Setup**
```python
build_config = {
    "build_timeout": 300,
    "allowed_commands": ["pip", "python", "pytest", "mypy", "black"],
    "quality_checks": ["mypy", "black", "isort", "flake8"],
    "coverage_threshold": 90
}
```

### **Git Server Setup**
```python
git_config = {
    "git_timeout": 60,
    "allowed_operations": ["init", "add", "commit", "status", "log"],
    "auto_gitignore": True,
    "commit_conventions": "conventional"
}
```

## 📊 Example Usage Scenarios

### **1. Calculator with MCP Enhancement**
```
"Create a Python calculator module with MCP-enhanced development:
- Basic and advanced arithmetic operations
- Comprehensive error handling and validation
- Command-line interface with user experience
- Memory functions and calculation history
- 95%+ test coverage with MCP testing tools
- Professional code quality with MCP build tools
- Git repository with MCP version control"
```

### **2. Web API with Full MCP Integration**
```
"Build a RESTful API service with complete MCP workflow:
- FastAPI framework with async operations
- JWT authentication and authorization
- Database integration with SQLAlchemy
- Comprehensive API testing suite
- Docker containerization
- Professional documentation and deployment"
```

### **3. CLI Tool with MCP Workflow**
```
"Develop a command-line productivity tool:
- File organization and management utilities
- Rich terminal interface with Click framework
- Plugin architecture for extensibility
- Cross-platform compatibility
- Comprehensive help and documentation
- Professional packaging and distribution"
```

## 🎯 Benefits of MCP Integration

### **Enhanced Reliability**
- **Robust Operations**: MCP servers provide tested, reliable operations
- **Error Recovery**: Advanced error handling and recovery mechanisms
- **Validation**: Input validation and sanitization at protocol level
- **Consistency**: Standardized operations across development stages

### **Improved Security**
- **Access Control**: Path validation and permission checking
- **Command Validation**: Whitelist-based command execution
- **Timeout Protection**: Prevents resource exhaustion attacks
- **Audit Logging**: Comprehensive operation logging and tracking

### **Better Performance**
- **Optimized Operations**: Streaming and caching for large files
- **Parallel Processing**: Concurrent operations where possible
- **Resource Management**: Efficient memory and CPU utilization
- **Caching**: Intelligent caching of build artifacts and results

### **Professional Quality**
- **Enterprise Standards**: Professional-grade development operations
- **Quality Assurance**: Automated code quality and testing
- **Documentation**: Comprehensive documentation generation
- **Compliance**: Industry standard practices and conventions

## 🔧 Customization and Extension

### **Adding Custom MCP Servers**
```python
class CustomMCPServer:
    def __init__(self, config):
        self.config = config
    
    async def custom_operation(self, params):
        # Implement custom MCP operation
        pass

# Register with MCP server manager
mcp_server_manager.register_server("custom", CustomMCPServer)
```

### **Extending Agent Capabilities**
```python
# Add new MCP-enhanced agent
custom_agent = LlmAgent(
    name="custom_mcp_agent",
    tools=[custom_mcp_toolset],
    instruction="Use MCP servers for enhanced operations..."
)
```

### **Custom Workflow Patterns**
```python
# Create custom MCP workflow
custom_workflow = SequentialAgent(
    name="custom_mcp_workflow",
    sub_agents=[
        mcp_spec_reader,
        custom_mcp_processor,
        mcp_quality_checker,
        mcp_deployer
    ]
)
```

## 📈 Performance and Monitoring

### **MCP Server Metrics**
- **Operation Latency**: Track MCP server response times
- **Success Rates**: Monitor operation success/failure rates
- **Resource Usage**: CPU, memory, and disk utilization
- **Error Patterns**: Identify common failure modes

### **Workflow Analytics**
- **Development Velocity**: Time from spec to deployment
- **Quality Metrics**: Test coverage, code quality scores
- **Error Rates**: Build failures, test failures, deployment issues
- **Resource Efficiency**: Optimal resource utilization patterns

## 🔍 Troubleshooting

### **Common MCP Issues**
1. **Server Connection**: Ensure MCP servers are running and accessible
2. **Permission Errors**: Check file system permissions and access controls
3. **Timeout Issues**: Adjust timeout settings for long-running operations
4. **Resource Limits**: Monitor and adjust resource limits as needed

### **Debug Commands**
```bash
# Check MCP server status
"Show MCP server status and health"

# Validate MCP configuration
"Validate MCP server configurations"

# Test MCP operations
"Test MCP filesystem operations"
```

This MCP-enhanced development workflow demonstrates how Model Context Protocol servers can significantly improve the reliability, security, and professional quality of multi-agent development systems.

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Git
- Virtual environment support

### Installation & Setup

1. **Clone and navigate to the project:**
   ```bash
   cd mcp_dev_workflow
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install local ADK with GitHub Copilot support:**
   ```bash
   pip install -e ..
   ```

### Running the Workflow

**Start the MCP-enhanced development workflow:**
```bash
source .venv/bin/activate
adk run .
```

This command will:
- ✅ Initialize the MCP coordinator agent with GitHub Copilot
- ✅ Start all MCP servers (filesystem, build, git)
- ✅ Launch the interactive development workflow
- ✅ Provide access to all specialized agents

### Available Commands
Once running, you can interact with the workflow by:
- Providing development specifications
- Requesting code generation
- Running tests and builds
- Managing version control
- Type `exit` to quit

### MCP Servers Included
- **Filesystem Server** (`mcp_filesystem_server.py`) - File operations
- **Build Server** (`mcp_build_server.py`) - Build, test, and lint operations  
- **Git Server** (`mcp_git_server.py`) - Version control operations

### Agent Architecture
- **Coordinator Agent** - Orchestrates the entire workflow
- **Spec Reader Agent** - Analyzes requirements and specifications
- **Code Generator Agent** - Creates implementation code with GitHub Copilot
- **Test Generator Agent** - Generates comprehensive test suites
- **Build Agent** - Handles compilation and build processes
- **Test Runner Agent** - Executes tests and generates reports
- **Git Agent** - Manages version control and commits

### Example Usage

Once the workflow is running, you can provide specifications like:

```
Create a Python calculator module with the following features:
- Basic arithmetic operations (add, subtract, multiply, divide)
- Support for floating-point numbers
- Error handling for division by zero
- Unit tests with pytest
- Type hints and docstrings
- Follow PEP 8 standards
```

The workflow will automatically:
1. 📋 Analyze the specification
2. 💻 Generate the implementation code
3. 🧪 Create comprehensive tests
4. 🔨 Build and validate the code
5. ✅ Run tests and quality checks
6. 📝 Commit to version control

### Troubleshooting

**Common Issues:**

1. **Import Error: `No module named 'google.adk.models.github_copilot_llm'`**
   ```bash
   # Make sure you installed the local ADK package
   pip install -e ..
   ```

2. **MCP Server Connection Issues:**
   ```bash
   # Ensure MCP servers are executable
   chmod +x mcp_*.py
   ```

3. **Permission Denied Errors:**
   ```bash
   # Check file permissions and allowed directories
   ls -la mcp_*.py
   ```

4. **Virtual Environment Issues:**
   ```bash
   # Recreate virtual environment
   rm -rf .venv
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install -e ..
   ```

### Configuration

The MCP servers can be configured via environment variables:

- **Filesystem Server:**
  - `ALLOWED_DIRECTORIES`: Comma-separated list of allowed directories
  - `MAX_FILE_SIZE`: Maximum file size in bytes (default: 10MB)

- **Build Server:**
  - `BUILD_TIMEOUT`: Build timeout in seconds (default: 300)
  - `ALLOWED_COMMANDS`: Comma-separated list of allowed commands

- **Git Server:**
  - `GIT_TIMEOUT`: Git operation timeout in seconds (default: 60)
  - `ALLOWED_OPERATIONS`: Comma-separated list of allowed git operations

---