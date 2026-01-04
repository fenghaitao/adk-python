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

"""DeepEval-based scoring system for apply_agent implementations.

Usage:
  python score.py --workdir /path/to/project --device wdt --model iflow/qwen3-coder-plus
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Optional

from evaluators.code_evaluator import CodeEvaluator
from evaluators.behavior_evaluator import BehaviorEvaluator
from report_generator import ReportGenerator


def main():
  parser = argparse.ArgumentParser(
    description="Score apply_agent implementation using DeepEval"
  )
  parser.add_argument(
    "--workdir",
    required=True,
    help="Working directory containing the implementation"
  )
  parser.add_argument(
    "--device",
    required=True,
    help="Device name (e.g., wdt)"
  )
  parser.add_argument(
    "--model",
    default="iflow/qwen3-coder-plus",
    help="LLM model for evaluation (default: iflow/qwen3-coder-plus)"
  )
  parser.add_argument(
    "--output",
    default="score.md",
    help="Output report file (default: score.md)"
  )
  parser.add_argument(
    "--format",
    choices=["markdown", "json", "html"],
    default="markdown",
    help="Output format (default: markdown)"
  )
  parser.add_argument(
    "--skip-behavior",
    action="store_true",
    help="Skip agent behavior evaluation (if no session logs)"
  )
  
  args = parser.parse_args()
  
  # Initialize evaluators
  code_eval = CodeEvaluator(
    workdir=args.workdir,
    device_name=args.device,
    model=args.model
  )
  
  behavior_eval = BehaviorEvaluator(
    workdir=args.workdir,
    device_name=args.device,
    model=args.model
  ) if not args.skip_behavior else None
  
  # Run evaluations
  print("🔍 Evaluating code quality...")
  code_results = code_eval.evaluate()
  
  behavior_results = None
  if behavior_eval:
    print("🔍 Evaluating agent behavior...")
    behavior_results = behavior_eval.evaluate()
  
  # Generate report
  print("📝 Generating report...")
  report_gen = ReportGenerator()
  report = report_gen.generate(
    code_results=code_results,
    behavior_results=behavior_results,
    format=args.format,
    device_name=args.device,
    model=args.model
  )
  
  # Save report
  output_path = Path(args.workdir) / args.output
  output_path.write_text(report)
  
  print(f"✅ Report saved to: {output_path}")
  
  # Print summary
  print_summary(code_results, behavior_results)
  
  # Exit with appropriate code
  overall_score = calculate_overall_score(code_results, behavior_results)
  sys.exit(0 if overall_score >= 0.7 else 1)


def print_summary(code_results: Dict, behavior_results: Optional[Dict]):
  """Print summary to console."""
  print("\n" + "="*60)
  print("EVALUATION SUMMARY")
  print("="*60)
  
  # Code quality
  code_score = code_results["overall_score"]
  print(f"\n📊 Code Quality: {code_score:.1%} ({code_score * 90:.0f}/90)")
  for metric_name, result in code_results["metrics"].items():
    print(f"  • {metric_name}: {result['score']:.1%}")
  
  # Agent behavior
  if behavior_results:
    behavior_score = behavior_results["overall_score"]
    print(f"\n🤖 Agent Behavior: {behavior_score:.1%} ({behavior_score * 90:.0f}/90)")
    for metric_name, result in behavior_results["metrics"].items():
      print(f"  • {metric_name}: {result['score']:.1%}")
  
  # Overall
  overall = calculate_overall_score(code_results, behavior_results)
  total_points = 180 if behavior_results else 90
  print(f"\n🎯 Overall Score: {overall:.1%} ({overall * total_points:.0f}/{total_points})")
  print("="*60 + "\n")


def calculate_overall_score(
    code_results: Dict,
    behavior_results: Optional[Dict]
) -> float:
  """Calculate overall score."""
  if behavior_results:
    return (code_results["overall_score"] + behavior_results["overall_score"]) / 2
  return code_results["overall_score"]


if __name__ == "__main__":
  main()
