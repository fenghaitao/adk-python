#!/usr/bin/env python3
"""
Simple ADK Session Viewer
Usage: python view_session.py session_file.json
"""

import json
import sys
from datetime import datetime
from pathlib import Path

def format_timestamp(timestamp_str):
    """Format ISO timestamp to readable format."""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return timestamp_str

def extract_text_content(content):
    """Extract text from content parts."""
    if not content or not content.get('parts'):
        return "[No content]"
    
    texts = []
    function_calls = []
    
    for part in content['parts']:
        if part.get('text'):
            texts.append(part['text'])
        elif part.get('inline_data'):
            texts.append(f"[Media: {part['inline_data'].get('mime_type', 'unknown')}]")
        elif part.get('function_call'):
            # Extract function call details
            func_call = part['function_call']
            func_name = func_call.get('name', 'unknown_function')
            func_args = func_call.get('args', {})
            
            # Format function call nicely
            if func_args:
                args_str = ', '.join([f"{k}={v}" for k, v in func_args.items()])
                function_calls.append(f"🔧 {func_name}({args_str})")
            else:
                function_calls.append(f"🔧 {func_name}()")
        elif part.get('function_response'):
            # Extract function response details
            func_resp = part['function_response']
            func_name = func_resp.get('name', 'unknown_function')
            response = func_resp.get('response', {})
            
            # Format response - handle different response types
            if isinstance(response, dict):
                if 'result' in response:
                    result = response['result']
                    if isinstance(result, str) and len(result) > 200:
                        result = result[:200] + "..."
                    function_calls.append(f"📤 {func_name} → {result}")
                elif 'error' in response:
                    function_calls.append(f"❌ {func_name} → Error: {response['error']}")
                else:
                    # Generic response display
                    resp_str = str(response)
                    if len(resp_str) > 200:
                        resp_str = resp_str[:200] + "..."
                    function_calls.append(f"📤 {func_name} → {resp_str}")
            else:
                resp_str = str(response)
                if len(resp_str) > 200:
                    resp_str = resp_str[:200] + "..."
                function_calls.append(f"📤 {func_name} → {resp_str}")
    
    # Combine text and function calls
    all_content = []
    if texts:
        all_content.extend(texts)
    if function_calls:
        all_content.extend(function_calls)
    
    return '\n'.join(all_content) if all_content else "[No content]"

def view_session(session_file):
    """View session in a formatted way."""
    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            session = json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {session_file}")
        return
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return

    # Session info
    print("=" * 80)
    print(f"📋 SESSION: {session_file}")
    print("=" * 80)
    print(f"App Name: {session.get('app_name', 'N/A')}")
    print(f"User ID: {session.get('user_id', 'N/A')}")
    print(f"Session ID: {session.get('id', 'N/A')}")
    print(f"Created: {format_timestamp(session.get('created_time', 'N/A'))}")
    print(f"Updated: {format_timestamp(session.get('updated_time', 'N/A'))}")
    
    # State info
    if session.get('state'):
        print(f"State: {len(session['state'])} items")
    
    # Events
    events = session.get('events', [])
    print(f"Events: {len(events)} total")
    print()

    # Show conversation
    print("=" * 80)
    print("💬 CONVERSATION")
    print("=" * 80)
    
    for i, event in enumerate(events, 1):
        author = event.get('author', 'unknown')
        timestamp = format_timestamp(event.get('created_time', ''))
        content = extract_text_content(event.get('content'))
        
        # Format based on author
        if author == 'user':
            icon = "👤"
            color_start = "\033[94m"  # Blue
        else:
            icon = "🤖"
            color_start = "\033[92m"  # Green
        
        color_end = "\033[0m"  # Reset
        
        print(f"{color_start}{icon} [{author}] {timestamp}{color_end}")
        
        # Indent content
        for line in content.split('\n'):
            if line.strip():
                print(f"   {line}")
        
        # Actions if any
        if event.get('actions'):
            actions = event['actions']
            if actions.get('state_delta'):
                state_delta = actions['state_delta']
                print(f"   📝 State update: {len(state_delta)} changes")
                # Show some state changes (truncated)
                for key, value in list(state_delta.items())[:3]:
                    value_str = str(value)
                    if len(value_str) > 100:
                        value_str = value_str[:100] + "..."
                    print(f"      {key}: {value_str}")
                if len(state_delta) > 3:
                    print(f"      ... and {len(state_delta) - 3} more changes")
        
        # Show any additional metadata
        if event.get('invocation_id'):
            print(f"   🆔 Invocation: {event['invocation_id']}")
        
        if event.get('branch'):
            print(f"   🌿 Branch: {event['branch']}")
        
        print()  # Blank line between events

    print("=" * 80)
    print("✅ Session view complete")
    print("=" * 80)

def main():
    if len(sys.argv) != 2:
        print("Usage: python view_session.py <session_file.json>")
        print("\nExample:")
        print("  python view_session.py specify_agent/myproject_specify.session.json")
        sys.exit(1)
    
    session_file = sys.argv[1]
    if not Path(session_file).exists():
        print(f"❌ File not found: {session_file}")
        print("\nAvailable session files:")
        for pattern in ["*/*.session.json", "*.session.json"]:
            for file in Path(".").glob(pattern):
                print(f"  {file}")
        sys.exit(1)
    
    view_session(session_file)

if __name__ == "__main__":
    main()