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

"""Scoring tools for agent evaluation.

This module provides MCP-style tools that agents can use to score themselves
and other agents.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict

from google.adk.tools.toolset import Toolset

try:
  from .agent_scoring import (
    ApplyAgentScore,
    ApplyImproveAgentScore,
    MetaImproveAgentScore,
  )
except ImportError:
  from agent_scoring import (
    ApplyAgentScore,
    ApplyImproveAgentScore,
    MetaImproveAgentScore,
  )


def score_apply_agent_session(
  session_file: str,
  build_attempts: int,
  time_minutes: float,
  error_types_count: int,
  final_success: bool,
  tests_passed: int = 0,
  tests_total: int = 0
) -> Dict[str, Any]:
  """Score an apply_agent session.
  
  Args:
    session_file: Path to the session file
    build_attempts: Number of build attempts
    time_minutes: Time taken in minutes
    error_types_count: Number of unique error types
    final_success: Whether the task completed successfully
    tests_passed: Number of tests passed
    tests_total: Total number of tests
    
  Returns:
    Dictionary with score and improvement suggestions
  """
  score = ApplyAgentScore(
    build_attempts=build_attempts,
    time_minutes=time_minutes,
    error_types_count=error_types_count,
    final_success=final_success,
    tests_passed=tests_passed,
    tests_total=tests_total
  )
  
  score.calculate_score()
  
  return {
    "session_file": session_file,
    "score": {
      "overall": round(score.overall_score, 2),
      "grade": score.grade,
      "build_attempts": round(score.build_attempts_score, 2),
      "time": round(score.time_score, 2),
      "error_types": round(score.error_types_score, 2),
      "success": round(score.success_score, 2)
    },
    "metrics": {
      "build_attempts": build_attempts,
      "time_minutes": time_minutes,
      "error_types_count": error_types_count,
      "final_success": final_success,
      "tests_passed": tests_passed,
      "tests_total": tests_total
    },
    "improvement_suggestions": score.get_improvement_suggestions()
  }


def score_apply_improve_agent_session(
  session_file: str,
  dimensions_covered: int,
  recommendations_count: int,
  recommendations_specific: int,
  recommendations_actionable: int,
  evidence_provided: bool,
  evidence_specific: bool,
  error_patterns_identified: int,
  best_practices_analyzed: bool,
  exact_text_provided: bool,
  location_specified: bool,
  impact_quantified: bool
) -> Dict[str, Any]:
  """Score an apply_improve_agent session.
  
  Args:
    session_file: Path to the session file
    dimensions_covered: Number of dimensions analyzed
    recommendations_count: Total number of recommendations
    recommendations_specific: Recommendations with code blocks
    recommendations_actionable: Actionable recommendations
    evidence_provided: Whether evidence was provided
    evidence_specific: Whether evidence is specific (quotes)
    error_patterns_identified: Number of error patterns found
    best_practices_analyzed: Whether best practices were analyzed
    exact_text_provided: Whether exact text was provided
    location_specified: Whether location was specified
    impact_quantified: Whether impact was quantified
    
  Returns:
    Dictionary with score and improvement suggestions
  """
  score = ApplyImproveAgentScore(
    dimensions_covered=dimensions_covered,
    recommendations_count=recommendations_count,
    recommendations_specific=recommendations_specific,
    recommendations_actionable=recommendations_actionable,
    evidence_provided=evidence_provided,
    evidence_specific=evidence_specific,
    error_patterns_identified=error_patterns_identified,
    best_practices_analyzed=best_practices_analyzed,
    exact_text_provided=exact_text_provided,
    location_specified=location_specified,
    impact_quantified=impact_quantified
  )
  
  score.calculate_score()
  
  return {
    "session_file": session_file,
    "score": {
      "overall": round(score.overall_score, 2),
      "grade": score.grade,
      "analysis_depth": round(score.analysis_depth_score, 2),
      "recommendation_quality": round(score.recommendation_quality_score, 2),
      "evidence_quality": round(score.evidence_quality_score, 2),
      "coverage": round(score.coverage_score, 2),
      "actionability": round(score.actionability_score, 2)
    },
    "metrics": {
      "dimensions_covered": dimensions_covered,
      "recommendations_count": recommendations_count,
      "recommendations_specific": recommendations_specific,
      "recommendations_actionable": recommendations_actionable,
      "evidence_provided": evidence_provided,
      "evidence_specific": evidence_specific,
      "error_patterns_identified": error_patterns_identified,
      "best_practices_analyzed": best_practices_analyzed,
      "exact_text_provided": exact_text_provided,
      "location_specified": location_specified,
      "impact_quantified": impact_quantified
    },
    "improvement_suggestions": score.get_improvement_suggestions()
  }


def score_meta_improve_agent_session(
  session_file: str,
  reference_file: str,
  dimensions_covered: int,
  dimensions_in_reference: int,
  recommendations_with_code: int,
  recommendations_with_code_in_reference: int,
  evidence_quotes_count: int,
  evidence_quotes_in_reference: int,
  follows_reference_structure: bool,
  impact_quantified_count: int,
  impact_quantified_in_reference: int
) -> Dict[str, Any]:
  """Score a meta_improve_agent session against a reference.
  
  Args:
    session_file: Path to the session file
    reference_file: Path to the reference analysis file
    dimensions_covered: Dimensions covered by agent
    dimensions_in_reference: Dimensions in reference
    recommendations_with_code: Agent's code blocks
    recommendations_with_code_in_reference: Reference's code blocks
    evidence_quotes_count: Agent's evidence quotes
    evidence_quotes_in_reference: Reference's evidence quotes
    follows_reference_structure: Whether structure matches reference
    impact_quantified_count: Agent's quantified impacts
    impact_quantified_in_reference: Reference's quantified impacts
    
  Returns:
    Dictionary with score and improvement suggestions
  """
  score = MetaImproveAgentScore(
    reference_file=reference_file,
    dimensions_covered=dimensions_covered,
    dimensions_in_reference=dimensions_in_reference,
    recommendations_with_code=recommendations_with_code,
    recommendations_with_code_in_reference=recommendations_with_code_in_reference,
    evidence_quotes_count=evidence_quotes_count,
    evidence_quotes_in_reference=evidence_quotes_in_reference,
    follows_reference_structure=follows_reference_structure,
    impact_quantified_count=impact_quantified_count,
    impact_quantified_in_reference=impact_quantified_in_reference
  )
  
  score.calculate_score()
  
  return {
    "session_file": session_file,
    "reference_file": reference_file,
    "score": {
      "overall": round(score.overall_score, 2),
      "grade": score.grade,
      "coverage": round(score.coverage_score, 2),
      "specificity": round(score.specificity_score, 2),
      "evidence": round(score.evidence_score, 2),
      "structure": round(score.structure_score, 2),
      "impact": round(score.impact_score, 2)
    },
    "metrics": {
      "dimensions_covered": dimensions_covered,
      "dimensions_in_reference": dimensions_in_reference,
      "recommendations_with_code": recommendations_with_code,
      "recommendations_with_code_in_reference": recommendations_with_code_in_reference,
      "evidence_quotes_count": evidence_quotes_count,
      "evidence_quotes_in_reference": evidence_quotes_in_reference,
      "follows_reference_structure": follows_reference_structure,
      "impact_quantified_count": impact_quantified_count,
      "impact_quantified_in_reference": impact_quantified_in_reference
    },
    "improvement_suggestions": score.get_improvement_suggestions()
  }


def create_scoring_toolset() -> Toolset:
  """Create a toolset with scoring tools.
  
  Returns:
    Toolset with scoring tools
  """
  return Toolset(
    name="scoring_tools",
    description="Tools for scoring agent performance",
    tools=[
      score_apply_agent_session,
      score_apply_improve_agent_session,
      score_meta_improve_agent_session
    ]
  )


# Example usage
if __name__ == "__main__":
  # Test scoring tools
  print("=== Testing Scoring Tools ===\n")
  
  # Test 1: Score apply_agent
  print("1. Scoring apply_agent session:")
  result1 = score_apply_agent_session(
    session_file="apply_implement-wdt-watchdog_20251218_175839.session.txt",
    build_attempts=15,
    time_minutes=8.98,
    error_types_count=3,
    final_success=True,
    tests_passed=0,
    tests_total=5
  )
  print(json.dumps(result1, indent=2))
  
  # Test 2: Score apply_improve_agent
  print("\n2. Scoring apply_improve_agent session:")
  result2 = score_apply_improve_agent_session(
    session_file="apply_improve_apply_improve_20251219_204307.session.txt",
    dimensions_covered=3,
    recommendations_count=5,
    recommendations_specific=3,
    recommendations_actionable=4,
    evidence_provided=True,
    evidence_specific=False,
    error_patterns_identified=3,
    best_practices_analyzed=True,
    exact_text_provided=False,
    location_specified=True,
    impact_quantified=True
  )
  print(json.dumps(result2, indent=2))
  
  # Test 3: Score meta_improve_agent
  print("\n3. Scoring meta_improve_agent session:")
  result3 = score_meta_improve_agent_session(
    session_file="meta_improve_meta_improve_20251220_120000.session.txt",
    reference_file="reference_analysis_20251220_apply_improve_text.md",
    dimensions_covered=6,
    dimensions_in_reference=7,
    recommendations_with_code=5,
    recommendations_with_code_in_reference=7,
    evidence_quotes_count=10,
    evidence_quotes_in_reference=21,
    follows_reference_structure=True,
    impact_quantified_count=5,
    impact_quantified_in_reference=7
  )
  print(json.dumps(result3, indent=2))
