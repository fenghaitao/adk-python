#!/usr/bin/env python3
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

"""Generate a new memory file based on error patterns from sessions.

This script analyzes sessions with a specific error type and generates
a new memory file with guidance to prevent that error.

Usage:
  python generate_memory_file.py \\
    --sessions historical_sessions.json \\
    --error-type missing_queue \\
    --output 08_Test_Queue_Assignment.md \\
    --model iflow/qwen3-coder-plus
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict

import litellm


def extract_error_examples(
    sessions: List[Dict],
    error_type: str
) -> List[Dict]:
  """Extract examples of sessions with this error.
  
  Args:
    sessions: All historical sessions
    error_type: Type of error to find examples for
    
  Returns:
    List of session examples with this error
  """
  examples = []
  
  for session in sessions:
    implementation = session.get('implementation', '')
    tests = session.get('tests', '')
    
    # Check if this session has the error
    has_error = False
    error_context = ""
    
    if error_type == 'missing_queue':
      if 'timer' in implementation.lower() and 'dev.queue' not in tests:
        has_error = True
        error_context = "Timer device without queue assignment in tests"
    
    elif error_type == 'missing_clock_setup':
      if 'clk.freq_mhz' not in tests:
        has_error = True
        error_context = "Tests without clock frequency configuration"
    
    elif error_type == 'incomplete_interrupt':
      if 'interrupt' in implementation.lower():
        if not any(word in implementation.lower() for word in ['raise', 'lower', 'set']):
          has_error = True
          error_context = "Interrupt declared but never raised/lowered"
    
    elif error_type == 'direct_register_write':
      if 'this.val =' in implementation:
        has_error = True
        error_context = "Direct register write without side-effects"
    
    elif error_type == 'hardcoded_address':
      import re
      if re.search(r'=\s*0x[0-9a-fA-F]{8,}', implementation):
        has_error = True
        error_context = "Hardcoded memory addresses in implementation"
    
    if has_error:
      examples.append({
        'device_name': session.get('device_name', 'unknown'),
        'error_context': error_context,
        'implementation_snippet': implementation[:500],  # First 500 chars
        'test_snippet': tests[:500] if tests else '',
        'score': session.get('score', 0.0)
      })
  
  return examples[:5]  # Return top 5 examples


def generate_memory_file_content(
    error_type: str,
    examples: List[Dict],
    model: str
) -> str:
  """Generate memory file content using LLM.
  
  Args:
    error_type: Type of error to address
    examples: Example sessions with this error
    model: LLM model to use
    
  Returns:
    Generated memory file content
  """
  # Build prompt for LLM
  examples_text = "\n\n".join([
    f"Example {i+1}: {ex['device_name']}\n"
    f"Context: {ex['error_context']}\n"
    f"Score: {ex['score']:.1%}\n"
    f"Implementation snippet:\n```dml\n{ex['implementation_snippet']}\n```\n"
    f"Test snippet:\n```python\n{ex['test_snippet']}\n```"
    for i, ex in enumerate(examples)
  ])
  
  prompt = f"""You are creating a best practices guide for Simics DML device development.

Create a memory file that helps agents avoid this error: {error_type.replace('_', ' ')}

Here are {len(examples)} real examples where agents made this mistake:

{examples_text}

Create a comprehensive memory file with:

1. **Title**: Clear, descriptive title
2. **Overview**: What this error is and why it matters
3. **The Problem**: Explain what goes wrong
4. **The Solution**: Step-by-step guidance
5. **How to Recognize**: Red flags that indicate this mistake
6. **Examples**: Show bad vs. good code
7. **Common Mistakes**: Variations of this error
8. **See Also**: Cross-references to related files

Use these formatting conventions:
- ⚠️ for warnings
- ❌ for bad examples
- ✅ for good examples
- 🔍 for recognition patterns
- 📋 for real examples

Make it practical and actionable. Focus on preventing the error, not just describing it.

Generate the complete memory file in Markdown format:"""
  
  # Call LLM
  response = litellm.completion(
    model=model,
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7
  )
  
  return response.choices[0].message.content


def suggest_file_number_and_name(
    error_type: str,
    memory_dir: Path
) -> str:
  """Suggest a file number and name for the new memory file.
  
  Args:
    error_type: Type of error
    memory_dir: Path to memory directory
    
  Returns:
    Suggested filename
  """
  # Determine category
  if any(word in error_type for word in ['test', 'clock', 'queue']):
    category = 'Test'
    prefix = '0'
  else:
    category = 'DML'
    prefix = '0'
  
  # Find next available number
  existing_files = list(memory_dir.glob(f'{prefix}*_{category}_*.md'))
  if existing_files:
    numbers = []
    for f in existing_files:
      try:
        num = int(f.name.split('_')[0])
        numbers.append(num)
      except:
        pass
    next_num = max(numbers) + 1 if numbers else 1
  else:
    next_num = 1
  
  # Create descriptive name
  name_parts = error_type.replace('_', ' ').title().split()
  name = '_'.join(name_parts)
  
  return f"{next_num:02d}_{category}_{name}.md"


def main():
  parser = argparse.ArgumentParser(
    description="Generate new memory file for an error type"
  )
  parser.add_argument(
    "--sessions",
    required=True,
    help="Path to historical sessions JSON"
  )
  parser.add_argument(
    "--error-type",
    required=True,
    help="Type of error to create file for (e.g., missing_queue)"
  )
  parser.add_argument(
    "--output",
    help="Output file path (optional, will suggest if not provided)"
  )
  parser.add_argument(
    "--memory-dir",
    default="../openspec-memories",
    help="Path to memory directory (for file numbering)"
  )
  parser.add_argument(
    "--model",
    default="iflow/qwen3-coder-plus",
    help="LLM model to use (default: iflow/qwen3-coder-plus)"
  )
  
  args = parser.parse_args()
  
  sessions_file = Path(args.sessions)
  if not sessions_file.exists():
    print(f"❌ Error: Sessions file not found: {sessions_file}")
    sys.exit(1)
  
  print(f"📊 Generating memory file for error: {args.error_type}")
  print(f"📂 Sessions: {sessions_file}")
  
  # Load sessions
  with open(sessions_file) as f:
    sessions = json.load(f)
  
  # Extract examples
  print(f"\n🔍 Finding examples of this error...")
  examples = extract_error_examples(sessions, args.error_type)
  
  if not examples:
    print(f"❌ No examples found for error type: {args.error_type}")
    print(f"   Try running: python identify_memory_gaps.py --sessions {sessions_file}")
    sys.exit(1)
  
  print(f"✅ Found {len(examples)} examples")
  
  # Generate content
  print(f"\n🤖 Generating memory file content with {args.model}...")
  content = generate_memory_file_content(args.error_type, examples, args.model)
  
  # Determine output path
  if args.output:
    output_path = Path(args.output)
  else:
    memory_dir = Path(args.memory_dir)
    suggested_name = suggest_file_number_and_name(args.error_type, memory_dir)
    output_path = memory_dir / suggested_name
    print(f"\n💡 Suggested filename: {suggested_name}")
  
  # Save file
  output_path.parent.mkdir(parents=True, exist_ok=True)
  output_path.write_text(content)
  
  print(f"\n✅ Memory file generated: {output_path}")
  print(f"📄 Size: {len(content)} characters, {len(content.split())} lines")
  
  print(f"\n💡 Next steps:")
  print(f"   1. Review the generated file: {output_path}")
  print(f"   2. Edit and refine as needed")
  print(f"   3. Add to index file:")
  print(f"      - For DML: openspec-memories/00_DML_Best_Practices_Index.md")
  print(f"      - For Test: openspec-memories/00_Test_Best_Practices_Index.md")
  print(f"   4. Test with new sessions")
  print(f"   5. Measure error rate reduction\n")


if __name__ == "__main__":
  main()
