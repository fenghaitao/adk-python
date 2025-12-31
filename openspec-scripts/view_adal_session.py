#!/usr/bin/env python3
"""Parse adal session logs and generate analysis reports."""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


def parse_session_id_from_log(log_file):
  """Extract session ID from log file by reading the file content."""
  # Strip ANSI escape codes
  ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
  
  with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()
    cleaned = ansi_escape.sub('', content)
    
    # Look for "Session ID: <uuid>" pattern
    match = re.search(
        r'Session ID\s*:\s*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-'
        r'[0-9a-f]{4}-[0-9a-f]{12})',
        cleaned,
        re.IGNORECASE
    )
    if match:
      return match.group(1)
  
  return None


def find_session_file(session_id):
  """Find the session jsonl file for the given session ID."""
  # Adal stores sessions in ~/.adal/sessions/
  sessions_dir = Path.home() / '.adal' / 'sessions'
  
  # Adal uses the pattern: conversation_<session-id>.jsonl
  session_file = sessions_dir / f'conversation_{session_id}.jsonl'
  
  if session_file.exists():
    return session_file
  
  # Also try without the conversation_ prefix (in case format changes)
  session_file_alt = sessions_dir / f'{session_id}.jsonl'
  if session_file_alt.exists():
    return session_file_alt
  
  # Also check if there's a subdirectory with the session ID
  session_subdir = sessions_dir / session_id
  if session_subdir.exists() and session_subdir.is_dir():
    # Look for jsonl files in the subdirectory
    for jsonl_file in session_subdir.glob('*.jsonl'):
      return jsonl_file
  
  return None


def parse_session_file(session_file):
  """Parse the session jsonl file and return all messages."""
  messages = []
  with open(session_file, 'r', encoding='utf-8') as f:
    for line in f:
      if line.strip():
        messages.append(json.loads(line.strip()))
  return messages


def format_timestamp(ts_ms):
  """Convert millisecond timestamp to readable format."""
  dt = datetime.fromtimestamp(ts_ms / 1000.0)
  return dt.strftime('%Y-%m-%d %H:%M:%S')


def calculate_duration(start_ms, end_ms):
  """Calculate duration in seconds between two timestamps."""
  return (end_ms - start_ms) / 1000.0


def truncate_text(text, max_len=500):
  """Truncate text to max length."""
  if len(text) > max_len:
    return text[:max_len] + '...'
  return text


def extract_text_from_parts(parts):
  """Extract text content from message parts."""
  texts = []
  for part in parts:
    if part.get('type') == 'text':
      data = part.get('data', {})
      text = data.get('text', '')
      if text:
        texts.append(text)
  return '\n'.join(texts)


def extract_tool_calls(parts):
  """Extract tool call information from message parts."""
  tool_calls = []
  for part in parts:
    if part.get('type') == 'tool_call':
      data = part.get('data', {})
      tool_input = data.get('input', '')
      # Try to parse input as JSON for better formatting
      try:
        input_obj = json.loads(tool_input) if isinstance(tool_input, str) else tool_input
      except (json.JSONDecodeError, TypeError):
        input_obj = tool_input
      
      tool_calls.append({
          'id': data.get('id', ''),
          'name': data.get('name', ''),
          'input': tool_input,
          'input_obj': input_obj,
      })
  return tool_calls


def extract_tool_results(parts):
  """Extract tool result information from message parts."""
  results = []
  for part in parts:
    if part.get('type') == 'tool_result':
      data = part.get('data', {})
      results.append({
          'tool_call_id': data.get('tool_call_id', ''),
          'content': data.get('content', ''),
      })
  return results


def generate_report(messages, output_file=None):
  """Generate a human-readable report from session messages."""
  report_lines = []
  report_lines.append('=' * 80)
  report_lines.append('ADAL SESSION REPORT')
  report_lines.append('=' * 80)
  report_lines.append('')
  
  # Calculate total session duration
  session_start = None
  session_end = None
  for msg in messages:
    created_at = msg.get('created_at', 0)
    finished_at = msg.get('finished_at', 0)
    
    if created_at and (session_start is None or created_at < session_start):
      session_start = created_at
    if finished_at and (session_end is None or finished_at > session_end):
      session_end = finished_at
  
  # Statistics
  user_msgs = [m for m in messages if m.get('role') == 'user' and not m.get('is_meta')]
  assistant_msgs = [m for m in messages if m.get('role') == 'assistant']
  tool_msgs = [m for m in messages if m.get('role') == 'tool']
  
  report_lines.append('SESSION STATISTICS')
  report_lines.append('-' * 80)
  
  # Show session duration at the top
  if session_start and session_end:
    total_duration = calculate_duration(session_start, session_end)
    report_lines.append(f'Session Start: {format_timestamp(session_start)}')
    report_lines.append(f'Session End: {format_timestamp(session_end)}')
    report_lines.append(f'Total Duration: {total_duration:.2f}s ({total_duration/60:.1f} minutes)')
    report_lines.append('')
  
  report_lines.append(f'Total Messages: {len(messages)}')
  report_lines.append(f'User Messages: {len(user_msgs)}')
  report_lines.append(f'Assistant Messages: {len(assistant_msgs)}')
  report_lines.append(f'Tool Messages: {len(tool_msgs)}')
  
  # Token usage summary
  total_input_tokens = 0
  total_output_tokens = 0
  for msg in assistant_msgs:
    usage = msg.get('usage', {})
    total_input_tokens += usage.get('input_tokens', 0)
    total_output_tokens += usage.get('output_tokens', 0)
  
  if total_input_tokens > 0 or total_output_tokens > 0:
    report_lines.append(f'Total Input Tokens: {total_input_tokens:,}')
    report_lines.append(f'Total Output Tokens: {total_output_tokens:,}')
    report_lines.append(f'Total Tokens: {total_input_tokens + total_output_tokens:,}')
  
  report_lines.append('')
  report_lines.append('=' * 80)
  report_lines.append('CONVERSATION')
  report_lines.append('=' * 80)
  report_lines.append('')
  
  # Track tool call durations and assistant turn durations
  tool_durations = []
  assistant_durations = []
  tool_call_map = {}  # Map tool call IDs to their start times
  
  # Process messages in order
  for msg in messages:
    role = msg.get('role', 'unknown')
    is_meta = msg.get('is_meta', False)
    timestamp = format_timestamp(msg.get('created_at', 0))
    created_at = msg.get('created_at', 0)
    finished_at = msg.get('finished_at', 0)
    parts = msg.get('parts', [])
    
    # Skip meta messages
    if is_meta:
      continue
    
    if role == 'user':
      text = extract_text_from_parts(parts)
      if text:
        report_lines.append(f'[{timestamp}] USER:')
        report_lines.append(text)
        report_lines.append('')
    
    elif role == 'assistant':
      text = extract_text_from_parts(parts)
      tool_calls = extract_tool_calls(parts)
      
      # Calculate duration
      if created_at and finished_at:
        duration = calculate_duration(created_at, finished_at)
        assistant_durations.append(duration)
      
      if text:
        report_lines.append(f'[{timestamp}] ASSISTANT:')
        report_lines.append(text)
        if created_at and finished_at:
          report_lines.append(f'  (Duration: {duration:.2f}s)')
        report_lines.append('')
      
      if tool_calls:
        report_lines.append(f'[{timestamp}] TOOL CALLS:')
        for tc in tool_calls:
          # Store tool call start time
          tool_call_map[tc['id']] = created_at
          
          # Format arguments nicely
          input_obj = tc.get('input_obj', {})
          if isinstance(input_obj, dict):
            args_str = ', '.join(f"{k}={truncate_text(str(v), 50)}" for k, v in input_obj.items())
            report_lines.append(f"  - {tc['name']}({args_str})")
          else:
            report_lines.append(f"  - {tc['name']} (id: {tc['id'][:16]}...)")
            report_lines.append(f"    Input: {truncate_text(tc['input'], 300)}")
        report_lines.append('')
    
    elif role == 'tool':
      results = extract_tool_results(parts)
      if results:
        report_lines.append(f'[{timestamp}] TOOL RESULTS:')
        for result in results:
          tool_id = result['tool_call_id']
          tool_id_short = tool_id[:16] if tool_id else 'unknown'
          content = result['content']
          
          # Calculate tool execution duration
          if tool_id in tool_call_map and finished_at:
            tool_duration = calculate_duration(tool_call_map[tool_id], finished_at)
            tool_durations.append({'id': tool_id_short, 'duration': tool_duration})
            report_lines.append(f'  Tool {tool_id_short}... (Duration: {tool_duration:.2f}s)')
          else:
            report_lines.append(f'  Tool {tool_id_short}...')
          
          # Try to parse content as JSON for better formatting
          try:
            content_data = json.loads(content)
            # Extract key fields
            stdout = content_data.get('stdout', '')
            stderr = content_data.get('stderr', '')
            exit_code = content_data.get('exit_code')
            
            if exit_code is not None:
              status = '✓' if exit_code == 0 else '✗'
              report_lines.append(f'    Status: {status} (exit code: {exit_code})')
            
            if stdout:
              report_lines.append(f'    Output: {truncate_text(stdout, 500)}')
            if stderr:
              report_lines.append(f'    Error: {truncate_text(stderr, 500)}')
          except (json.JSONDecodeError, TypeError):
            report_lines.append(f'    Result: {truncate_text(content, 500)}')
        report_lines.append('')
  
  # Add duration summaries
  report_lines.append('=' * 80)
  report_lines.append('DURATION SUMMARY')
  report_lines.append('=' * 80)
  report_lines.append('')
  
  # Show total session duration again in summary
  if session_start and session_end:
    total_duration = calculate_duration(session_start, session_end)
    report_lines.append(f'Total Session Duration: {total_duration:.2f}s ({total_duration/60:.1f} minutes)')
    report_lines.append('')
  
  if assistant_durations:
    report_lines.append('Assistant Turn Durations:')
    for i, duration in enumerate(assistant_durations, 1):
      report_lines.append(f'  Turn {i}: {duration:.2f}s')
    total_assistant_time = sum(assistant_durations)
    report_lines.append(f'  Total: {total_assistant_time:.2f}s')
    
    # Show percentage of total session time
    if session_start and session_end and total_duration > 0:
      percentage = (total_assistant_time / total_duration) * 100
      report_lines.append(f'  ({percentage:.1f}% of total session time)')
    report_lines.append('')
  
  if tool_durations:
    report_lines.append('Tool Execution Durations:')
    for tool_info in tool_durations:
      report_lines.append(f"  {tool_info['id']}...: {tool_info['duration']:.2f}s")
    total_tool_time = sum(t['duration'] for t in tool_durations)
    report_lines.append(f'  Total: {total_tool_time:.2f}s')
    
    # Show percentage of total session time
    if session_start and session_end and total_duration > 0:
      percentage = (total_tool_time / total_duration) * 100
      report_lines.append(f'  ({percentage:.1f}% of total session time)')
    report_lines.append('')
  
  report_lines.append('=' * 80)
  report_lines.append('END OF REPORT')
  report_lines.append('=' * 80)
  
  # Write output
  report_content = '\n'.join(report_lines)
  if output_file:
    with open(output_file, 'w', encoding='utf-8') as f:
      f.write(report_content)
    print(f'Report written to {output_file}')
  else:
    print(report_content)


def main():
  """Main entry point."""
  parser = argparse.ArgumentParser(
      description='Parse adal session logs and generate analysis reports'
  )
  parser.add_argument(
      'log_file',
      help='Session log file (e.g., adal-proposal-session_*.log)'
  )
  parser.add_argument(
      '-o',
      '--output',
      help='Output file (default: <log_file_base>.txt)'
  )
  
  args = parser.parse_args()
  
  # Extract session ID from log file
  session_id = parse_session_id_from_log(args.log_file)
  
  if not session_id:
    print('Error: Could not extract session ID from log file', file=sys.stderr)
    sys.exit(1)
  
  print(f'Session ID: {session_id}')
  
  # Find session jsonl file
  session_file = find_session_file(session_id)
  
  if not session_file:
    print(f'Error: Session file not found for ID: {session_id}', file=sys.stderr)
    print('Searched in ~/.adal/sessions/', file=sys.stderr)
    sys.exit(1)
  
  print(f'Session file: {session_file}')
  
  # Parse session
  try:
    messages = parse_session_file(session_file)
    print(f'Parsed {len(messages)} messages')
  except Exception as e:
    print(f'Error parsing session file: {e}', file=sys.stderr)
    sys.exit(1)
  
  # Generate report
  output_file = args.output
  if not output_file:
    # Default: replace .log with .txt
    log_path = Path(args.log_file)
    output_file = str(log_path.with_suffix('.txt'))
  
  try:
    generate_report(messages, output_file)
  except Exception as e:
    print(f'Error generating report: {e}', file=sys.stderr)
    sys.exit(1)


if __name__ == '__main__':
  main()
