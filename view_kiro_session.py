#!/usr/bin/env python3
"""
Simple Kiro CLI Session Viewer
Usage: python view_kiro_session.py session_file
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def format_timestamp(timestamp_str):
  """Format timestamp string to readable format."""
  try:
    if not timestamp_str:
      return "N/A"
    # Parse ISO format with timezone
    dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    return dt.strftime('%Y-%m-%d %H:%M:%S')
  except Exception:
    return str(timestamp_str)


def format_duration(duration_seconds):
  """Format duration in seconds to human-readable format."""
  if duration_seconds < 1:
    return f"{duration_seconds * 1000:.0f}ms"
  elif duration_seconds < 60:
    return f"{duration_seconds:.1f}s"
  elif duration_seconds < 3600:
    minutes = duration_seconds / 60
    return f"{minutes:.1f}m"
  else:
    hours = duration_seconds / 3600
    return f"{hours:.1f}h"


def extract_user_content(user_msg):
  """Extract content from user message."""
  content = user_msg.get('content', {})
  
  # Handle Prompt type
  if 'Prompt' in content:
    prompt = content['Prompt'].get('prompt', '')
    return prompt if prompt else "[Empty prompt]"
  
  # Handle ToolUseResults type
  if 'ToolUseResults' in content:
    results = content['ToolUseResults'].get('tool_use_results', [])
    if not results:
      return "[Tool results: empty]"
    
    summaries = []
    for result in results:
      tool_id = result.get('tool_use_id', 'unknown')
      status = result.get('status', 'unknown')
      content_items = result.get('content', [])
      
      # Extract result preview
      preview = ""
      for item in content_items:
        if 'Text' in item:
          text = item['Text']
          if len(text) > 100:
            text = text[:100] + "..."
          preview = text
          break
        elif 'Json' in item:
          json_data = item['Json']
          preview = f"JSON: {list(json_data.keys())}"
          break
      
      summaries.append(f"📤 {tool_id[-8:]}: {status} - {preview}")
    
    return '\n'.join(summaries)
  
  return "[Unknown content type]"


def extract_assistant_content(assistant_msg):
  """Extract content from assistant message."""
  # Handle ToolUse type
  if 'ToolUse' in assistant_msg:
    tool_use = assistant_msg['ToolUse']
    content = tool_use.get('content', '')
    tool_uses = tool_use.get('tool_uses', [])
    
    parts = []
    if content:
      parts.append(content)
    
    if tool_uses:
      for tool in tool_uses:
        tool_name = tool.get('name', 'unknown')
        tool_id = tool.get('id', 'unknown')
        args = tool.get('args', {})
        
        # Format tool call
        if args:
          # Simplify args display
          args_summary = []
          for key, value in args.items():
            if isinstance(value, str) and len(value) > 50:
              value = value[:50] + "..."
            elif isinstance(value, (list, dict)):
              value = f"{type(value).__name__}[{len(value)}]"
            args_summary.append(f"{key}={value}")
          args_str = ', '.join(args_summary)
          parts.append(f"🔧 {tool_name}({args_str})")
        else:
          parts.append(f"🔧 {tool_name}()")
    
    return '\n'.join(parts) if parts else "[No content]"
  
  # Handle Response type
  if 'Response' in assistant_msg:
    response = assistant_msg['Response']
    content = response.get('content', '')
    return content if content else "[Empty response]"
  
  return "[Unknown assistant message type]"


def calculate_turn_duration(history_item):
  """Calculate duration for a conversation turn."""
  if 'request_metadata' not in history_item:
    return None
  
  metadata = history_item['request_metadata']
  start_ms = metadata.get('request_start_timestamp_ms')
  end_ms = metadata.get('stream_end_timestamp_ms')
  
  if start_ms and end_ms:
    return (end_ms - start_ms) / 1000.0  # Convert to seconds
  
  return None


def view_session(session_file):
  """View Kiro CLI session in a formatted way."""
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
  print(f"📋 KIRO CLI SESSION: {session_file}")
  print("=" * 80)
  print(f"Conversation ID: {session.get('conversation_id', 'N/A')}")
  
  # Model info
  model_info = session.get('model_info', {})
  if model_info:
    print(f"Model: {model_info.get('model_name', 'N/A')}")
    print(f"Model ID: {model_info.get('model_id', 'N/A')}")
    print(f"Context Window: {model_info.get('context_window_tokens', 'N/A')} tokens")
  
  # Context info
  context_mgr = session.get('context_manager', {})
  if context_mgr:
    print(f"Context Profile: {context_mgr.get('current_profile', 'N/A')}")
    print(f"Max Context Size: {context_mgr.get('max_context_files_size', 'N/A')} bytes")
  
  # History
  history = session.get('history', [])
  print(f"Conversation Turns: {len(history)}")
  print()

  # Show conversation
  print("=" * 80)
  print("💬 CONVERSATION")
  print("=" * 80)
  
  # Track timing
  turn_durations = []
  total_user_prompts = 0
  total_assistant_responses = 0
  
  for i, turn in enumerate(history, 1):
    # User message
    user_msg = turn.get('user', {})
    user_timestamp = user_msg.get('timestamp', '')
    user_content = extract_user_content(user_msg)
    
    # Calculate turn duration
    turn_duration = calculate_turn_duration(turn)
    if turn_duration:
      turn_durations.append({
        'turn': i,
        'duration': turn_duration,
        'content': user_content
      })
    
    # Display user message
    print(f"\033[94m👤 [USER] Turn {i}\033[0m")
    if user_timestamp:
      print(f"   ⏰ {format_timestamp(user_timestamp)}")
    
    for line in user_content.split('\n'):
      if line.strip():
        print(f"   {line}")
    print()
    
    total_user_prompts += 1
    
    # Assistant message
    assistant_msg = turn.get('assistant', {})
    assistant_content = extract_assistant_content(assistant_msg)
    
    # Display assistant message
    duration_str = f" ({format_duration(turn_duration)})" if turn_duration else ""
    print(f"\033[92m🤖 [ASSISTANT] Turn {i}{duration_str}\033[0m")
    
    for line in assistant_content.split('\n'):
      if line.strip():
        print(f"   {line}")
    
    # Show metadata if available
    if 'request_metadata' in turn:
      metadata = turn['request_metadata']
      
      # Show model used
      model_id = metadata.get('model_id', 'N/A')
      if model_id != 'N/A':
        print(f"   📊 Model: {model_id}")
      
      # Show token usage if available
      user_prompt_length = metadata.get('user_prompt_length')
      response_size = metadata.get('response_size')
      if user_prompt_length or response_size:
        print(f"   📏 Tokens: prompt={user_prompt_length}, response={response_size}")
      
      # Show tool usage
      tool_ids_and_names = metadata.get('tool_use_ids_and_names', [])
      if tool_ids_and_names:
        tool_names = [name for _, name in tool_ids_and_names]
        print(f"   🔧 Tools: {', '.join(tool_names)}")
    
    print()
    total_assistant_responses += 1

  # Timing summary
  print("=" * 80)
  print("⏱️  SESSION TIMING SUMMARY")
  print("=" * 80)
  
  if turn_durations:
    total_duration = sum(d['duration'] for d in turn_durations)
    avg_duration = total_duration / len(turn_durations)
    
    print(f"Total Turns: {len(history)}")
    print(f"Total Duration: {format_duration(total_duration)}")
    print(f"Average Turn Duration: {format_duration(avg_duration)}")
    print()
    
    # Show slow turns
    print("🐌 SLOW TURNS (>5 seconds)")
    print("=" * 40)
    
    slow_turns = [d for d in turn_durations if d['duration'] > 5.0]
    slow_turns.sort(key=lambda x: x['duration'], reverse=True)
    
    if slow_turns:
      for i, turn_info in enumerate(slow_turns, 1):
        duration_str = format_duration(turn_info['duration'])
        content = turn_info['content']
        if len(content) > 80:
          content = content[:77] + "..."
        print(f"{i:3d}. Turn #{turn_info['turn']:2d} - {duration_str:>8} - {content}")
      
      print()
      total_slow_time = sum(t['duration'] for t in slow_turns)
      print(f"Total time in slow turns: {format_duration(total_slow_time)}")
      print(f"Percentage of session: {(total_slow_time / total_duration * 100):.1f}%")
    else:
      print("No turns taking more than 5 seconds")
      print("This indicates a very responsive session!")
  else:
    print("No timing information available")
  
  # File tracking summary
  print()
  print("=" * 80)
  print("📝 FILE MODIFICATIONS")
  print("=" * 80)
  
  file_tracker = session.get('file_line_tracker', {})
  if file_tracker:
    print(f"Files modified: {len(file_tracker)}")
    print()
    
    for filepath, stats in file_tracker.items():
      # Shorten path for display
      display_path = filepath
      if len(display_path) > 60:
        parts = display_path.split('/')
        display_path = '.../' + '/'.join(parts[-3:])
      
      lines_added = stats.get('lines_added_by_agent', 0)
      lines_removed = stats.get('lines_removed_by_agent', 0)
      is_first = stats.get('is_first_write', False)
      
      status = "📄 NEW" if is_first else "✏️  MOD"
      print(f"{status} {display_path}")
      print(f"     +{lines_added} -{lines_removed} lines")
    
    # Calculate totals
    total_added = sum(s.get('lines_added_by_agent', 0) for s in file_tracker.values())
    total_removed = sum(s.get('lines_removed_by_agent', 0) for s in file_tracker.values())
    print()
    print(f"Total: +{total_added} -{total_removed} lines across {len(file_tracker)} files")
  else:
    print("No files modified in this session")
  
  # Transcript summary
  print()
  print("=" * 80)
  print("📜 TRANSCRIPT SUMMARY")
  print("=" * 80)
  
  transcript = session.get('transcript', [])
  if transcript:
    print(f"Total messages: {len(transcript)}")
    print()
    print("Message preview:")
    for i, msg in enumerate(transcript[:5], 1):  # Show first 5
      if len(msg) > 100:
        msg = msg[:97] + "..."
      print(f"{i}. {msg}")
    
    if len(transcript) > 5:
      print(f"... and {len(transcript) - 5} more messages")
  else:
    print("No transcript available")
  
  print()
  print("=" * 80)
  print("✅ Session view complete")
  print("=" * 80)


def main():
  if len(sys.argv) != 2:
    print("Usage: python view_kiro_session.py <session_file>")
    print("\nExample:")
    print("  python view_kiro_session.py proposal-session")
    print("  python view_kiro_session.py /path/to/session.json")
    sys.exit(1)
  
  session_file = sys.argv[1]
  if not Path(session_file).exists():
    print(f"❌ File not found: {session_file}")
    print("\nSearching for session files...")
    
    # Search in common locations
    search_paths = [
      Path("."),
      Path(".."),
      Path("../adk_openspec_project"),
    ]
    
    found_files = []
    for search_path in search_paths:
      if search_path.exists():
        for pattern in ["*session*", "*.json"]:
          for file in search_path.glob(pattern):
            if file.is_file() and 'session' in file.name.lower():
              found_files.append(file)
    
    if found_files:
      print("\nAvailable session files:")
      for file in found_files[:10]:  # Show first 10
        print(f"  {file}")
      if len(found_files) > 10:
        print(f"  ... and {len(found_files) - 10} more")
    else:
      print("\nNo session files found")
    
    sys.exit(1)
  
  view_session(session_file)


if __name__ == "__main__":
  main()
