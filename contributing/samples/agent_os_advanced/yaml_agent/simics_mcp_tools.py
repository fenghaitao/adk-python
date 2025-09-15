import json
import re
from typing import List, Dict, Any

import os
from pathlib import Path
from dotenv import load_dotenv
import requests
from datetime import datetime
import argparse
import asyncio
from fastmcp import FastMCP
from string import Template
import subprocess

FILE_BASE_DIR = Path(__file__).resolve().parent
load_dotenv()

SIMICS_KW_SEARCH_DOCS_PATH = FILE_BASE_DIR / "simics_doc_search_index.json"
SIMICS_KW_SEARCH_DOCS_PATH_LINUX = SIMICS_KW_SEARCH_DOCS_PATH
DOCUMENT_DATA = None

INITIAL_PROMPT_PATH = FILE_BASE_DIR / "ini_prompt.md"
INITIAL_PROMPT_PATH_LINUX = INITIAL_PROMPT_PATH
INITIAL_PROMPT = None

DML_TPL_PATH = FILE_BASE_DIR / "dml-tpl.dml"
DML_TPL_PATH_LINUX = DML_TPL_PATH
DML_TEMPLATE = None

try:
    with open(SIMICS_KW_SEARCH_DOCS_PATH, 'r', encoding='utf-8') as file:
        DOCUMENT_DATA = json.load(file)
except FileNotFoundError:
    try:
        with open(SIMICS_KW_SEARCH_DOCS_PATH_LINUX, 'r', encoding='utf-8') as file:
            DOCUMENT_DATA = json.load(file)
    except FileNotFoundError:
        print("WARNING Windows simics doc json not found, ignoring...")

try:
    with open(INITIAL_PROMPT_PATH, 'r', encoding='utf-8') as file:
        INITIAL_PROMPT = file.read()
except FileNotFoundError:
    try:
        with open(INITIAL_PROMPT_PATH_LINUX, 'r', encoding='utf-8') as file:
            INITIAL_PROMPT = file.read()
    except FileNotFoundError:
        print("WARNING Windows simics doc json not found, ignoring...")
        
try:
    with open(DML_TPL_PATH, 'r', encoding='utf-8') as file:
        DML_TEMPLATE = file.read()
except:
    with open(DML_TPL_PATH_LINUX, 'r', encoding='utf-8') as file:
        DML_TEMPLATE = file.read()


##################################################################
# simics guide dify KB retrieval
##################################################################

def query_guide(query_list: list, wf = "guide") -> list:
    """
    Query the Dify workflow guide with a list of queries, deduplicate results by segment_id
    
    Args:
        query_list: List of query strings to process
        
    Returns:
        List of deduplicated results from the workflow
    """
    api_key_map = {
        "guide": os.getenv('API_KEY_GUIDE_WF'),
        "utility_doc": os.getenv('API_KEY_UTILITY_WF')
    }
    if wf not in api_key_map:
        raise ValueError("WF not found")
    # Get API key from environment
    api_key = api_key_map[wf]
    base_url = os.getenv('BASE_URL')
    if not base_url:
        raise ValueError("BASE_URL not found in environment variables")

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    all_results = []
    seen_segment_ids = set()
    
    for query in query_list:
        try:
            # Prepare request payload
            payload = {
                "inputs": {
                    "query": 
                        query
                },
                "response_mode": "blocking",
                "user": "simics-guide-agent"
            }
            
            # Make request to workflow API
            response = requests.post(
                f"{base_url}/workflows/run",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            result_data = response.json()
            
            # Extract text results from the workflow output
            if 'data' in result_data and 'outputs' in result_data['data']:
                text_results = result_data['data']['outputs'].get('text', [])
                
                # Process and deduplicate results
                for item in text_results:
                    if isinstance(item, dict) and 'metadata' in item:
                        segment_id = item['metadata'].get('segment_id')
                        
                        # Only add if we haven't seen this segment_id before
                        if segment_id and segment_id not in seen_segment_ids:
                            seen_segment_ids.add(segment_id)
                            # Add query information to track which query produced this result
                            item['source_query'] = query
                            all_results.append(item)
            
            print(f">>> [query_guide] Processed query: '{query}' - Found {len(text_results)} results")
            
        except requests.exceptions.RequestException as e:
            print(f">>> [query_guide] Error processing query '{query}': {str(e)}")
            continue
        except Exception as e:
            print(f">>> [query_guide] Unexpected error for query '{query}': {str(e)}")
            continue
    
    print(f"Total unique results after deduplication: {len(all_results)}")
    all_results = [x["content"] for x in all_results]
    return all_results

def format_guide_results(results: list, max_results: int = 10) -> str:
    """
    Format guide results for display
    
    Args:
        results: List of guide results from query_guide
        max_results: Maximum number of results to format
        
    Returns:
        Formatted string representation of the results
    """
    if not results:
        return "No results found."
    
    formatted = f"Found {len(results)} unique results:\n\n"

    HARD_MAX = 10
    for i, result in enumerate(results):
        formatted += f"=== Result {i+1} ===\n"

        content = result
        content_preview = content
        formatted += f"Content: {content_preview}\n\n"
    
    # if len(results) > max_results:
    #     formatted += f"... and {len(results) - max_results} more results\n"
    
    return formatted

def q_guide(queries: str, max_results: int = 5, wf = "guide") -> str:
    """
    Query the Simics guide with one or more queries
    
    Args:
        queries: Comma-separated list of queries or single query
        max_results: Maximum number of results to return
        
    Returns:
        Formatted results from the Simics guide
    """
    try:
        # Parse queries - support both single query and comma-separated list
        if ',' in queries:
            query_list = [q.strip() for q in queries.split(',') if q.strip()]
        else:
            query_list = [queries.strip()]
        
        results = query_guide(query_list, wf)
        return format_guide_results(results, max_results)
        
    except Exception as e:
        return f"Error querying Simics guide: {str(e)}"

def create_simics_guide_tool():
    """
    Create a tool for querying the Simics guide
    - NOT A PART OF THE MCP SERVER -
    """
    parameters = [
        ToolParameter("queries", "string", "Comma-separated list of one or more short queries for the Simics guide. One call with several queries should be used instead of several calls of one query.", required=True),
        ToolParameter("max_results", "number", "Maximum number of results to return (default: 5)", required=False)
    ]
    
    return (lambda q, m: q_guide(q, m)), parameters

##################################################################
# simics doc keyword search
##################################################################

def search_documents(documents_data: Dict[str, Any], keyword: str, case_sensitive: bool = False) -> List[Dict[str, str]]:
    """
    Search for a keyword in the document structure and return matching sections.
    
    Args:
        documents_data: The JSON data containing documents structure
        keyword: The keyword to search for
        case_sensitive: Whether the search should be case sensitive (default: False)
    
    Returns:
        List of dictionaries containing search results with document_title, page_title, 
        section_title, section_url, and text fields
    """
    results = []
    
    # Prepare keyword for searching
    search_keyword = keyword if case_sensitive else keyword.lower()
    
    # Iterate through documents
    for document in documents_data.get('documents', []):
        document_title = document.get('title', '')
        
        # Iterate through pages in each document
        for page in document.get('pages', []):
            page_title = page.get('title', '')
            
            # Iterate through sections in each page
            for section in page.get('sections', []):
                section_title = section.get('title', '')
                section_url = section.get('url', '')
                section_text = section.get('text', '')
                
                # Perform keyword search
                search_text = section_text if case_sensitive else section_text.lower()
                
                if search_keyword in search_text:
                    results.append({
                        'document_title': document_title,
                        'page_title': page_title,
                        'section_title': section_title,
                        'section_url': section_url,
                        'text': section_text
                    })
    
    return results


def search_multiple_keywords(documents_data: Dict[str, Any], keywords: List[str], case_sensitive: bool = False) -> List[Dict[str, str]]:
    """
    Search for multiple keywords in the document structure and return deduplicated matching sections.
    
    Args:
        documents_data: The JSON data containing documents structure
        keywords: List of keywords to search for
        case_sensitive: Whether the search should be case sensitive (default: False)
    
    Returns:
        List of deduplicated dictionaries containing search results
    """
    all_results = []
    seen_urls = set()
    
    for keyword in keywords:
        results = search_documents(documents_data, keyword, case_sensitive)
        
        # Deduplicate by section_url
        for result in results:
            section_url = result.get('section_url', '')
            if section_url and section_url not in seen_urls:
                seen_urls.add(section_url)
                # Add source keyword to track which keyword produced this result
                result['source_keyword'] = keyword
                all_results.append(result)
    
    return all_results

def format_doc_search_results(results: List[Dict[str, str]], max_results: int = 10, offset: int = 0) -> str:
    """
    Format document search results for display
    
    Args:
        results: List of document search results
        max_results: Maximum number of results to format
        
    Returns:
        Formatted string representation of the results
    """
    if not results:
        return "No results found."
    
    if offset >= len(results):
        return "No more results! Your offset exceeds the length of all results."
    
    formatted = f"Showing Result {offset} to {offset + max_results - 1} ({len(results)} in total) unique document sections:\n\n"
    
    for i, result in enumerate(results[offset:offset + max_results]):
        formatted += f"=== Result {i+1} ===\n"
        formatted += f"Document: {result.get('document_title', 'N/A')}\n"
        formatted += f"Page: {result.get('page_title', 'N/A')}\n"
        formatted += f"Section: {result.get('section_title', 'N/A')}\n"
        # formatted += f"URL: {result.get('section_url', 'N/A')}\n"
        
        if 'source_keyword' in result:
            formatted += f"Matched Keyword: {result['source_keyword']}\n"
        
        text = result.get('text', '')
        # Truncate text if too long
        # if len(text) > 300:
        #     text = text[:300] + "..."
        formatted += f"Text: {text}\n\n"
    
    # if len(results) > max_results:
    #     formatted += f"... and {len(results) - (offset + max_results)} more results\n"
    
    return formatted

def create_doc_kw_search_tool():
    """
    Create a tool for keyword searching in Simics documentation
    - NOT A PART OF MCP SERVER -
    """
    def search_simics_docs(keywords: str, max_results: int = 10) -> str:
        """
        Search Simics documentation for keywords
        
        Args:
            keywords: Comma-separated list of keywords or single keyword
            max_results: Maximum number of results to return
            
        Returns:
            Formatted results from the Simics documentation search
        """
        try:
            # Parse keywords - support both single keyword and comma-separated list
            if ',' in keywords:
                keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
            else:
                keyword_list = [keywords.strip()]

            results = search_multiple_keywords(DOCUMENT_DATA, keyword_list, False)
            return format_doc_search_results(results, max_results)
        except Exception as e:
            return f"Error reading documentation file: {str(e)}"
    
    parameters = [
        ToolParameter("keywords", "string", "Comma-separated list of one or more keywords for searching all simics documentations. One call with several keywords should be used instead of several calls of one keyword.", required=True),
        ToolParameter("max_results", "number", "Maximum number of results to return (default: 10)", required=False)
    ]
    
    return search_simics_docs, parameters

##################################################################
# FastMCP Server Setup
##################################################################

# Initialize FastMCP server
mcp = FastMCP("Simics Documentation Server")

def _init_prompt(req: str):
    template = Template(INITIAL_PROMPT)
    formatted = template.substitute(req=req)
    return formatted

@mcp.prompt
def simics_init_prompt(req: str) -> str:
    """
    Initial prompt template for the Simics Documentation Server.
    
    This prompt establishes the AI assistant's role and capabilities for helping with Simics-related queries.
    """
    return _init_prompt(req)

@mcp.tool()
def query_simics_guide(queries: str, max_results: int = 5) -> str:
    """
    Semantically query the Simics documentation and concept guides. Use when you want to get know of a unfamiliar concept by ambiguous query or natural language. Can be used as a bootstrap.
    Documentation contained:
    - **Full DML 1.4 language specification**
    - **Model Builder User's Guide**, which focuses on modeling the behavior of a system. It contains:
        - *Introduction and Preparation*: Provides an overview of the way you model your hardware in Simics and how to map hardware concepts to Simics concepts.
        - *Basic Modeling Concepts*: The concepts of system modeling and how they map to modeling in Simics.
        - *Device Modeling*: Describes the device modeling concepts and introduces DML, the tool used for writing device models. Also includes chapters on writing new commands for the Simics CLI and how to define new interfaces between device models.
        - *Modeling Common Hardware Components*: Shows you how to model some common kinds of devices in Simics.
        - *Creating Virtual Systems*: Assembling the parts of a virtual system into a complete system. It also shows you how to deal with memory and address spaces in Simics. This is one of the most abstract parts of modeling a system in Simics and tries to map how software sees the hardware.
        - *Simics API*: Explain Simics API's major concepts, how it is structured, how it evolves, and some rules and conventions for how to use it. It also explains how the API interacts with Simics's multithreading support, and how to make your modules safe to use in multithreaded simulations.
    
    Args:
        queries: Comma-separated list of queries or single query
        max_results: Maximum number of results to return
        
    Returns:
        Formatted results from the Simics guide
    """
    try:
        res = q_guide(queries, max_results)
        return res
    except Exception as e:
        return f"Error querying Simics guide: {str(e)}"

@mcp.tool()
def get_dml_example() -> str:
    """
    Get the DML file example. This is the same as the DML template provided to you in the first message.
    Use this tool to recall the correct syntax of DML file.
        
    Returns:
        The content of the DML example.
    """
    return DML_TEMPLATE

@mcp.tool()
def query_lib_doc(queries: str, max_results: int = 5) -> str:
    """
    Semantically query the Device Modeling Language documentation of the
    names, parameters and description of:
    - built-in templates, functions, methods, object attributes, object methods.
    - standard templates in `utility.dml`.
    - more about Simics library

    You can find usable templates, descriptions and methods of attributes, banks, connect,
    interface, port, subdevice, implement, registers, fields and events.

    Also suitable for keyword search as the doc contains many keywords.
    
    Args:
        queries: Comma-separated list of queries or single query
        max_results: Maximum number of results to return
        
    Returns:
        Formatted results from the Simics guide
    """
    try:
        res = q_guide(queries, max_results, "utility_doc")
        return res
    except Exception as e:
        return f"Error querying Utility doc: {str(e)}"

@mcp.tool()
def search_simics_docs(keywords: str, max_results: int = 10, offset: int = 0) -> str:
    """
    Search the full Simics documentation, API documentation, guides, code snippets and manuals by keyword match.
    You can search for a keyword here to get the descriptive content of it.
    
    Args:
        keywords: Comma-separated list of keywords or single keyword
        max_results: Maximum number of results to return
        offset: The offset of the results. Useful when you want to view more results of one set of keywords. This tool returns results[offset:offset + max_results]
        
    Returns:
        Formatted results from the Simics documentation search
    """
    try:
        # Parse keywords - support both single keyword and comma-separated list
        if ',' in keywords:
            keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
        else:
            keyword_list = [keywords.strip()]

        results = search_multiple_keywords(DOCUMENT_DATA, keyword_list, False)
        return format_doc_search_results(results, max_results, offset)
    except Exception as e:
        return f"Error reading documentation file: {str(e)}"

def _auto_build(device_name: str, dml_path: str) -> str:
    # Read the DML file content
    try:
        with open(dml_path, 'r', encoding='utf-8') as file:
            dml_content = file.read()
        if len(dml_content) == 0:
            raise FileNotFoundError
    except FileNotFoundError:
        return f"Error: DML file not found or is empty at path: {dml_path}. If you are LLM Agent, maybe the user hasn't accept your code, which causes the file to be empty."
    except Exception as e:
        return f"Error reading DML file: {str(e)}"

    return __auto_build(device_name, dml_content)


def auto_build_srv_req(payload: dict, path: str = "/upload_code") -> dict:
    """
    Send a POST request to the auto build server with the given payload.
    Returns the parsed JSON response, or raises an exception on error.
    """
    auto_build_srv = os.getenv("AUTO_BUILD_HOST_PORT")
    if not auto_build_srv or len(auto_build_srv) == 0:
        raise ConnectionError("Auto build server is not available now.")

    try:
        response = requests.post(
            f"{auto_build_srv}{path}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=300  # 5 minutes timeout for build process
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        raise TimeoutError("Build request timed out after 5 minutes.")
    except requests.exceptions.ConnectionError:
        raise ConnectionError(f"Could not connect to build server at {auto_build_srv}. Make sure the server is running.")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Request failed - {str(e)}")
    except ValueError as e:
        raise ValueError(f"Invalid JSON response from server - {str(e)}")

def __auto_build(device_name: str, dml_content: str) -> str:
    try:
        job_id = str(int(datetime.now().timestamp() * 1000))  # milliseconds for uniqueness
        payload = {
            "device_name": device_name,
            "upload_code": dml_content,
            "job_id": job_id
        }
        try:
            response_data = auto_build_srv_req(payload, "/upload_code")
            compile_status = response_data.get("compile_status")
            if compile_status == 1:  # SUCCESS_BUILD = 1
                build_log = response_data.get("log", "No log available")
                return f"Build successful for device '{device_name}' (Job ID: {job_id})\n\nBuild Log:\n{build_log}"
            else:  # FAILED_BUILD = -1
                error_log = response_data.get("log", "No error log available")
                return f"Build failed for device '{device_name}' (Job ID: {job_id})\n\nError Log:\n{error_log}"
        except TimeoutError:
            return f"Error: Build request timed out after 5 minutes for device '{device_name}'"
        except ConnectionError as ce:
            return f"Error: {str(ce)} Ask for user's help if this is still not available after several tries."
        except Exception as e:
            return f"Error: {str(e)}"
    except Exception as e:
        return f"Auto Build service is not available now. Error in auto_build function: {str(e)}"

@mcp.tool()
def auto_build(device_name: str, dml_path: str) -> str:
    """
    Automatically build a Simics device by reading DML code from a file and sending it to the build server.
    The returned result is the stdout and stderr of the build server.
    You should call this tool after you implemented the device to check if any error occurs.
    
    Args:
        device_name: The name of the device
        dml_path: Path to the DML file containing the device code
        
    Returns:
        Build log if successful, or error message if failed
    """
    return _auto_build(device_name, dml_path)

@mcp.tool()
def auto_build_by_content(device_name: str, dml_content: str) -> str:
    """
    You should NOT call this tool unless your previous call of `auto_build` failed. Otherwise, use `auto_build` tool.
    Same as `auto_build`, but you provide the DML content directly instead of a file path.
    
    Args:
        device_name: The name of the device
        dml_content: Content of device code
        
    Returns:
        Build log if successful, or error message if failed
    """
    return __auto_build(device_name, dml_content)

def _run_test_runner(test_path: str) -> str:
    try:
        payload = {"test_path": test_path}
        response = auto_build_srv_req(payload, "/vp")
        return response.get("result", "No result returned from build server.")
    except Exception as e:
        return f"Error running test-runner: {str(e)}"

# @mcp.tool()
# def run_test_runner(test_path: str) -> str:
#     """
#     Run the unit test specified by `test_path`. The path is relative to the path in environment variable `VP_PROJ_ABS_PATH`.
#     Returns the combined stdout and stderr output.
    
#     Args:
#         test_path: Path to the test file to run with test-runner.
        
#     Returns:
#         Combined stdout and stderr output from the test-runner command.
#     """
#     return _run_test_runner(test_path)


def test_auto_build():
    """Test function for auto_build tool."""
    # Set these variables to your test values
    test_device_name = "wdt"
    test_dml_path = "/home/sy/simicsAI/watchdog.dml"
    
    result = _auto_build(test_device_name, test_dml_path)
    print("auto_build result:")
    print(result)

def main():
    """Main function to run the MCP server"""

    # MCP server pre-checks

    # Check if DOCUMENT_DATA, INITIAL_PROMPT and DML_TEMPLATE are not None
    if DOCUMENT_DATA is None:
        print("ERROR: DOCUMENT_DATA is not loaded. Please check the path of simics_doc_search_index.json.")
        exit(1)
    if INITIAL_PROMPT is None:
        print("ERROR: INITIAL_PROMPT is not loaded. Please check the path of ini_prompt.md.")
        exit(1)
    if DML_TEMPLATE is None:
        print("ERROR: DML_TEMPLATE is not loaded. Please check the path of dml-tpl.dml.")
        exit(1)
    
    # vp_proj_path = os.getenv("VP_PROJ_ABS_PATH")
    # if not vp_proj_path:
    #     print("Error: VP_PROJ_ABS_PATH environment variable is not set.")
    #     exit(1)

    # Check required environment variables
    required_env_vars = ["API_KEY_GUIDE_WF", "API_KEY_UTILITY_WF", "BASE_URL"]
    missing_env = [var for var in required_env_vars if not os.getenv(var)]
    if missing_env:
        print(f"ERROR: Missing required environment variables: {', '.join(missing_env)}")
        exit(1)

    # Check no_proxy
    if not os.getenv("no_proxy"):
        print("WARNING: no_proxy is not set. This may cause issues with API requests. This MCP server should access only the Intel internal network.")

    # Check AUTO_BUILD_HOST_PORT
    if not os.getenv("AUTO_BUILD_HOST_PORT"):
        print("WARNING: Auto build server is not available.")
    
    print(f"Simics AI Tools MCP Server")

    
    try:
        # Run the FastMCP server
        mcp.run()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    # print(_init_prompt("test"))
    
    # test_auto_build()
    main()

    # print(q_guide("init", 5, "utility_doc"))
    # print(_run_test_runner("test/unit-tests/watchdog/s-reset.py"))