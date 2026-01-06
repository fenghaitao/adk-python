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
  # Full evaluation (code + behavior)
  python score.py --workdir /path/to/project --device wdt --model iflow/qwen3-coder-plus --agent kiro-cli
  
  # Code evaluation only
  python score.py --workdir /path/to/project --device wdt --model iflow/qwen3-coder-plus --result-only
  
  # Behavior evaluation only
  python score.py --workdir /path/to/project --device wdt --model iflow/qwen3-coder-plus --agent kiro-cli --behavior-only
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Optional

from evaluators.code_evaluator import CodeEvaluator
from evaluators.behavior_evaluator import BehaviorEvaluator
from metrics.deterministic_scoring import DeterministicScorer
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
    "--result-only",
    action="store_true",
    help="Skip agent behavior evaluation and only evaluate code results"
  )
  parser.add_argument(
    "--behavior-only",
    action="store_true",
    help="Skip code evaluation and only evaluate agent behavior"
  )
  parser.add_argument(
    "--scoring-mode",
    choices=["llm", "deterministic", "hybrid"],
    default="llm",
    help="Scoring mode: llm (LLM-based), deterministic (parser-based), or hybrid (both)"
  )
  parser.add_argument(
    "--agent",
    help="Agent type for behavior evaluation (e.g., rovodev, copilot-cli, kiro-cli, adk-python, qodercli)"
  )
  
  args = parser.parse_args()
  
  # Validate mutually exclusive options
  if args.result_only and args.behavior_only:
    print("❌ Error: --result-only and --behavior-only are mutually exclusive")
    sys.exit(1)
  
  # Initialize evaluators based on scoring mode and options
  code_results = None
  deterministic_results = None
  
  # Skip code evaluation if behavior-only mode
  if not args.behavior_only:
    if args.scoring_mode in ["llm", "hybrid"]:
      # LLM-based evaluation
      code_eval = CodeEvaluator(
        workdir=args.workdir,
        device_name=args.device,
        model=args.model
      )
      print("🔍 Evaluating code quality with LLM...")
      code_results = code_eval.evaluate()
    
    if args.scoring_mode in ["deterministic", "hybrid"]:
      # Deterministic evaluation
      deterministic_scorer = DeterministicScorer(
        workdir=args.workdir,
        device_name=args.device
      )
      print("🔍 Evaluating code quality with deterministic scoring...")
      deterministic_results = deterministic_scorer.score_implementation()
  
  # Skip behavior evaluation if result-only mode or deterministic-only mode
  behavior_eval = None
  if not args.result_only and args.scoring_mode != "deterministic":
    behavior_eval = BehaviorEvaluator(
      workdir=args.workdir,
      device_name=args.device,
      model=args.model,
      agent=args.agent
    )
  
  # Run behavior evaluation (only for LLM modes and when not skipped)
  behavior_results = None
  if behavior_eval:
    print("🔍 Evaluating agent behavior with G-Eval...")
    behavior_results = behavior_eval.evaluate()
  
  # Generate report
  print("📝 Generating report...")
  report_gen = ReportGenerator()
  report = report_gen.generate(
    code_results=code_results,
    behavior_results=behavior_results,
    deterministic_results=deterministic_results,
    format=args.format,
    device_name=args.device,
    model=args.model,
    scoring_mode=args.scoring_mode
  )
  
  # Save report
  output_path = Path(args.workdir) / args.output
  output_path.write_text(report)
  
  print(f"✅ Report saved to: {output_path}")
  
  # Print summary
  print_summary(code_results, behavior_results, deterministic_results, args.scoring_mode)
  
  # Exit with appropriate code
  overall_score = calculate_overall_score(code_results, behavior_results, deterministic_results, args.scoring_mode)
  sys.exit(0 if overall_score >= 0.7 else 1)


def print_summary(
    code_results: Optional[Dict], 
    behavior_results: Optional[Dict],
    deterministic_results: Optional[Dict],
    scoring_mode: str
):
  """Print summary to console."""
  print("\n" + "="*60)
  print("EVALUATION SUMMARY")
  print("="*60)
  
  # Deterministic scoring
  if deterministic_results:
    det_score = deterministic_results["overall_score"]
    print(f"\n🔧 Deterministic Score: {det_score:.1%} ({det_score * 90:.0f}/90)")
    for metric_name, score in deterministic_results["component_scores"].items():
      print(f"  • {metric_name.replace('_', ' ').title()}: {score:.1%}")
  
  # LLM-based code quality
  if code_results:
    code_score = code_results["overall_score"]
    print(f"\n📊 LLM Code Quality: {code_score:.1%} ({code_score * 90:.0f}/90)")
    for metric_name, result in code_results["metrics"].items():
      print(f"  • {metric_name}: {result['score']:.1%}")
  
  # Agent behavior
  if behavior_results:
    behavior_score = behavior_results["overall_score"]
    print(f"\n🤖 Agent Behavior: {behavior_score:.1%} ({behavior_score * 90:.0f}/90)")
    for metric_name, result in behavior_results["metrics"].items():
      print(f"  • {metric_name}: {result['score']:.1%}")
  
  # Overall
  overall = calculate_overall_score(code_results, behavior_results, deterministic_results, scoring_mode)
  
  if scoring_mode == "hybrid":
    print(f"\n🎯 Hybrid Score: {overall:.1%}")
    print("   Weighting: 40% Deterministic + 40% LLM Code + 20% Behavior")
  else:
    total_points = _calculate_total_points(code_results, behavior_results, deterministic_results)
    print(f"\n🎯 Overall Score: {overall:.1%} ({overall * total_points:.0f}/{total_points})")
  
  print(f"📋 Scoring Mode: {scoring_mode.upper()}")
  print("="*60 + "\n")


def calculate_overall_score(
    code_results: Optional[Dict],
    behavior_results: Optional[Dict],
    deterministic_results: Optional[Dict],
    scoring_mode: str
) -> float:
  """Calculate overall score based on available results."""
  
  if scoring_mode == "deterministic":
    if deterministic_results:
      return deterministic_results["overall_score"]
    return 0.0
    
  elif scoring_mode == "llm":
    scores = []
    if code_results:
      scores.append(code_results["overall_score"])
    if behavior_results:
      scores.append(behavior_results["overall_score"])
    return sum(scores) / len(scores) if scores else 0.0
    
  elif scoring_mode == "hybrid":
    # Hybrid mode: Use deterministic for objective metrics, LLM for subjective
    # Weight: 40% deterministic (objective), 40% LLM code quality (subjective), 20% behavior
    
    total_score = 0.0
    total_weight = 0.0
    
    # Deterministic scoring (objective metrics)
    if deterministic_results:
      total_score += deterministic_results["overall_score"] * 0.4
      total_weight += 0.4
    
    # LLM code quality (subjective analysis)
    if code_results:
      total_score += code_results["overall_score"] * 0.4
      total_weight += 0.4
    
    # Agent behavior (process evaluation)
    if behavior_results:
      total_score += behavior_results["overall_score"] * 0.2
      total_weight += 0.2
    
    return total_score / total_weight if total_weight > 0 else 0.0
  
  return 0.0


def _calculate_total_points(
    code_results: Optional[Dict],
    behavior_results: Optional[Dict], 
    deterministic_results: Optional[Dict]
) -> int:
  """Calculate total possible points based on what was evaluated."""
  # Each component contributes 90 points when present
  points = 0
  if code_results:
    points += 90
  if behavior_results:
    points += 90
  if deterministic_results:
    points += 90
  return points if points > 0 else 90


if __name__ == "__main__":
  main()
