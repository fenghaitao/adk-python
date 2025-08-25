# Multi-Agent Software Development Workflow

## 🚀 Complete Example: Spec → Code → Tests → Build → Test → Commit

This example demonstrates a sophisticated multi-agent system that handles the entire software development lifecycle:

1. **📋 Spec Reader** - Analyzes requirements and specifications
2. **💻 Code Generator** - Creates implementation code
3. **🧪 Test Generator** - Creates comprehensive tests
4. **🔨 Build Agent** - Handles building and compilation
5. **✅ Test Runner** - Executes tests and reports results
6. **📝 Git Agent** - Handles version control operations
7. **🎯 Coordinator** - Orchestrates the entire workflow

## 🏗️ How to Use This Example

### Method 1: Interactive CLI

```bash
# Run the agent interactively
adk run .

# Then provide a specification like:
"Create a Python calculator module with basic arithmetic operations, 
advanced functions, input validation, and a command-line interface. 
Include comprehensive tests and proper documentation."
```

### Method 2: Web Interface

```bash
# Launch web UI
adk web . --port 8080

# Open browser to http://localhost:8080
# Enter your specification in the chat interface
```

### Method 3: Demo Script

```bash
# Run the demo script
python demo.py

# Choose from pre-built scenarios:
# 1. Simple calculator specification
# 2. Task manager from specification file
# 3. File utility specification
```

### Method 4: Using Specification Files

```bash
# Use the provided sample specification
adk run .
"Read the specification from sample_spec.md and implement the task manager."

# Or create your own specification file
cp sample_spec.md my_project_spec.md
# Edit my_project_spec.md with your requirements
adk run .
"Read the specification from my_project_spec.md and implement it."
```

## 📋 Using Specification Files

### What is sample_spec.md?

The `sample_spec.md` file is a **detailed specification document** that demonstrates how to write comprehensive software requirements for the multi-agent system. It serves multiple purposes:

#### **1. Example Input for the System**
Shows users what a well-structured specification looks like that the system can process effectively, including:
- Functional requirements (what the software should do)
- Technical requirements (technology stack, architecture)
- File structure (how to organize the code)
- User interface design (CLI commands and usage)
- Testing requirements (coverage, test types)
- Quality standards (coding standards, documentation)

#### **2. Reference for the Spec Reader Agent**
When you tell the system to read from `sample_spec.md`, the Spec Reader Agent will:
- Use the `read_specification_file()` tool to read the file
- Parse all the detailed requirements
- Extract technical specifications
- Create a comprehensive development plan

#### **3. Template for Your Own Specifications**
Use `sample_spec.md` as a template to create your own specification files:

```markdown
# Your Project Specification

## Overview
Brief description of what you want to build

## Functional Requirements
### Core Features
1. Feature 1: Description
2. Feature 2: Description

## Technical Requirements
### Programming Language
- Python 3.8+
- Specific libraries/frameworks

### Code Structure
- Class designs
- Module organization

## File Structure
```
project_name/
├── src/
│   ├── main.py
│   └── utils.py
├── tests/
└── README.md
```

## Testing Requirements
- Unit tests with 90% coverage
- Integration tests
- Error handling tests
```

### How to Use Specification Files

#### **Method 1: Use the Sample Specification**
```bash
adk run .
# Then enter:
"Read the specification from sample_spec.md and implement the complete task manager application."
```

#### **Method 2: Create Your Own Specification**
```bash
# Copy and customize the sample
cp sample_spec.md my_web_api_spec.md
# Edit with your requirements

# Then run:
adk run .
"Please read the specification from my_web_api_spec.md and implement the complete web API."
```

#### **Method 3: Via Demo Script**
```bash
python demo.py
# Choose option 2: "Task Manager from Specification File"
```

### Benefits of Using Specification Files

- **Detailed Requirements**: More comprehensive than simple text prompts
- **Structured Format**: Ensures nothing is missed during implementation
- **Consistent Results**: Same specification produces consistent implementations
- **Reusable Templates**: Create templates for common project types
- **Version Control**: Track changes to requirements over time

### What the Sample Spec Contains

The `sample_spec.md` defines a **Task Manager Application** with:
- **Core Features**: Add, list, complete, remove tasks
- **Data Model**: Task properties (ID, description, status, dates, priority)
- **CLI Interface**: Detailed command-line commands and usage examples
- **Data Persistence**: JSON file storage with error handling
- **Testing Requirements**: 90% coverage with comprehensive test scenarios
- **Quality Standards**: PEP 8 compliance, type hints, documentation

## 📋 Example Specifications to Try

### 1. Simple Calculator
```
Create a Python calculator module with the following features:
- Basic arithmetic: add, subtract, multiply, divide
- Advanced operations: power, square root, factorial
- Input validation and error handling
- Command-line interface
- Memory functions (store, recall, clear)
- Calculation history
```

### 2. File Utility
```
Build a Python file utility with these capabilities:
- Read and write text files
- Create file backups with timestamps
- Search for text within files
- File size and modification date info
- Batch operations on multiple files
- Error handling for file operations
```

### 3. Data Validator
```
Implement a data validation library that can:
- Validate email addresses
- Check phone number formats
- Validate URLs and IP addresses
- Custom validation rules
- Batch validation of datasets
- Generate validation reports
```

### 4. Task Manager (from sample_spec.md)
```
"Read the specification from sample_spec.md and implement the complete task manager application."
```
This uses the detailed specification file that includes:
- Complete feature requirements
- Technical architecture details
- File structure specifications
- CLI interface design
- Testing and quality requirements

### 5. Custom Project (using your own spec)
```
# First create your specification file
cp sample_spec.md my_project_spec.md
# Edit my_project_spec.md with your requirements

# Then run:
"Please read the specification from my_project_spec.md and implement the complete system."
```

## 🔄 What the System Does

### Step 1: Specification Analysis
- Reads and parses requirements
- Identifies technology stack
- Creates development plan
- Sets up project structure

### Step 2: Code Generation
- Implements core functionality
- Follows best practices
- Adds error handling
- Includes documentation

### Step 3: Test Creation
- Generates unit tests
- Creates integration tests
- Includes edge cases
- Ensures high coverage

### Step 4: Build Process
- Installs dependencies
- Validates syntax
- Checks imports
- Reports build status

### Step 5: Test Execution
- Runs complete test suite
- Analyzes results
- Reports coverage
- Identifies issues

### Step 6: Version Control
- Initializes git repository
- Commits all files
- Creates meaningful commit messages
- Sets up git configuration

## 📁 Generated Project Structure

The system creates a complete project structure:

```
project_name/
├── src/
│   ├── __init__.py
│   ├── main_module.py
│   └── utils.py
├── tests/
│   ├── __init__.py
│   ├── test_main_module.py
│   └── test_utils.py
├── docs/
│   └── README.md
├── requirements.txt
├── .gitignore
└── README.md
```

## 🎯 Key Features

### Multi-Agent Coordination
- **Sequential Pipeline**: Agents work in order, each building on previous results
- **State Management**: Information flows between agents via `output_key` mechanism
- **Error Handling**: Each agent can handle and report issues
- **Flexible Routing**: Coordinator can choose between different workflow paths

### Code Quality
- **Best Practices**: Follows PEP 8 and Python conventions
- **Documentation**: Comprehensive docstrings and comments
- **Type Hints**: Full type annotation support
- **Error Handling**: Robust error handling and validation

### Testing Excellence
- **High Coverage**: Aims for >90% test coverage
- **Multiple Test Types**: Unit, integration, and edge case tests
- **Pytest Framework**: Uses modern testing practices
- **Automated Execution**: Runs tests and reports results

### DevOps Integration
- **Build Automation**: Handles dependencies and compilation
- **Version Control**: Git initialization and commit automation
- **Project Structure**: Creates industry-standard project layouts
- **Documentation**: Generates README and documentation

## 🔧 Prerequisites

### Required Setup
1. **ADK Installation**: `pip install google-adk`
2. **API Keys**: Set up Gemini API key or Google Cloud credentials
3. **Git**: Ensure git is installed and accessible
4. **Python**: Python 3.8+ with pip

### Optional Tools
- **pytest**: For test execution (installed automatically)
- **Docker**: For containerized builds
- **IDE**: VS Code or PyCharm for development

## 📝 Best Practices for Specification Files

### Be Specific and Detailed
```markdown
# Good:
- Use Python 3.8+ with type hints and dataclasses
- Store data in JSON format at data/tasks.json
- Include comprehensive docstrings for all functions
- Follow PEP 8 style guidelines

# Too Vague:
- Use Python
- Save data somehow
- Add some documentation
```

### Include Examples and Usage Scenarios
```markdown
### Example Usage
```bash
$ python cli.py add "Buy groceries" --due 2024-02-15 --priority high
Task added: #1 - Buy groceries

$ python cli.py list --status pending
1. [PENDING] Buy groceries (Due: 2024-02-15, Priority: High)
```
```

### Define Quality Standards
```markdown
## Quality Requirements
- Follow PEP 8 style guidelines
- Minimum 90% test coverage
- Include type hints for all functions
- Comprehensive error handling for edge cases
- Proper logging for debugging
```

### Specify File Structure
```markdown
## File Structure
```
project_name/
├── src/
│   ├── __init__.py
│   ├── models.py        # Data models
│   ├── manager.py       # Core logic
│   └── cli.py          # Command-line interface
├── tests/
│   ├── test_models.py
│   ├── test_manager.py
│   └── test_cli.py
├── data/
│   └── storage.json    # Data persistence
├── requirements.txt
└── README.md
```
```

## 🎉 Expected Results

After running a specification through the system, you'll get:

1. **Complete Codebase**: Production-ready implementation
2. **Comprehensive Tests**: Full test suite with high coverage
3. **Documentation**: README and code documentation
4. **Git Repository**: Initialized repo with initial commit
5. **Build Validation**: Confirmed working build
6. **Test Results**: Passing test suite

## 🔍 Troubleshooting

### Common Issues
1. **API Key Missing**: Set `GOOGLE_API_KEY` environment variable
2. **Git Not Found**: Install git and ensure it's in PATH
3. **Permission Errors**: Check file/directory permissions
4. **Build Failures**: Review dependency requirements

### Debug Mode
```bash
# Run with detailed logging
adk run . --log_level DEBUG

# Save session for analysis
adk run . --save_session --session_id debug_001
```

This multi-agent system demonstrates the power of specialized AI agents working together to solve complex, multi-step problems. Each agent brings expertise in their domain while the coordinator ensures smooth workflow execution.