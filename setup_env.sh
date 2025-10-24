#!/bin/bash

# setup_env.sh - Environment setup script for ADK Python repository
# This script initializes git submodules and sets up Python virtual environments

set -e  # Exit on any error

echo "🚀 Starting ADK Python environment setup..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    print_error "uv is not installed. Please install uv first:"
    print_error "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

print_success "uv is installed"

# Initialize and update git submodules (skip LFS files for faster checkout)
print_status "Initializing and updating git submodules (skipping LFS files)..."
GIT_LFS_SKIP_SMUDGE=1 git submodule update --init --recursive

if [ $? -eq 0 ]; then
    print_success "Git submodules initialized and updated"
else
    print_error "Failed to initialize git submodules"
    exit 1
fi

# List of submodules from .gitmodules (excluding agent-os and agent_os_integration simics-mcp-server)
SUBMODULES=(
    "spec-kit"
    "contributing/samples/spec_kit_integration/simics-mcp-server"
    "contributing/samples/spec_kit_integration/mcp-crawl4ai-rag"
)

# Function to setup virtual environment for a submodule
setup_submodule_env() {
    local submodule_path=$1
    
    if [ ! -d "$submodule_path" ]; then
        print_warning "Submodule directory $submodule_path does not exist, skipping..."
        return
    fi
    
    print_status "Setting up environment for submodule: $submodule_path"
    
    # Change to submodule directory
    cd "$submodule_path"
    
    # Check if pyproject.toml or setup.py exists (indicating a Python project)
    if [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
        print_status "Creating virtual environment with Python 3.12..."
        uv venv --python 3.12
        
        if [ $? -eq 0 ]; then
            print_success "Virtual environment created for $submodule_path"
            
            print_status "Installing package in development mode..."
            # Special handling for mcp-crawl4ai-rag which needs torch-backend cpu
            if [[ "$submodule_path" == *"mcp-crawl4ai-rag"* ]]; then
                uv pip install --torch-backend cpu -e .
            else
                uv pip install -e .
            fi
            
            if [ $? -eq 0 ]; then
                print_success "Package installed in development mode for $submodule_path"
                
                # Additional setup for mcp-crawl4ai-rag
                if [[ "$submodule_path" == *"mcp-crawl4ai-rag"* ]]; then
                    print_status "Running additional setup for mcp-crawl4ai-rag..."
                    
                    # Check if we have sudo permission
                    if sudo -n true 2>/dev/null; then
                        print_status "Sudo permission available, running crawl4ai-setup..."
                        .venv/bin/crawl4ai-setup
                        if [ $? -eq 0 ]; then
                            print_success "crawl4ai-setup completed successfully"
                        else
                            print_error "crawl4ai-setup failed"
                        fi
                    else
                        print_status "No sudo permission, running install_deps_without_sudo.py..."
                        if [ -f "install_deps_without_sudo.py" ]; then
                            .venv/bin/python install_deps_without_sudo.py
                            if [ $? -eq 0 ]; then
                                print_success "install_deps_without_sudo.py completed successfully"
                            else
                                print_error "install_deps_without_sudo.py failed"
                            fi
                        else
                            print_warning "install_deps_without_sudo.py not found in $submodule_path"
                        fi
                    fi
                fi
                
                # Additional setup for simics-mcp-server
                if [[ "$submodule_path" == *"simics-mcp-server"* ]]; then
                    print_status "Running additional setup for simics-mcp-server..."
                    
                    if [ -f "setup_ispm.sh" ]; then
                        print_status "Running setup_ispm.sh..."
                        bash setup_ispm.sh --quiet
                        if [ $? -eq 0 ]; then
                            print_success "setup_ispm.sh completed successfully"
                        else
                            print_error "setup_ispm.sh failed"
                        fi
                    else
                        print_warning "setup_ispm.sh not found in $submodule_path"
                    fi
                fi
            else
                print_error "Failed to install package for $submodule_path"
            fi
        else
            print_error "Failed to create virtual environment for $submodule_path"
        fi
    else
        print_warning "No pyproject.toml or setup.py found in $submodule_path, skipping Python setup"
    fi
    
    # Return to repository root
    cd - > /dev/null
}

# Setup virtual environments for each submodule
for submodule in "${SUBMODULES[@]}"; do
    setup_submodule_env "$submodule"
    echo ""  # Add spacing between submodules
done

# Setup main repository environment
print_status "Setting up main repository environment..."
if [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
    print_status "Creating virtual environment for main repository with Python 3.12..."
    uv venv --python 3.12
    
    if [ $? -eq 0 ]; then
        print_success "Virtual environment created for main repository"
        
        print_status "Installing main package in development mode..."
        uv pip install -e .
        
        if [ $? -eq 0 ]; then
            print_success "Main package installed in development mode"
        else
            print_error "Failed to install main package"
        fi
    else
        print_error "Failed to create virtual environment for main repository"
    fi
else
    print_warning "No pyproject.toml or setup.py found in main repository"
fi

echo ""
print_success "🎉 Environment setup completed!"
print_status "To activate the main virtual environment, run:"
print_status "source .venv/bin/activate"
print_status ""
print_status "To activate submodule virtual environments, navigate to the submodule directory and run:"
print_status "source .venv/bin/activate"
print_status ""
print_warning "⚠️  IMPORTANT: Don't forget to set required environment variables!"
print_status "Add the following to your ~/.bashrc file:"
print_status "export GITHUB_TOKEN=your_github_token_here"
print_status "export IFLOW_API_KEY=your_iflow_api_key_here"
print_status ""
print_status "Then reload your shell with: source ~/.bashrc"
