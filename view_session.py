#!/usr/bin/env python3
"""
Simple ADK Session Viewer
Usage: python view_session.py session_file.json
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

def format_timestamp(timestamp):
    """Format timestamp (ISO string or Unix float) to readable format."""
    try:
        if isinstance(timestamp, (int, float)):
            # Unix timestamp
            dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        elif isinstance(timestamp, str):
            # ISO format string
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return str(timestamp)
    except:
        return str(timestamp)

def format_duration(duration_seconds):
    """Format duration in seconds to human-readable format."""
    if duration_seconds < 60:
        return f"{duration_seconds:.1f} seconds"
    elif duration_seconds < 3600:
        minutes = duration_seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = duration_seconds / 3600
        return f"{hours:.1f} hours"

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
    
    # Handle last_update_time if present
    if 'last_update_time' in session:
        last_update = session['last_update_time']
        print(f"Last Update: {format_timestamp(last_update)}")
        if 'last_update_time_human' in session:
            print(f"Last Update (Human): {session['last_update_time_human']}")
    
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
    
    # Pre-calculate event durations
    event_durations = []
    for i in range(len(events)):
        current_event = events[i]
        current_timestamp = current_event.get('created_time') or current_event.get('timestamp')
        
        if current_timestamp and i > 0:
            # Get previous event timestamp
            prev_event = events[i-1]
            prev_timestamp = prev_event.get('created_time') or prev_event.get('timestamp')
            
            if prev_timestamp:
                # Convert both to Unix timestamps for calculation
                current_unix = current_timestamp if isinstance(current_timestamp, (int, float)) else None
                prev_unix = prev_timestamp if isinstance(prev_timestamp, (int, float)) else None
                
                # Handle ISO format conversion if needed
                if current_unix is None and isinstance(current_timestamp, str):
                    try:
                        dt = datetime.fromisoformat(current_timestamp.replace('Z', '+00:00'))
                        current_unix = dt.timestamp()
                    except:
                        pass
                
                if prev_unix is None and isinstance(prev_timestamp, str):
                    try:
                        dt = datetime.fromisoformat(prev_timestamp.replace('Z', '+00:00'))
                        prev_unix = dt.timestamp()
                    except:
                        pass
                
                # Calculate duration
                if current_unix and prev_unix:
                    duration = current_unix - prev_unix
                    event_durations.append(duration)
                else:
                    event_durations.append(None)
            else:
                event_durations.append(None)
        else:
            event_durations.append(None)  # First event has no duration
    
    for i, event in enumerate(events, 1):
        author = event.get('author', 'unknown')
        # Handle both created_time and timestamp fields
        event_timestamp = event.get('created_time') or event.get('timestamp', '')
        timestamp = format_timestamp(event_timestamp)
        content = extract_text_content(event.get('content'))
        
        # Get duration for this event
        duration = event_durations[i-1] if i-1 < len(event_durations) else None
        
        # Format based on author
        if author == 'user':
            icon = "👤"
            color_start = "\033[94m"  # Blue
        else:
            icon = "🤖"
            color_start = "\033[92m"  # Green
        
        color_end = "\033[0m"  # Reset
        
        # Format the header with duration
        if duration is not None:
            duration_str = f" (+{format_duration(duration)})"
            print(f"{color_start}{icon} [{author}] {timestamp}{duration_str}{color_end}")
        else:
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

    # Calculate and display session duration
    print("=" * 80)
    print("⏱️  SESSION TIMING SUMMARY")
    print("=" * 80)
    
    # Calculate session duration from events
    if events:
        # Get timestamps from events
        event_timestamps = []
        for event in events:
            event_timestamp = event.get('created_time') or event.get('timestamp')
            if event_timestamp:
                if isinstance(event_timestamp, (int, float)):
                    event_timestamps.append(event_timestamp)
                elif isinstance(event_timestamp, str):
                    try:
                        dt = datetime.fromisoformat(event_timestamp.replace('Z', '+00:00'))
                        event_timestamps.append(dt.timestamp())
                    except:
                        pass
        
        if event_timestamps:
            session_start = min(event_timestamps)
            session_end = max(event_timestamps)
            session_duration = session_end - session_start
            
            print(f"Session Start: {format_timestamp(session_start)}")
            print(f"Session End: {format_timestamp(session_end)}")
            print(f"Session Duration: {format_duration(session_duration)}")
            print(f"Total Events: {len(events)}")
            
            if session_duration > 0:
                events_per_minute = len(events) / (session_duration / 60)
                print(f"Average Events per Minute: {events_per_minute:.1f}")
            
            # Analyze time-consuming events
            print()
            print("🐌 TIME-CONSUMING EVENTS")
            print("=" * 40)
            
            # Create list of events with durations and metadata
            time_consuming_events = []
            for i, (event, duration) in enumerate(zip(events, event_durations)):
                if duration and duration > 1.0:  # Events taking more than 1 second
                    author = event.get('author', 'unknown')
                    event_timestamp = event.get('created_time') or event.get('timestamp', '')
                    timestamp_str = format_timestamp(event_timestamp)
                    content = extract_text_content(event.get('content'))
                    
                    # Extract summary of content (first line or function call)
                    content_lines = content.split('\n')
                    if content_lines:
                        first_line = content_lines[0].strip()
                        # Limit length for display
                        if len(first_line) > 80:
                            first_line = first_line[:77] + "..."
                        content_summary = first_line
                    else:
                        content_summary = "[No content]"
                    
                    time_consuming_events.append({
                        'index': i + 1,
                        'duration': duration,
                        'author': author,
                        'timestamp': timestamp_str,
                        'content': content_summary
                    })
            
            # Sort by duration (longest first)
            time_consuming_events.sort(key=lambda x: x['duration'], reverse=True)
            
            if time_consuming_events:
                print(f"Found {len(time_consuming_events)} events taking >1 second:")
                print()
                for i, event_info in enumerate(time_consuming_events, 1):  # Show ALL events
                    duration_str = format_duration(event_info['duration'])
                    author_icon = "👤" if event_info['author'] == 'user' else "🤖"
                    print(f"{i:3d}. {author_icon} {duration_str:>12} - {event_info['content']}")
                    print(f"      Event #{event_info['index']} at {event_info['timestamp']}")
                    print()
                
                # Show statistics
                total_slow_time = sum(e['duration'] for e in time_consuming_events)
                avg_slow_duration = total_slow_time / len(time_consuming_events)
                print(f"Total time in slow events: {format_duration(total_slow_time)}")
                print(f"Average slow event duration: {format_duration(avg_slow_duration)}")
                print(f"Percentage of session time: {(total_slow_time / session_duration * 100):.1f}%")
            else:
                print("No events found taking more than 1 second")
                print("This indicates a very responsive session!")
        else:
            print("No valid timestamps found in events")
    else:
        print("No events found in session")
    
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