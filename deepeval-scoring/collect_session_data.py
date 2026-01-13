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

"""Collect historical session data for optimizer training.

This script scans a workspace for past agent sessions and creates a dataset
suitable for training DeepEval's PromptOptimizer.

Usage:
  python collect_session_data.py \\
    --workdir /path/to/project \\
    --output historical_sessions.json \\
    --min-score 0.5
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

from parsers.dml_parser import DMLParser
from parsers.test_parser import TestParser
from parsers.spec_parser import SpecParser
from parsers.session_parser import SessionParser


def extract_device_name_from_session(session_log: str) -> Optional[str]:
  """Extract device name from session log.
  
  Args:
    session_log: Session log content
    
  Returns:
    Device name or None
  """
  # Look for patterns like "implement-wdt", "device wdt", etc.
  patterns = [
    r'implement-(\w+)',
    r'device[:\s]+(\w+)',
    r'module[:\s]+(\w+)',
    r'--device\s+(\w+)'
  ]
  
  for pattern in patterns:
    match = re.search(pattern, session_log, re.IGNORECASE)
    if match:
      return match.group(1)
  
  return None


def extract_task_description(session_log: str, spec_content: str) -> str:
  """Extract task description from session and spec.
  
  Args:
    session_log: Session log content
    spec_content: Specification content
    
  Returns:
    Task description
  """
  # Try to extract from spec first
  if spec_content:
    # Look for overview or description section
    lines = spec_content.split("\n")
    description_lines = []
    in_description = False
    
    for line in lines:
      if re.match(r'^##?\s+(Overview|Description|Summary)', line, re.IGNORECASE):
        in_description = True
        continue
      elif in_description and re.match(r'^##?\s+', line):
        break
      elif in_description:
        description_lines.append(line)
    
    if description_lines:
      return "\n".join(description_lines).strip()
  
  # Fallback: extract from session log
  # Look for initial user message or task description
  lines = session_log.split("\n")
  for i, line in enumerate(lines[:50]):  # Check first 50 lines
    if "implement" in line.lower() or "create" in line.lower():
      # Take this line and next few lines
      return "\n".join(lines[i:min(i+5, len(lines))]).strip()
  
  return "No task description found"


def score_session(
    workdir: Path,
    device_name: str,
    model: str = "iflow/qwen3-coder-plus"
) -> Dict[str, Any]:
  """Score a session using our evaluation system.
  
  Args:
    workdir: Working directory
    device_name: Device name
    model: LLM model for evaluation
    
  Returns:
    Score results dictionary
  """
  from evaluators.code_evaluator import CodeEvaluator
  from evaluators.behavior_evaluator import BehaviorEvaluator
  
  try:
    # Run code evaluation
    code_eval = CodeEvaluator(
      workdir=str(workdir),
      device_name=device_name,
      model=model
    )
    code_results = code_eval.evaluate()
    
    # Run behavior evaluation (if session log exists)
    behavior_results = None
    try:
      behavior_eval = BehaviorEvaluator(
        workdir=str(workdir),
        device_name=device_name,
        model=model
      )
      behavior_results = behavior_eval.evaluate()
    except Exception:
      pass  # Behavior evaluation optional
    
    # Calculate overall score
    scores = [code_results["overall_score"]]
    if behavior_results:
      scores.append(behavior_results["overall_score"])
    
    overall_score = sum(scores) / len(scores)
    
    return {
      "overall_score": overall_score,
      "code_score": code_results["overall_score"],
      "behavior_score": behavior_results["overall_score"] if behavior_results else None,
      "metrics": {
        "code": code_results["metrics"],
        "behavior": behavior_results["metrics"] if behavior_results else None
      }
    }
    
  except Exception as e:
    print(f"⚠️  Warning: Failed to score session for {device_name}: {e}")
    return {
      "overall_score": 0.0,
      "code_score": 0.0,
      "behavior_score": None,
      "metrics": {}
    }


def collect_session(
    workdir: Path,
    session_file: Path,
    model: str,
    min_score: float
) -> Optional[Dict[str, Any]]:
  """Collect data from a single session.
  
  Args:
    workdir: Working directory
    session_file: Session log file
    model: LLM model for scoring
    min_score: Minimum score threshold
    
  Returns:
    Session data dictionary or None if invalid
  """
  print(f"📄 Processing: {session_file.name}")
  
  # Read session log
  session_log = session_file.read_text()
  
  # Extract device name
  device_name = extract_device_name_from_session(session_log)
  if not device_name:
    print(f"  ⚠️  Could not extract device name, skipping")
    return None
  
  print(f"  📦 Device: {device_name}")
  
  # Find implementation files
  dml_file = workdir / f"simics-project/modules/{device_name}/{device_name}.dml"
  if not dml_file.exists():
    print(f"  ⚠️  DML file not found: {dml_file}, skipping")
    return None
  
  # Parse implementation
  dml_parser = DMLParser()
  dml_data = dml_parser.parse_file(dml_file)
  implementation = dml_file.read_text()
  
  # Find test files
  test_dir = workdir / f"simics-project/modules/{device_name}/test"
  test_files = []
  if test_dir.exists():
    test_files = list(test_dir.glob("s-*.py"))
  
  tests_content = ""
  if test_files:
    tests_content = "\n\n".join([f.read_text() for f in test_files])
  
  # Find spec file
  spec_file = workdir / f"specs/{device_name}/spec.md"
  spec_content = ""
  if spec_file.exists():
    spec_content = spec_file.read_text()
  
  # Extract task description
  task_description = extract_task_description(session_log, spec_content)
  
  # Score this session
  print(f"  🔍 Scoring implementation...")
  score_result = score_session(workdir, device_name, model)
  overall_score = score_result["overall_score"]
  
  print(f"  📊 Score: {overall_score:.1%}")
  
  # Check minimum score threshold
  if overall_score < min_score:
    print(f"  ⚠️  Score below threshold ({min_score:.1%}), skipping")
    return None
  
  # Create session data
  session_data = {
    "device_name": device_name,
    "task_description": task_description,
    "implementation": implementation,
    "tests": tests_content,
    "spec": spec_content,
    "session_log": session_log,
    "score": overall_score,
    "metrics": score_result["metrics"],
    "dml_components": dml_data,
    "num_test_files": len(test_files),
    "session_file": str(session_file.relative_to(workdir))
  }
  
  print(f"  ✅ Session collected")
  return session_data


def main():
  parser = argparse.ArgumentParser(
    description="Collect historical session data for optimizer training"
  )
  parser.add_argument(
    "--workdir",
    required=True,
    help="Working directory to scan for sessions"
  )
  parser.add_argument(
    "--output",
    required=True,
    help="Output JSON file for collected data"
  )
  parser.add_argument(
    "--model",
    default="iflow/qwen3-coder-plus",
    help="LLM model for scoring (default: iflow/qwen3-coder-plus)"
  )
  parser.add_argument(
    "--min-score",
    type=float,
    default=0.5,
    help="Minimum score threshold (default: 0.5)"
  )
  parser.add_argument(
    "--pattern",
    default="**/*.session.txt",
    help="Glob pattern for session files (default: **/*.session.txt)"
  )
  
  args = parser.parse_args()
  
  workdir = Path(args.workdir)
  if not workdir.exists():
    print(f"❌ Error: Workdir does not exist: {workdir}")
    sys.exit(1)
  
  print(f"🔍 Scanning for session files in: {workdir}")
  print(f"📋 Pattern: {args.pattern}")
  print(f"📊 Minimum score: {args.min_score:.1%}")
  print("="*60)
  
  # Find all session files
  session_files = list(workdir.glob(args.pattern))
  print(f"\n📁 Found {len(session_files)} session files")
  
  if not session_files:
    print("❌ No session files found")
    sys.exit(1)
  
  # Collect data from each session
  collected_sessions = []
  for session_file in session_files:
    session_data = collect_session(
      workdir=workdir,
      session_file=session_file,
      model=args.model,
      min_score=args.min_score
    )
    
    if session_data:
      collected_sessions.append(session_data)
    
    print()  # Blank line between sessions
  
  print("="*60)
  print(f"\n✅ Collected {len(collected_sessions)} sessions")
  
  if not collected_sessions:
    print("❌ No sessions met the criteria")
    sys.exit(1)
  
  # Save to JSON
  output_path = Path(args.output)
  output_path.parent.mkdir(parents=True, exist_ok=True)
  
  with open(output_path, 'w') as f:
    json.dump(collected_sessions, f, indent=2)
  
  print(f"💾 Data saved to: {output_path}")
  
  # Print summary statistics
  scores = [s["score"] for s in collected_sessions]
  avg_score = sum(scores) / len(scores)
  min_score_val = min(scores)
  max_score_val = max(scores)
  
  print(f"\n📊 Summary Statistics:")
  print(f"  Average Score: {avg_score:.1%}")
  print(f"  Min Score: {min_score_val:.1%}")
  print(f"  Max Score: {max_score_val:.1%}")
  print(f"  Total Sessions: {len(collected_sessions)}")
  
  # Device breakdown
  devices = {}
  for session in collected_sessions:
    device = session["device_name"]
    devices[device] = devices.get(device, 0) + 1
  
  print(f"\n📦 Devices:")
  for device, count in sorted(devices.items()):
    print(f"  {device}: {count} session(s)")
  
  print(f"\n💡 Next step:")
  print(f"  python optimize_instructions.py \\")
  print(f"    --historical-data {output_path} \\")
  print(f"    --current-instructions apply_agent_instruction.md \\")
  print(f"    --output optimized_instructions.md")


if __name__ == "__main__":
  main()
