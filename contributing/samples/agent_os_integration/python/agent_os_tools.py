# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Agent OS tools integration for ADK."""

import os
import subprocess
import tempfile
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

# Import ADK tools - use more robust import method
try:
    # Try direct import first (when ADK is properly installed)
    from google.adk.tools.base_tool import BaseTool
    from google.adk.tools.base_toolset import BaseToolset
    from google.adk.tools.tool_context import ToolContext
    from google.adk.tools.transfer_to_agent_tool import transfer_to_agent
except ImportError:
    # Fallback: Add src directory only if direct import fails
    import sys
    from pathlib import Path as PathLib
    
    # Find ADK source directory relative to this file
    current_dir = PathLib(__file__).parent
    adk_src_dir = current_dir.parent.parent.parent / "src"
    
    if adk_src_dir.exists():
        sys.path.insert(0, str(adk_src_dir))
        try:
            from google.adk.tools.base_tool import BaseTool
            from google.adk.tools.base_toolset import BaseToolset
            from google.adk.tools.tool_context import ToolContext
            from google.adk.tools.transfer_to_agent_tool import transfer_to_agent
        except ImportError as e:
            raise ImportError(
                f"Could not import ADK tools. Please ensure ADK is installed or "
                f"PYTHONPATH includes the ADK source directory. Error: {e}"
            ) from e
    else:
        raise ImportError(
            f"ADK source directory not found at {adk_src_dir}. "
            f"Please ensure ADK is installed or set PYTHONPATH correctly."
        )


class AgentOsReadTool(BaseTool):
    """Tool for reading files in Agent OS workflows."""

    def __init__(self):
        super().__init__(
            name="read_file",
            description="Read the contents of a file. Use this to examine files in the project.",
        )

    def _get_declaration(self) -> Optional['types.FunctionDeclaration']:
        """Get function declaration for the LLM."""
        from google.genai import types
        return types.FunctionDeclaration(
            name="read_file",
            description="Read the contents of a file. Use this to examine files in the project.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "file_path": types.Schema(
                        type=types.Type.STRING,
                        description="Path to the file to read"
                    )
                },
                required=["file_path"]
            )
        )

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: ToolContext
    ) -> Any:
        file_path = args.get("file_path")
        if not file_path:
            return {"error": "file_path is required"}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return {"content": content, "file_path": file_path}
        except FileNotFoundError:
            return {"error": f"File not found: {file_path}"}
        except Exception as e:
            return {"error": f"Error reading file: {str(e)}"}


class AgentOsWriteTool(BaseTool):
    """Tool for writing files in Agent OS workflows."""

    def __init__(self):
        super().__init__(
            name="write_file",
            description="Write content to a file. Use this to create or update files in the project.",
        )

    def _get_declaration(self) -> Optional['types.FunctionDeclaration']:
        """Get function declaration for the LLM."""
        from google.genai import types
        return types.FunctionDeclaration(
            name="write_file",
            description="Write content to a file. Use this to create or update files in the project.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "file_path": types.Schema(
                        type=types.Type.STRING,
                        description="Path to the file to write"
                    ),
                    "content": types.Schema(
                        type=types.Type.STRING,
                        description="Content to write to the file"
                    ),
                    "overwrite": types.Schema(
                        type=types.Type.BOOLEAN,
                        description="Whether to overwrite if file exists (default: False)"
                    )
                },
                required=["file_path", "content"]
            )
        )

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: ToolContext
    ) -> Any:
        file_path = args.get("file_path")
        content = args.get("content", "")
        overwrite = args.get("overwrite", False)

        if not file_path:
            return {"error": "file_path is required"}

        try:
            # Check if file exists and overwrite is False
            if os.path.exists(file_path) and not overwrite:
                return {"error": f"File already exists: {file_path}. Set overwrite=True to overwrite."}

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return {"success": True, "file_path": file_path, "bytes_written": len(content)}
        except Exception as e:
            return {"error": f"Error writing file: {str(e)}"}


class AgentOsGrepTool(BaseTool):
    """Tool for searching files using grep in Agent OS workflows."""

    def __init__(self):
        super().__init__(
            name="grep_search",
            description="Search for patterns in files using grep. Use this to find specific content across files.",
        )

    def _get_declaration(self) -> Optional['types.FunctionDeclaration']:
        """Get function declaration for the LLM."""
        from google.genai import types
        return types.FunctionDeclaration(
            name="grep_search",
            description="Search for patterns in files using grep. Use this to find specific content across files.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "pattern": types.Schema(
                        type=types.Type.STRING,
                        description="Pattern to search for"
                    ),
                    "file_path": types.Schema(
                        type=types.Type.STRING,
                        description="File or directory to search in (default: '.')"
                    ),
                    "case_sensitive": types.Schema(
                        type=types.Type.BOOLEAN,
                        description="Whether search is case sensitive (default: False)"
                    ),
                    "max_lines": types.Schema(
                        type=types.Type.INTEGER,
                        description="Maximum number of result lines to return (default: 50)"
                    )
                },
                required=["pattern"]
            )
        )

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: ToolContext
    ) -> Any:
        pattern = args.get("pattern")
        file_path = args.get("file_path", ".")
        case_sensitive = args.get("case_sensitive", False)
        max_lines = args.get("max_lines", 50)

        if not pattern:
            return {"error": "pattern is required"}

        try:
            cmd = ["grep", "-n"]
            if not case_sensitive:
                cmd.append("-i")
            cmd.extend([pattern, file_path])

            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30
            )
            
            lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
            if lines and lines[0] == "":
                lines = lines[1:]
            
            # Limit results
            if len(lines) > max_lines:
                lines = lines[:max_lines]
                truncated = True
            else:
                truncated = False

            return {
                "matches": lines,
                "pattern": pattern,
                "file_path": file_path,
                "total_matches": len(lines),
                "truncated": truncated,
            }
        except subprocess.TimeoutExpired:
            return {"error": "Search timed out"}
        except Exception as e:
            return {"error": f"Error searching: {str(e)}"}


class AgentOsGlobTool(BaseTool):
    """Tool for finding files using glob patterns in Agent OS workflows."""

    def __init__(self):
        super().__init__(
            name="glob_search",
            description="Find files matching a glob pattern. Use this to discover files in the project.",
        )

    def _get_declaration(self) -> Optional['types.FunctionDeclaration']:
        """Get function declaration for the LLM."""
        from google.genai import types
        return types.FunctionDeclaration(
            name="glob_search",
            description="Find files matching a glob pattern. Use this to discover files in the project.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "pattern": types.Schema(
                        type=types.Type.STRING,
                        description="Glob pattern to match files (e.g., '*.py', '**/*.md')"
                    ),
                    "directory": types.Schema(
                        type=types.Type.STRING,
                        description="Directory to search in (default: '.')"
                    ),
                    "max_files": types.Schema(
                        type=types.Type.INTEGER,
                        description="Maximum number of files to return (default: 100)"
                    )
                },
                required=["pattern"]
            )
        )

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: ToolContext
    ) -> Any:
        pattern = args.get("pattern")
        directory = args.get("directory", ".")
        max_files = args.get("max_files", 100)

        if not pattern:
            return {"error": "pattern is required"}

        try:
            from glob import glob
            
            search_path = os.path.join(directory, pattern)
            files = glob(search_path, recursive=True)
            
            # Limit results
            if len(files) > max_files:
                files = files[:max_files]
                truncated = True
            else:
                truncated = False

            return {
                "files": files,
                "pattern": pattern,
                "directory": directory,
                "total_files": len(files),
                "truncated": truncated,
            }
        except Exception as e:
            return {"error": f"Error searching files: {str(e)}"}


class AgentOsBashTool(BaseTool):
    """Tool for executing bash commands in Agent OS workflows."""

    def __init__(self):
        super().__init__(
            name="bash_command",
            description="Execute bash commands. Use this to run shell commands, git operations, and other system tasks.",
        )

    def _get_declaration(self) -> Optional['types.FunctionDeclaration']:
        """Get function declaration for the LLM."""
        from google.genai import types
        return types.FunctionDeclaration(
            name="bash_command",
            description="Execute bash commands. Use this to run shell commands, git operations, and other system tasks.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "command": types.Schema(
                        type=types.Type.STRING,
                        description="Bash command to execute"
                    ),
                    "working_directory": types.Schema(
                        type=types.Type.STRING,
                        description="Directory to run command in (default: '.')"
                    ),
                    "timeout": types.Schema(
                        type=types.Type.INTEGER,
                        description="Timeout in seconds (default: 60)"
                    )
                },
                required=["command"]
            )
        )

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: ToolContext
    ) -> Any:
        command = args.get("command")
        working_directory = args.get("working_directory", ".")
        timeout = args.get("timeout", 60)

        if not command:
            return {"error": "command is required"}

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=working_directory,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "command": command,
                "working_directory": working_directory,
            }
        except subprocess.TimeoutExpired:
            return {"error": f"Command timed out after {timeout} seconds"}
        except Exception as e:
            return {"error": f"Error executing command: {str(e)}"}


class AgentOsTransferTool(BaseTool):
    """Tool for transferring control to another agent."""

    def __init__(self):
        super().__init__(
            name="transfer_to_agent",
            description="Transfer control to another agent. Use this when you have completed your task and need to return control to the main agent or transfer to another specialized agent.",
        )

    def _get_declaration(self) -> Optional['types.FunctionDeclaration']:
        """Get function declaration for the LLM."""
        from google.genai import types
        return types.FunctionDeclaration(
            name="transfer_to_agent",
            description="Transfer control to another agent. Use this when you have completed your task and need to return control to the main agent or transfer to another specialized agent.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "agent_name": types.Schema(
                        type=types.Type.STRING,
                        description="Name of the agent to transfer control to. Use 'agent_os_agent' to return to main agent."
                    )
                },
                required=["agent_name"]
            )
        )

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: ToolContext
    ) -> Any:
        agent_name = args.get("agent_name")
        if not agent_name:
            return {"error": "agent_name is required"}

        # Use the ADK transfer mechanism
        transfer_to_agent(agent_name, tool_context)
        return {"result": f"Transferred control to {agent_name}"}


# Simics-specific tools for device modeling
class SimicsGetDmlExampleTool(BaseTool):
    """Tool for getting DML template and examples."""

    def __init__(self):
        super().__init__(
            name="get_dml_example",
            description="Get the DML file example template for device modeling. Returns DML syntax patterns and examples.",
        )
        
        # Load DML template if available
        self.dml_template = self._load_dml_template()

    def _load_dml_template(self) -> Optional[str]:
        """Load DML template from file."""
        try:
            # Look for DML template in various locations
            template_paths = [
                Path(__file__).parent / "simics-dml-tpl.dml",
                Path("simics-dml-tpl.dml"),
                Path(".") / "simics-dml-tpl.dml"
            ]
            
            for path in template_paths:
                if path.exists():
                    return path.read_text(encoding='utf-8')
                    
            # Return basic DML template if file not found
            return """dml 1.4;

device sample_device;

// Device attributes
attribute device_name default "sample_device";

// Register bank
bank registers {
    register control size 4 @ 0x00 {
        // Control register implementation
        field enable @ [0];
        field reset @ [1];
        
        method write_register(uint64 enabled_bytes, uint64 value) {
            default(enabled_bytes, value);
            // Add side effects here
        }
    }
    
    register status size 4 @ 0x04 "read-only" {
        // Status register implementation
        field ready @ [0];
        field error @ [1];
    }
}

// Port for external signals
port signal_in {
    implement signal {
        method signal_raise() {
            // Handle incoming signal
        }
    }
}

// Connect for interface communication
connect memory {
    interface memory_space;
}
"""
        except Exception:
            return None

    def _get_declaration(self) -> Optional['types.FunctionDeclaration']:
        """Get function declaration for the LLM."""
        from google.genai import types
        return types.FunctionDeclaration(
            name="get_dml_example",
            description="Get the DML file example template for device modeling. Returns DML syntax patterns and examples.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={},
                required=[]
            )
        )

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: ToolContext
    ) -> Any:
        return {
            "dml_template": self.dml_template or "DML template not available",
            "description": "DML template with basic device structure, registers, ports, and connections"
        }


class SimicsQueryLibDocTool(BaseTool):
    """Tool for querying Simics library documentation."""

    def __init__(self):
        super().__init__(
            name="query_lib_doc",
            description="Query Device Modeling Language documentation for built-in templates, functions, methods, and Simics library components.",
        )

    def _get_declaration(self) -> Optional['types.FunctionDeclaration']:
        """Get function declaration for the LLM."""
        from google.genai import types
        return types.FunctionDeclaration(
            name="query_lib_doc",
            description="Query Device Modeling Language documentation for built-in templates, functions, methods, and Simics library components.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "queries": types.Schema(
                        type=types.Type.STRING,
                        description="Comma-separated list of queries or single query"
                    ),
                    "max_results": types.Schema(
                        type=types.Type.INTEGER,
                        description="Maximum number of results to return (default: 5)"
                    )
                },
                required=["queries"]
            )
        )

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: ToolContext
    ) -> Any:
        queries = args.get("queries", "")
        max_results = args.get("max_results", 5)
        
        try:
            # Try to use the actual API if environment is configured
            results = self._query_utility_doc(queries, max_results)
            return {"results": results, "queries": queries}
        except Exception as e:
            # Fallback to static documentation
            return {
                "results": self._get_static_lib_doc(queries),
                "queries": queries,
                "note": f"Using static documentation. API error: {str(e)}"
            }

    def _query_utility_doc(self, queries: str, max_results: int) -> List[str]:
        """Query the actual utility documentation API."""
        load_dotenv()
        
        api_key = os.getenv('API_KEY_UTILITY_WF')
        base_url = os.getenv('BASE_URL')
        
        if not api_key or not base_url:
            raise ValueError("API configuration not available")

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        query_list = [q.strip() for q in queries.split(',') if q.strip()]
        all_results = []

        for query in query_list:
            try:
                payload = {
                    "inputs": {"query": query},
                    "response_mode": "blocking",
                    "user": "simics-lib-agent"
                }

                response = requests.post(
                    f"{base_url}/workflows/run",
                    headers=headers,
                    json=payload,
                    timeout=60
                )

                response.raise_for_status()
                result_data = response.json()

                if 'data' in result_data and 'outputs' in result_data['data']:
                    text_results = result_data['data']['outputs'].get('text', [])
                    for item in text_results:
                        if isinstance(item, dict) and 'content' in item:
                            all_results.append(item['content'])

            except Exception:
                continue

        return all_results[:max_results]

    def _get_static_lib_doc(self, queries: str) -> List[str]:
        """Return static DML library documentation."""
        static_docs = [
            "DML built-in templates: register, field, bank, port, connect, implement",
            "Common register methods: read_register(), write_register(), reset()",
            "Utility templates: utility.dml contains pre-defined templates for common patterns",
            "Attribute types: uint64, int64, bool, string, object",
            "Event handling: after() for deferred operations, event objects for timers",
            "Interface implementation: implement interface_name for connecting to other devices",
            "Memory operations: transact() for reading/writing memory",
            "Logging: log(), log_error(), log_warning() for debug output"
        ]
        
        query_words = queries.lower().split()
        filtered_docs = []
        
        for doc in static_docs:
            if any(word in doc.lower() for word in query_words):
                filtered_docs.append(doc)
        
        return filtered_docs if filtered_docs else static_docs


class SimicsQueryGuideTool(BaseTool):
    """Tool for querying Simics documentation and concept guides."""

    def __init__(self):
        super().__init__(
            name="query_simics_guide",
            description="Semantically query Simics documentation and concept guides for understanding concepts and modeling approaches.",
        )

    def _get_declaration(self) -> Optional['types.FunctionDeclaration']:
        """Get function declaration for the LLM."""
        from google.genai import types
        return types.FunctionDeclaration(
            name="query_simics_guide",
            description="Semantically query Simics documentation and concept guides for understanding concepts and modeling approaches.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "queries": types.Schema(
                        type=types.Type.STRING,
                        description="Comma-separated list of queries or single query"
                    ),
                    "max_results": types.Schema(
                        type=types.Type.INTEGER,
                        description="Maximum number of results to return (default: 5)"
                    )
                },
                required=["queries"]
            )
        )

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: ToolContext
    ) -> Any:
        queries = args.get("queries", "")
        max_results = args.get("max_results", 5)
        
        try:
            # Try to use the actual API if environment is configured
            results = self._query_guide_api(queries, max_results)
            return {"results": results, "queries": queries}
        except Exception as e:
            # Fallback to static guide content
            return {
                "results": self._get_static_guide_content(queries),
                "queries": queries,
                "note": f"Using static guide content. API error: {str(e)}"
            }

    def _query_guide_api(self, queries: str, max_results: int) -> List[str]:
        """Query the actual Simics guide API."""
        load_dotenv()
        
        api_key = os.getenv('API_KEY_GUIDE_WF')
        base_url = os.getenv('BASE_URL')
        
        if not api_key or not base_url:
            raise ValueError("API configuration not available")

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        query_list = [q.strip() for q in queries.split(',') if q.strip()]
        all_results = []

        for query in query_list:
            try:
                payload = {
                    "inputs": {"query": query},
                    "response_mode": "blocking",
                    "user": "simics-guide-agent"
                }

                response = requests.post(
                    f"{base_url}/workflows/run",
                    headers=headers,
                    json=payload,
                    timeout=60
                )

                response.raise_for_status()
                result_data = response.json()

                if 'data' in result_data and 'outputs' in result_data['data']:
                    text_results = result_data['data']['outputs'].get('text', [])
                    for item in text_results:
                        if isinstance(item, dict) and 'content' in item:
                            all_results.append(item['content'])

            except Exception:
                continue

        return all_results[:max_results]

    def _get_static_guide_content(self, queries: str) -> List[str]:
        """Return static Simics guide content."""
        static_content = [
            "Device modeling basics: Model only software-visible behavior, implement all registers accurately",
            "Register modeling: Use register templates with proper read/write methods and side effects",
            "Memory mapping: Devices are mapped into memory spaces using banks and register addresses",
            "Signal modeling: Use ports and interfaces for device interconnection and communication",
            "Event handling: Use events for asynchronous operations like timers and interrupts",
            "State management: Use attributes for device state that needs checkpointing",
            "DML compilation: Use Simics build system to compile DML into .so modules",
            "Testing approach: Write unit tests for device behavior and integration with Simics"
        ]
        
        query_words = queries.lower().split()
        filtered_content = []
        
        for content in static_content:
            if any(word in content.lower() for word in query_words):
                filtered_content.append(content)
        
        return filtered_content if filtered_content else static_content


class SimicsSearchDocsTool(BaseTool):
    """Tool for keyword-based search of Simics documentation."""

    def __init__(self):
        super().__init__(
            name="search_simics_docs",
            description="Search Simics documentation, API references, and manuals using keyword matching.",
        )
        
        # Load documentation index if available
        self.doc_data = self._load_doc_index()

    def _load_doc_index(self) -> Optional[Dict]:
        """Load documentation search index."""
        try:
            index_paths = [
                Path(__file__).parent / "simics_doc_search_index.json",
                Path("simics_doc_search_index.json"),
                Path(".") / "simics_doc_search_index.json"
            ]
            
            for path in index_paths:
                if path.exists():
                    with open(path, 'r', encoding='utf-8') as f:
                        return json.load(f)
        except Exception:
            pass
        return None

    def _get_declaration(self) -> Optional['types.FunctionDeclaration']:
        """Get function declaration for the LLM."""
        from google.genai import types
        return types.FunctionDeclaration(
            name="search_simics_docs",
            description="Search Simics documentation, API references, and manuals using keyword matching.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "keywords": types.Schema(
                        type=types.Type.STRING,
                        description="Comma-separated list of keywords or single keyword"
                    ),
                    "max_results": types.Schema(
                        type=types.Type.INTEGER,
                        description="Maximum number of results to return (default: 10)"
                    ),
                    "offset": types.Schema(
                        type=types.Type.INTEGER,
                        description="Offset for pagination (default: 0)"
                    )
                },
                required=["keywords"]
            )
        )

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: ToolContext
    ) -> Any:
        keywords = args.get("keywords", "")
        max_results = args.get("max_results", 10)
        offset = args.get("offset", 0)
        
        if self.doc_data:
            results = self._search_indexed_docs(keywords, max_results, offset)
        else:
            results = self._search_static_docs(keywords, max_results, offset)
        
        return {
            "results": results,
            "keywords": keywords,
            "total_results": len(results),
            "using_index": self.doc_data is not None
        }

    def _search_indexed_docs(self, keywords: str, max_results: int, offset: int) -> List[Dict]:
        """Search using loaded documentation index."""
        keyword_list = [k.strip().lower() for k in keywords.split(',') if k.strip()]
        results = []
        seen_urls = set()
        
        for document in self.doc_data.get('documents', []):
            doc_title = document.get('title', '')
            for page in document.get('pages', []):
                page_title = page.get('title', '')
                for section in page.get('sections', []):
                    section_title = section.get('title', '')
                    section_url = section.get('url', '')
                    section_text = section.get('text', '').lower()
                    
                    if any(keyword in section_text for keyword in keyword_list):
                        if section_url not in seen_urls:
                            seen_urls.add(section_url)
                            results.append({
                                'document_title': doc_title,
                                'page_title': page_title,
                                'section_title': section_title,
                                'section_url': section_url,
                                'text': section.get('text', '')
                            })
        
        return results[offset:offset + max_results]

    def _search_static_docs(self, keywords: str, max_results: int, offset: int) -> List[Dict]:
        """Search using static documentation content."""
        static_sections = [
            {
                'document_title': 'DML Language Reference',
                'page_title': 'Device Modeling',
                'section_title': 'Register Implementation',
                'text': 'Registers are the primary interface between software and device models. Use register templates with read_register() and write_register() methods.'
            },
            {
                'document_title': 'Model Builder Guide',
                'page_title': 'Basic Concepts',
                'section_title': 'Memory Mapping',
                'text': 'Device registers are mapped into memory spaces using banks. Each register has an address offset within the bank.'
            },
            {
                'document_title': 'Simics API Reference',
                'page_title': 'Interfaces',
                'section_title': 'Signal Interfaces',
                'text': 'Devices communicate through interfaces and ports. Use connect blocks to implement interface methods.'
            }
        ]
        
        keyword_list = [k.strip().lower() for k in keywords.split(',') if k.strip()]
        filtered_results = []
        
        for section in static_sections:
            text = section['text'].lower()
            if any(keyword in text for keyword in keyword_list):
                filtered_results.append(section)
        
        return filtered_results[offset:offset + max_results]


class SimicsAutoBuildTool(BaseTool):
    """Tool for building DML source files."""

    def __init__(self):
        super().__init__(
            name="auto_build",
            description="Compile DML source file to .so module using Simics build system.",
        )

    def _get_declaration(self) -> Optional['types.FunctionDeclaration']:
        """Get function declaration for the LLM."""
        from google.genai import types
        return types.FunctionDeclaration(
            name="auto_build",
            description="Compile DML source file to .so module using Simics build system.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "device_name": types.Schema(
                        type=types.Type.STRING,
                        description="Name of the device being built"
                    ),
                    "dml_path": types.Schema(
                        type=types.Type.STRING,
                        description="Path to the DML source file"
                    )
                },
                required=["device_name", "dml_path"]
            )
        )

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: ToolContext
    ) -> Any:
        device_name = args.get("device_name")
        dml_path = args.get("dml_path")
        
        if not device_name or not dml_path:
            return {"error": "device_name and dml_path are required"}
        
        try:
            # Read DML file content
            with open(dml_path, 'r', encoding='utf-8') as f:
                dml_content = f.read()
            
            if not dml_content.strip():
                return {"error": f"DML file is empty: {dml_path}"}
            
            # Try to use build service
            result = self._build_with_service(device_name, dml_content)
            return result
            
        except FileNotFoundError:
            return {"error": f"DML file not found: {dml_path}"}
        except Exception as e:
            return {"error": f"Build failed: {str(e)}"}

    def _build_with_service(self, device_name: str, dml_content: str) -> Dict:
        """Build using auto-build service."""
        load_dotenv()
        
        auto_build_srv = os.getenv("AUTO_BUILD_HOST_PORT")
        if not auto_build_srv:
            return {"error": "Auto build server not configured"}
        
        try:
            job_id = str(int(datetime.now().timestamp() * 1000))
            payload = {
                "device_name": device_name,
                "upload_code": dml_content,
                "job_id": job_id
            }
            
            response = requests.post(
                f"{auto_build_srv}/upload_code",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=300
            )
            
            response.raise_for_status()
            result_data = response.json()
            
            compile_status = result_data.get("compile_status")
            log = result_data.get("log", "No log available")
            
            if compile_status == 1:
                return {
                    "success": True,
                    "device_name": device_name,
                    "job_id": job_id,
                    "log": log,
                    "message": f"Build successful for device '{device_name}'"
                }
            else:
                return {
                    "success": False,
                    "device_name": device_name,
                    "job_id": job_id,
                    "log": log,
                    "message": f"Build failed for device '{device_name}'"
                }
                
        except requests.exceptions.Timeout:
            return {"error": "Build request timed out after 5 minutes"}
        except requests.exceptions.ConnectionError:
            return {"error": f"Could not connect to build server at {auto_build_srv}"}
        except Exception as e:
            return {"error": f"Build service error: {str(e)}"}


class SimicsAutoBuildByContentTool(BaseTool):
    """Tool for building DML content directly."""

    def __init__(self):
        super().__init__(
            name="auto_build_by_content",
            description="Compile DML source code directly to .so module using Simics build system.",
        )

    def _get_declaration(self) -> Optional['types.FunctionDeclaration']:
        """Get function declaration for the LLM."""
        from google.genai import types
        return types.FunctionDeclaration(
            name="auto_build_by_content",
            description="Compile DML source code directly to .so module using Simics build system.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "device_name": types.Schema(
                        type=types.Type.STRING,
                        description="Name of the device being built"
                    ),
                    "dml_content": types.Schema(
                        type=types.Type.STRING,
                        description="DML source code content"
                    )
                },
                required=["device_name", "dml_content"]
            )
        )

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: ToolContext
    ) -> Any:
        device_name = args.get("device_name")
        dml_content = args.get("dml_content")
        
        if not device_name or not dml_content:
            return {"error": "device_name and dml_content are required"}
        
        if not dml_content.strip():
            return {"error": "DML content is empty"}
        
        try:
            result = self._build_with_service(device_name, dml_content)
            return result
            
        except Exception as e:
            return {"error": f"Build failed: {str(e)}"}

    def _build_with_service(self, device_name: str, dml_content: str) -> Dict:
        """Build using auto-build service."""
        load_dotenv()
        
        auto_build_srv = os.getenv("AUTO_BUILD_HOST_PORT")
        if not auto_build_srv:
            return {"error": "Auto build server not configured"}
        
        try:
            job_id = str(int(datetime.now().timestamp() * 1000))
            payload = {
                "device_name": device_name,
                "upload_code": dml_content,
                "job_id": job_id
            }
            
            response = requests.post(
                f"{auto_build_srv}/upload_code",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=300
            )
            
            response.raise_for_status()
            result_data = response.json()
            
            compile_status = result_data.get("compile_status")
            log = result_data.get("log", "No log available")
            
            if compile_status == 1:
                return {
                    "success": True,
                    "device_name": device_name,
                    "job_id": job_id,
                    "log": log,
                    "message": f"Build successful for device '{device_name}'"
                }
            else:
                return {
                    "success": False,
                    "device_name": device_name,
                    "job_id": job_id,
                    "log": log,
                    "message": f"Build failed for device '{device_name}'"
                }
                
        except requests.exceptions.Timeout:
            return {"error": "Build request timed out after 5 minutes"}
        except requests.exceptions.ConnectionError:
            return {"error": f"Could not connect to build server at {auto_build_srv}"}
        except Exception as e:
            return {"error": f"Build service error: {str(e)}"}


class AgentOsToolset(BaseToolset):
    """Toolset containing all Agent OS tools."""

    def __init__(self):
        super().__init__()
        self.tools = [
            AgentOsReadTool(),
            AgentOsWriteTool(),
            AgentOsGrepTool(),
            AgentOsGlobTool(),
            AgentOsBashTool(),
            AgentOsTransferTool(),
            # Simics-specific tools
            SimicsGetDmlExampleTool(),
            SimicsQueryLibDocTool(),
            SimicsQueryGuideTool(),
            SimicsSearchDocsTool(),
            SimicsAutoBuildTool(),
            SimicsAutoBuildByContentTool(),
        ]

    async def get_tools(self, readonly_context=None) -> List[BaseTool]:
        """Return all tools in this toolset."""
        _ = readonly_context  # Mark as used to avoid linter warnings
        return self.tools

    @classmethod
    def from_config(cls, config, config_abs_path: str):
        """Create an AgentOsToolset from configuration.
        
        Args:
            config: The configuration object (unused for this simple toolset)
            config_abs_path: Absolute path to the config file (unused)
            
        Returns:
            AgentOsToolset: A new instance of the toolset
        """
        _ = config  # Mark as used to avoid linter warnings
        _ = config_abs_path  # Mark as used to avoid linter warnings
        return cls()


# Convenience function to create the toolset
def create_agent_os_toolset() -> AgentOsToolset:
    """Create an Agent OS toolset with all available tools."""
    return AgentOsToolset()
