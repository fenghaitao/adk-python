#!/usr/bin/env python3
"""
Rovodev Session Viewer
Usage: python view_rovodev_session.py <log_file>

Extracts session ID from log file and displays formatted session information.
"""

import json
import sys
import re
from datetime import datetime
from pathlib import Path


def extract_session_id_from_log(log_file):
    """Extract session ID from rovodev log file."""
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for session ID pattern
        pattern = r'Session ID:\s*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'
        match = re.search(pattern, content, re.IGNORECASE)
        
        if match:
            return match.group(1)
        
        # Try to find any UUID in the log
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        matches = re.findall(uuid_pattern, content)
        if matches:
            return matches[-1]  # Return last UUID found
        
        return None
    except Exception as e:
        print(f"❌ Error reading log file: {e}")
        return None


def format_timestamp(timestamp_str):
    """Format timestamp string to readable format."""
    try:
        if not timestamp_str:
            return "N/A"
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return str(timestamp_str)


def truncate_text(text, max_length=100):
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def view_rovodev_session(log_file):
    """View rovodev session from log file."""
    log_path = Path(log_file)
    
    if not log_path.exists():
        print(f"❌ Log file not found: {log_file}")
        return
    
    # Extract session ID from log
    session_id = extract_session_id_from_log(log_file)
    
    if not session_id:
        print(f"❌ Could not extract session ID from log file: {log_file}")
        return
    
    # Find session directory
    sessions_dir = Path.home() / ".rovodev" / "sessions" / session_id
    
    if not sessions_dir.exists():
        print(f"❌ Session directory not found: {sessions_dir}")
        return
    
    # Read session context
    session_file = sessions_dir / "session_context.json"
    
    if not session_file.exists():
        print(f"❌ Session context file not found: {session_file}")
        return
    
    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            session = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in session file: {e}")
        return
    
    # Create output file
    output_file = log_path.parent / f"{log_path.stem}.txt"
    
    # Generate report
    with open(output_file, 'w', encoding='utf-8') as out:
        # Header
        out.write("=" * 80 + "\n")
        out.write(f"ROVODEV SESSION REPORT\n")
        out.write("=" * 80 + "\n")
        out.write(f"Log File: {log_file}\n")
        out.write(f"Session ID: {session_id}\n")
        out.write(f"Session Dir: {sessions_dir}\n")
        out.write(f"\n")
        
        # Message history
        message_history = session.get('message_history', [])
        out.write(f"Total Messages: {len(message_history)}\n")
        out.write(f"\n")
        
        # Process messages
        out.write("=" * 80 + "\n")
        out.write("CONVERSATION\n")
        out.write("=" * 80 + "\n")
        out.write(f"\n")
        
        for i, msg in enumerate(message_history, 1):
            parts = msg.get('parts', [])
            kind = msg.get('kind', 'unknown')
            timestamp = msg.get('timestamp', '')
            
            if kind == 'request':
                out.write(f"[USER] Message {i}\n")
                if timestamp:
                    out.write(f"   Time: {format_timestamp(timestamp)}\n")
                
                # Extract all parts from request
                for part in parts:
                    part_kind = part.get('part_kind', '')
                    content = part.get('content', '')
                    
                    if part_kind == 'user-prompt' and content.strip():
                        # Skip iteration count messages
                        if not content.strip().startswith('You have used'):
                            out.write(f"   Prompt: {truncate_text(content, 200)}\n")
                    
                    elif part_kind == 'tool-return':
                        tool_name = part.get('tool_name', 'unknown')
                        tool_call_id = part.get('tool_call_id', 'unknown')
                        
                        # Show tool result
                        out.write(f"   Tool Result [{tool_name}]:\n")
                        if content:
                            # Handle both string and list content
                            if isinstance(content, list):
                                # If it's a list, join items
                                content_str = '\n'.join(str(item) for item in content)
                            else:
                                content_str = str(content)
                            
                            # Show first few lines of content
                            lines = content_str.split('\n')
                            preview_lines = lines[:5]  # Show first 5 lines
                            for line in preview_lines:
                                out.write(f"      {truncate_text(line, 150)}\n")
                            if len(lines) > 5:
                                out.write(f"      ... ({len(lines) - 5} more lines)\n")
                        else:
                            out.write(f"      (no content)\n")
                
                out.write(f"\n")
            
            elif kind == 'response':
                out.write(f"[ASSISTANT] Message {i}\n")
                
                # Extract response content
                for part in parts:
                    part_kind = part.get('part_kind', '')
                    
                    if part_kind == 'text':
                        content = part.get('content', '')
                        if content:
                            out.write(f"   {truncate_text(content, 200)}\n")
                    
                    elif part_kind == 'tool-call':
                        tool_name = part.get('tool_name', 'unknown')
                        out.write(f"   Tool: {tool_name}\n")
                
                # Show usage if available
                usage = msg.get('usage', {})
                if usage:
                    input_tokens = usage.get('input_tokens', 0)
                    output_tokens = usage.get('output_tokens', 0)
                    cache_read = usage.get('cache_read_tokens', 0)
                    
                    out.write(f"   Tokens: input={input_tokens}, output={output_tokens}")
                    if cache_read > 0:
                        out.write(f", cache_read={cache_read}")
                    out.write(f"\n")
                
                out.write(f"\n")
        
        # Summary
        out.write("=" * 80 + "\n")
        out.write("SESSION SUMMARY\n")
        out.write("=" * 80 + "\n")
        out.write(f"\n")
        
        # Count message types
        requests = sum(1 for msg in message_history if msg.get('kind') == 'request')
        responses = sum(1 for msg in message_history if msg.get('kind') == 'response')
        
        out.write(f"User Messages: {requests}\n")
        out.write(f"Assistant Messages: {responses}\n")
        out.write(f"Total Messages: {len(message_history)}\n")
        out.write(f"\n")
        
        # Token usage summary
        total_input = 0
        total_output = 0
        total_cache_read = 0
        
        for msg in message_history:
            usage = msg.get('usage', {})
            total_input += usage.get('input_tokens', 0)
            total_output += usage.get('output_tokens', 0)
            total_cache_read += usage.get('cache_read_tokens', 0)
        
        if total_input > 0 or total_output > 0:
            out.write(f"Total Input Tokens: {total_input:,}\n")
            out.write(f"Total Output Tokens: {total_output:,}\n")
            if total_cache_read > 0:
                out.write(f"Total Cache Read Tokens: {total_cache_read:,}\n")
            out.write(f"Total Tokens: {total_input + total_output:,}\n")
        
        out.write(f"\n")
        out.write("=" * 80 + "\n")
        out.write("Report complete\n")
        out.write("=" * 80 + "\n")
    
    print(f"✅ Session report saved to: {output_file}")
    
    # Also print to console
    print(f"\n" + "=" * 80)
    print(f"ROVODEV SESSION: {session_id}")
    print("=" * 80)
    print(f"Total Messages: {len(message_history)}")
    print(f"User Messages: {requests}")
    print(f"Assistant Messages: {responses}")
    if total_input > 0 or total_output > 0:
        print(f"Total Tokens: {total_input + total_output:,}")
    print(f"\nFull report: {output_file}")
    print("=" * 80)


def main():
    if len(sys.argv) != 2:
        print("Usage: python view_rovodev_session.py <log_file>")
        print("\nExample:")
        print("  python view_rovodev_session.py rovodev-apply/rovodev-apply_20251228_045040.log")
        sys.exit(1)
    
    log_file = sys.argv[1]
    view_rovodev_session(log_file)


if __name__ == "__main__":
    main()
