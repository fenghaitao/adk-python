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

"""Optimize a specific memory/best practices file using DeepEval.

This script optimizes individual memory files based on error patterns
that occur even after agents read those files.

Usage:
  python optimize_memory_file.py \\
    --memory-file openspec-memories/02_DML_Anti_Patterns.md \\
    --sessions historical_sessions.json \\
    --output 02_DML_Anti_Patterns_optimized.md \\
    --focus-errors cycle_by_cycle_updates,sim_cycle_count_in_init
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

from deepeval.optimizer import PromptOptimizer
from deepeval.optimizer.algorithms import MIPROv2, SIMBA
from deepeval.prompt import Prompt
from deepeval.dataset import Golden

from metrics.code_correctness import CodeCorrectnessMetric
from metrics.code_style import CodeStyleMetric


def extract_files_read(session_log: str) -> set:
  """Extract memory files read during session."""
  files_read = set()
  patterns = [
    r'openspec-memories/([0-9]+_[A-Za-z_]+\.md)',
    r'Reading.*?([0-9]+_[A-Za-z_]+\.md)',
  ]
  for pattern in patterns:
    matches = re.findall(pattern, session_log, re.IGNORECASE)
    files_read.update(matches)
  return files_read


def filter_relevant_sessions(
    sessions: List[Dict],
    memory_file_name: str,
    focus_errors: Optional[List[str]] = None
) -> List[Golden]:
  """Filter sessions that read this memory file.
  
  Args:
    sessions: All historical sessions
    memory_file_name: Name of memory file to optimize
    focus_errors: Optional list of specific errors to focus on
    
  Returns:
    List of Golden test cases for sessions that used this file
  """
  relevant_sessions = []
  
  for session in sessions:
    session_log = session.get('session_log', '')
    files_read = extract_files_read(session_log)
    
    # Only include if this file was read
    if memory_file_name not in files_read:
      continue
    
    # If focus_errors specified, only include sessions with those errors
    if focus_errors:
      implementation = session.get('implementation', '')
      has_focus_error = any(
        error.replace('_', ' ').lower() in implementation.lower()
        for error in focus_errors
      )
      if not has_focus_error:
        continue
    
    # Create Golden test case
    golden = Golden(
      input=session.get('task_description', ''),
      actual_output=session.get('implementation', ''),
      expected_output='',  # We don't have expected output
      context=[
        session.get('spec', ''),
        session.get('tests', ''),
        session.get('session_log', '')
      ],
      additional_metadata={
        'device_name': session.get('device_name', ''),
        'score': session.get('score', 0.0),
        'metrics': session.get('metrics', {})
      }
    )
    relevant_sessions.append(golden)
  
  return relevant_sessions


def create_model_callback(model: str):
  """Create model callback for optimizer."""
  def model_callback(prompt: str) -> str:
    import litellm
    response = litellm.completion(
      model=model,
      messages=[{"role": "user", "content": prompt}],
      temperature=0.7
    )
    return response.choices[0].message.content
  return model_callback


def create_focused_metrics(
    memory_file_name: str,
    model: str
) -> List:
  """Create metrics focused on this memory file's purpose.
  
  Args:
    memory_file_name: Name of memory file
    model: LLM model name
    
  Returns:
    List of relevant metrics
  """
  # Default metrics
  metrics = [
    CodeCorrectnessMetric(model=model, threshold=0.7),
    CodeStyleMetric(model=model, threshold=0.8)
  ]
  
  # Add file-specific metrics based on file name
  # (In a full implementation, you'd create custom metrics for each file type)
  
  return metrics


def add_optimization_context(
    memory_content: str,
    focus_errors: Optional[List[str]],
    session_count: int
) -> str:
  """Add context about what to optimize.
  
  Args:
    memory_content: Original memory file content
    focus_errors: Errors to focus on
    session_count: Number of sessions analyzed
    
  Returns:
    Content with optimization context prepended
  """
  context = f"""
# OPTIMIZATION CONTEXT (Remove this section after optimization)

This memory file is being optimized based on {session_count} historical sessions.

"""
  
  if focus_errors:
    context += f"""
**Focus Areas**: The following errors still occurred even after agents read this file:
"""
    for error in focus_errors:
      error_name = error.replace('_', ' ').title()
      context += f"- {error_name}\n"
    
    context += """
**Optimization Goal**: Make the guidance clearer so agents avoid these specific errors.

**Suggestions**:
- Add more explicit warnings with ⚠️ symbols
- Use ❌/✅ to show bad/good examples
- Add "How to recognize this pattern" sections
- Include real examples from session logs
- Add cross-references to related files
- Make critical information stand out visually

"""
  
  context += "---\n\n"
  
  return context + memory_content


def optimize_memory_file(
    memory_file: Path,
    sessions: List[Golden],
    output: Path,
    model: str,
    algorithm: str,
    iterations: int,
    focus_errors: Optional[List[str]] = None
) -> str:
  """Optimize a memory file using DeepEval PromptOptimizer.
  
  Args:
    memory_file: Path to memory file to optimize
    sessions: Relevant historical sessions
    output: Output path for optimized file
    model: LLM model name
    algorithm: Optimization algorithm (miprov2 or simba)
    iterations: Number of optimization iterations
    focus_errors: Optional list of errors to focus on
    
  Returns:
    Optimized memory file content
  """
  # Load memory file
  with open(memory_file) as f:
    content = f.read()
  
  # Add optimization context
  content_with_context = add_optimization_context(
    content,
    focus_errors,
    len(sessions)
  )
  
  # Create prompt
  prompt = Prompt(
    template=content_with_context,
    variables=[]  # Memory files don't have variables
  )
  
  # Create metrics
  metrics = create_focused_metrics(memory_file.name, model)
  
  # Select algorithm
  if algorithm == 'simba':
    algo = SIMBA(
      iterations=iterations,
      num_mutations=5
    )
  else:  # miprov2
    algo = MIPROv2(
      iterations=iterations,
      num_instructions=5,  # Fewer variants for memory files
      num_demos=3
    )
  
  # Create optimizer
  print(f"🔧 Creating optimizer with {algorithm} algorithm...")
  optimizer = PromptOptimizer(
    model_callback=create_model_callback(model),
    metrics=metrics,
    algorithm=algo
  )
  
  # Run optimization
  print(f"🚀 Running optimization ({iterations} iterations)...")
  print(f"📊 Using {len(sessions)} relevant sessions")
  print(f"📈 Metrics: {[m.__name__ for m in metrics]}")
  
  optimized_prompt = optimizer.optimize(
    prompt=prompt,
    dataset=sessions
  )
  
  # Remove optimization context from result
  optimized_content = optimized_prompt.template
  if "# OPTIMIZATION CONTEXT" in optimized_content:
    # Remove everything from OPTIMIZATION CONTEXT to the --- separator
    optimized_content = re.sub(
      r'# OPTIMIZATION CONTEXT.*?---\n\n',
      '',
      optimized_content,
      flags=re.DOTALL
    )
  
  return optimized_content


def main():
  parser = argparse.ArgumentParser(
    description="Optimize a memory/best practices file"
  )
  parser.add_argument(
    "--memory-file",
    required=True,
    help="Path to memory file to optimize"
  )
  parser.add_argument(
    "--sessions",
    required=True,
    help="Path to historical sessions JSON"
  )
  parser.add_argument(
    "--output",
    required=True,
    help="Output path for optimized file"
  )
  parser.add_argument(
    "--model",
    default="iflow/qwen3-coder-plus",
    help="LLM model for optimization (default: iflow/qwen3-coder-plus)"
  )
  parser.add_argument(
    "--algorithm",
    choices=["miprov2", "simba"],
    default="simba",
    help="Optimization algorithm (default: simba - conservative for memory files)"
  )
  parser.add_argument(
    "--iterations",
    type=int,
    default=3,
    help="Number of optimization iterations (default: 3)"
  )
  parser.add_argument(
    "--focus-errors",
    help="Comma-separated list of errors to focus on (e.g., cycle_by_cycle_updates,scope_error)"
  )
  parser.add_argument(
    "--min-sessions",
    type=int,
    default=5,
    help="Minimum number of relevant sessions required (default: 5)"
  )
  
  args = parser.parse_args()
  
  # Validate inputs
  memory_file = Path(args.memory_file)
  if not memory_file.exists():
    print(f"❌ Error: Memory file not found: {memory_file}")
    sys.exit(1)
  
  sessions_file = Path(args.sessions)
  if not sessions_file.exists():
    print(f"❌ Error: Sessions file not found: {sessions_file}")
    sys.exit(1)
  
  # Parse focus errors
  focus_errors = None
  if args.focus_errors:
    focus_errors = [e.strip() for e in args.focus_errors.split(',')]
  
  print(f"📂 Memory file: {memory_file.name}")
  print(f"📊 Sessions file: {sessions_file}")
  if focus_errors:
    print(f"🎯 Focus errors: {', '.join(focus_errors)}")
  
  # Load sessions
  print(f"\n📥 Loading historical sessions...")
  with open(sessions_file) as f:
    all_sessions = json.load(f)
  print(f"✅ Loaded {len(all_sessions)} total sessions")
  
  # Filter relevant sessions
  print(f"\n🔍 Filtering sessions that used {memory_file.name}...")
  relevant_sessions = filter_relevant_sessions(
    all_sessions,
    memory_file.name,
    focus_errors
  )
  
  print(f"✅ Found {len(relevant_sessions)} relevant sessions")
  
  if len(relevant_sessions) < args.min_sessions:
    print(f"\n⚠️  Warning: Only {len(relevant_sessions)} relevant sessions found")
    print(f"   Minimum recommended: {args.min_sessions}")
    print(f"   Optimization may not be effective with limited data")
    
    response = input("\nContinue anyway? (y/n): ")
    if response.lower() != 'y':
      print("Aborted.")
      sys.exit(0)
  
  # Run optimization
  print(f"\n{'='*70}")
  print("STARTING OPTIMIZATION")
  print(f"{'='*70}\n")
  
  optimized_content = optimize_memory_file(
    memory_file=memory_file,
    sessions=relevant_sessions,
    output=Path(args.output),
    model=args.model,
    algorithm=args.algorithm,
    iterations=args.iterations,
    focus_errors=focus_errors
  )
  
  # Save optimized file
  output_path = Path(args.output)
  output_path.parent.mkdir(parents=True, exist_ok=True)
  output_path.write_text(optimized_content)
  
  print(f"\n{'='*70}")
  print("OPTIMIZATION COMPLETE")
  print(f"{'='*70}\n")
  
  # Show diff summary
  original_lines = memory_file.read_text().split('\n')
  optimized_lines = optimized_content.split('\n')
  
  print(f"📊 Summary:")
  print(f"   Original: {len(original_lines)} lines")
  print(f"   Optimized: {len(optimized_lines)} lines")
  print(f"   Change: {len(optimized_lines) - len(original_lines):+d} lines")
  print(f"\n💾 Optimized file saved to: {output_path}")
  
  print(f"\n💡 Next Steps:")
  print(f"   1. Review optimized file: {output_path}")
  print(f"   2. Compare with original: diff {memory_file} {output_path}")
  print(f"   3. Test with new sessions:")
  print(f"      cp {output_path} {memory_file}")
  print(f"      ./run-openspec-apply.sh <workdir> <change-id> standard")
  print(f"   4. Measure error rate reduction")
  print(f"   5. If improved, keep optimized version")
  print(f"   6. If not improved, try different focus-errors or more sessions\n")


if __name__ == "__main__":
  main()
