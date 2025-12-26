#!/usr/bin/env python3
import json
import sys
import os
import re
import argparse
from pathlib import Path

def parse_session_id(filename):
    match = re.search(r'session-(.+)\.log$', filename)
    return match.group(1) if match else None

def parse_session_file(session_id):
    session_file = Path.home() / '.copilot' / 'session-state' / f'{session_id}.jsonl'
    if not session_file.exists():
        raise FileNotFoundError(f"Session file not found: {session_file}")
    
    events = []
    with open(session_file, 'r') as f:
        for line in f:
            events.append(json.loads(line.strip()))
    return events

def format_timestamp(ts):
    return ts.replace('T', ' ').replace('Z', '')

def truncate_result(result, max_len=200):
    if isinstance(result, str) and len(result) > max_len:
        return result[:max_len] + "..."
    return str(result)[:max_len] + "..." if len(str(result)) > max_len else result

def calculate_duration(start, end):
    try:
        import pandas as pd
        return (pd.to_datetime(end) - pd.to_datetime(start)).total_seconds()
    except ImportError:
        from datetime import datetime
        start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
        return (end_dt - start_dt).total_seconds()

def parse_args(args_list):
    args=""
    for k, v in args_list.items():
        if args:
            args += f", {k}={v}"
        else:
            args += f"{k}={v}"
    return args

def generate_report(events, output_file=None):
    messages = []
    
    i = 0
    while i < len(events):
        event = events[i]
        
        # User message
        if event.get('type') == 'user.message':
            timestamp = event['timestamp']
            content = event.get('data', {}).get('content', '')
            messages.append({
                'timestamp': timestamp,
                'type': 'user',
                'content': content
            })
            i += 1
        
        # Assistant turn
        elif event.get('type') == 'assistant.turn_start':
            start_time = event['timestamp']
            turn_id = event.get('data', {}).get('turnId', "0")
            
            # Find turn_end
            j = i + 1
            while j < len(events) and events[j].get('type') != 'assistant.turn_end':
                j += 1
            
            if j < len(events):
                end_time = events[j]['timestamp']
                duration = calculate_duration(start_time, end_time)
                
                # Collect tool execution data and assistant messages
                tool_calls = {}
                assistant_content = ""
                
                # Parse events between start and end
                for k in range(i + 1, j):
                    evt = events[k]
                    
                    if evt.get('type') == 'assistant.message':
                        content = evt.get('data', {}).get('content', '')
                        assistant_content += content
                    
                    elif evt.get('type') == 'tool.execution_start':
                        tool_id = evt.get('data', {}).get('toolCallId')
                        tool_name = evt.get('data', {}).get('toolName', 'unknown')
                        args = parse_args(evt.get('data', {}).get('arguments', {}))
                        timestamp = evt.get('timestamp')
                        tool_calls[tool_id] = {'start': timestamp, 'name': tool_name, 'args': args}
                    
                    elif evt.get('type') == 'tool.execution_complete':
                        tool_id = evt.get('data', {}).get('toolCallId')
                        if tool_id in tool_calls:
                            tool_calls[tool_id]['end'] = evt['timestamp']
                            tool_calls[tool_id]['success'] = evt.get('data', {}).get('success', False)
                            result = evt.get('data', {}).get('result', {})
                            content = result.get('content', '') if isinstance(result, dict) else str(result)
                            tool_calls[tool_id]['result'] = truncate_result(content)
                
                # Add assistant message
                messages.append({
                    'timestamp': start_time,
                    'type': 'assistant',
                    'turn_id': turn_id,
                    'content': assistant_content,
                    'duration': duration
                })
                
                # Add tool calls
                for tool_id, call_data in tool_calls.items():
                    if tool_id in tool_calls:
                        exec_data = tool_calls[tool_id]
                        if 'end' in exec_data:
                            exec_duration = calculate_duration(exec_data['start'], exec_data['end'])
                            messages.append({
                                'timestamp': exec_data['start'],
                                'type': 'tool',
                                'name': call_data['name'],
                                'args': call_data['args'],
                                'duration': exec_duration,
                                'success': exec_data['success'],
                                'result': exec_data['result']
                            })
                
                i = j
            else:
                i += 1
        else:
            i += 1
    
    # Sort messages by timestamp
    messages.sort(key=lambda x: x['timestamp'])
    
    # Generate report content
    report_lines = []
    report_lines.append("SESSION REPORT")
    report_lines.append("=" * 50)
    
    for msg in messages:
        timestamp = format_timestamp(msg['timestamp'])
        
        if msg['type'] == 'user':
            report_lines.append(f"\n[{timestamp}] USER: {msg['content']}")
        
        elif msg['type'] == 'assistant' and msg['content']:
            report_lines.append(f"\n[{timestamp}] ASSISTANT: {msg['content']}")
        
        elif msg['type'] == 'tool':
            report_lines.append(f"[{timestamp}] TOOL CALL: {msg['name']}({msg['args']})")
            report_lines.append(f"TOOL RESPONSE: state={msg['success']}, result={msg['result']}\n")
    
    report_lines.append("=" * 50)
    report_lines.append("Asssistant duration summary")
    for msg in messages:
        if msg['type'] == 'assistant':
            report_lines.append(f"Assistant turn {msg['turn_id']} duration {msg['duration']:.2f}s")
    
    report_lines.append("=" * 50)
    report_lines.append("Tool execution duration summary")
    for msg in messages:
        if msg['type'] == 'tool':
            report_lines.append(f"{msg['name']} duration {msg['duration']:.2f}s")
    
    # Output to file or stdout
    report_content = '\n'.join(report_lines)
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report_content)
        print(f"Report written to {output_file}")
    else:
        print(report_content)

def main():
    parser = argparse.ArgumentParser(description='Parse Agent session logs')
    parser.add_argument('session_file', help='Session log file (session-<id>.log)')
    parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    
    args = parser.parse_args()
    
    session_id = parse_session_id(args.session_file)
    
    if not session_id:
        print("Error: Could not parse session ID from filename")
        sys.exit(1)
    
    try:
        events = parse_session_file(session_id)
        generate_report(events, args.output)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
