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

"""Report generator for evaluation results."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Dict, Optional


class ReportGenerator:
  """Generates evaluation reports in various formats."""
  
  def generate(
      self,
      code_results: Optional[Dict] = None,
      behavior_results: Optional[Dict] = None,
      deterministic_results: Optional[Dict] = None,
      format: str = "markdown",
      device_name: str = "",
      model: str = "",
      scoring_mode: str = "llm"
  ) -> str:
    """Generate evaluation report.
    
    Args:
      code_results: LLM-based code evaluation results (optional)
      behavior_results: Behavior evaluation results (optional)
      deterministic_results: Deterministic evaluation results (optional)
      format: Output format (markdown, json, html)
      device_name: Device name
      model: Model used for evaluation
      scoring_mode: Scoring mode used
    
    Returns:
      Report as string
    """
    if format == "markdown":
      return self._generate_markdown(
        code_results, behavior_results, deterministic_results, 
        device_name, model, scoring_mode
      )
    elif format == "json":
      return self._generate_json(
        code_results, behavior_results, deterministic_results, scoring_mode
      )
    elif format == "html":
      return self._generate_html(
        code_results, behavior_results, deterministic_results,
        device_name, model, scoring_mode
      )
    else:
      raise ValueError(f"Unsupported format: {format}")
  
  def _generate_markdown(
      self,
      code_results: Optional[Dict],
      behavior_results: Optional[Dict],
      deterministic_results: Optional[Dict],
      device_name: str,
      model: str,
      scoring_mode: str
  ) -> str:
    """Generate markdown report."""
    lines = []
    
    # Header
    lines.append("# DeepEval Scoring Report")
    lines.append("")
    lines.append(f"**Device**: {device_name}")
    lines.append(f"**Model**: {model}")
    lines.append(f"**Scoring Mode**: {scoring_mode.upper()}")
    lines.append(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    # Overall score
    overall = self._calculate_overall(code_results, behavior_results, deterministic_results, scoring_mode)
    lines.append("## Overall Score")
    lines.append("")
    lines.append(f"**{overall:.1%}**")
    lines.append("")
    
    # Deterministic scoring section
    if deterministic_results:
      lines.append("## Deterministic Analysis (Parser-Based)")
      lines.append("")
      det_score = deterministic_results["overall_score"]
      lines.append(f"**Score**: {det_score:.1%}")
      lines.append("")
      
      lines.append("### Component Scores")
      lines.append("")
      for component, score in deterministic_results["component_scores"].items():
        weight = deterministic_results["weights"][component]
        lines.append(f"- **{component.replace('_', ' ').title()}**: {score:.1%} (weight: {weight:.1%})")
      lines.append("")
      
      lines.append("### Implementation Details")
      lines.append("")
      details = deterministic_results["details"]
      lines.append(f"- DML file exists: {'✅' if details['dml_file_exists'] else '❌'}")
      lines.append(f"- Registers found: {details['registers_found']}")
      lines.append(f"- Methods found: {details['methods_found']}")
      lines.append(f"- Events found: {details['events_found']}")
      lines.append(f"- Test files found: {details['test_files_found']}")
      lines.append(f"- Has session variables: {'✅' if details['has_session_variables'] else '❌'}")
      lines.append(f"- Has reset logic: {'✅' if details['has_reset_logic'] else '❌'}")
      lines.append(f"- Has interrupt logic: {'✅' if details['has_interrupt_logic'] else '❌'}")
      lines.append("")
    
    # LLM-based code quality section
    if code_results:
      lines.append("## LLM Code Quality Analysis")
      lines.append("")
      code_score = code_results["overall_score"]
      lines.append(f"**Score**: {code_score:.1%}")
      lines.append("")
      
      for metric_name, result in code_results["metrics"].items():
        lines.append(f"### {metric_name}")
        lines.append("")
        lines.append(f"**Score**: {result['score']:.1%}")
        lines.append(f"**Threshold**: {result['threshold']:.1%}")
        lines.append(f"**Status**: {'✅ Pass' if result['success'] else '❌ Fail'}")
        lines.append("")
        if result.get("reason"):
          lines.append("**Details**:")
          lines.append("")
          lines.append(result["reason"])
          lines.append("")
    
    # Agent behavior section
    if behavior_results:
      lines.append("## Agent Behavior Analysis")
      lines.append("")
      behavior_score = behavior_results["overall_score"]
      lines.append(f"**Score**: {behavior_score:.1%}")
      lines.append("")
      
      for metric_name, result in behavior_results["metrics"].items():
        lines.append(f"### {metric_name}")
        lines.append("")
        lines.append(f"**Score**: {result['score']:.1%}")
        lines.append(f"**Threshold**: {result['threshold']:.1%}")
        lines.append(f"**Status**: {'✅ Pass' if result['success'] else '❌ Fail'}")
        lines.append("")
        if result.get("reason"):
          lines.append("**Details**:")
          lines.append("")
          lines.append(result["reason"])
          lines.append("")
    
    # Recommendations
    lines.append("## Recommendations")
    lines.append("")
    lines.extend(self._generate_recommendations(code_results, behavior_results, deterministic_results))
    
    return "\n".join(lines)
  
  def _generate_json(
      self,
      code_results: Optional[Dict],
      behavior_results: Optional[Dict],
      deterministic_results: Optional[Dict],
      scoring_mode: str
  ) -> str:
    """Generate JSON report."""
    data = {
      "timestamp": datetime.now().isoformat(),
      "scoring_mode": scoring_mode,
      "overall_score": self._calculate_overall(code_results, behavior_results, deterministic_results, scoring_mode),
      "deterministic_analysis": deterministic_results,
      "llm_code_quality": code_results,
      "agent_behavior": behavior_results
    }
    return json.dumps(data, indent=2)
  
  def _generate_html(
      self,
      code_results: Optional[Dict],
      behavior_results: Optional[Dict],
      deterministic_results: Optional[Dict],
      device_name: str,
      model: str,
      scoring_mode: str
  ) -> str:
    """Generate HTML report."""
    # Simple HTML template
    overall = self._calculate_overall(code_results, behavior_results, deterministic_results, scoring_mode)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
  <title>DeepEval Scoring Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 40px; }}
    h1 {{ color: #333; }}
    .score {{ font-size: 24px; font-weight: bold; color: #4CAF50; }}
    .metric {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
    .pass {{ color: #4CAF50; }}
    .fail {{ color: #f44336; }}
  </style>
</head>
<body>
  <h1>DeepEval Scoring Report</h1>
  <p><strong>Device:</strong> {device_name}</p>
  <p><strong>Model:</strong> {model}</p>
  <p><strong>Scoring Mode:</strong> {scoring_mode.upper()}</p>
  <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
  
  <h2>Overall Score</h2>
  <p class="score">{overall:.1%}</p>
"""
    
    # Deterministic results
    if deterministic_results:
      html += f"""
  <h2>Deterministic Analysis</h2>
  <p class="score">{deterministic_results['overall_score']:.1%}</p>
"""
      for component, score in deterministic_results["component_scores"].items():
        html += f"""
  <div class="metric">
    <h3>{component.replace('_', ' ').title()}</h3>
    <p><strong>Score:</strong> {score:.1%}</p>
  </div>
"""
    
    # LLM code results
    if code_results:
      html += f"""
  <h2>LLM Code Quality</h2>
  <p class="score">{code_results['overall_score']:.1%}</p>
"""
      for metric_name, result in code_results["metrics"].items():
        status_class = "pass" if result["success"] else "fail"
        html += f"""
  <div class="metric">
    <h3>{metric_name}</h3>
    <p><strong>Score:</strong> {result['score']:.1%}</p>
    <p class="{status_class}"><strong>Status:</strong> {'✅ Pass' if result['success'] else '❌ Fail'}</p>
    <p>{result.get('reason', '')}</p>
  </div>
"""
    
    if behavior_results:
      html += f"""
  <h2>Agent Behavior</h2>
  <p class="score">{behavior_results['overall_score']:.1%}</p>
"""
      for metric_name, result in behavior_results["metrics"].items():
        status_class = "pass" if result["success"] else "fail"
        html += f"""
  <div class="metric">
    <h3>{metric_name}</h3>
    <p><strong>Score:</strong> {result['score']:.1%}</p>
    <p class="{status_class}"><strong>Status:</strong> {'✅ Pass' if result['success'] else '❌ Fail'}</p>
    <p>{result.get('reason', '')}</p>
  </div>
"""
    
    html += """
</body>
</html>
"""
    return html
  
  def _calculate_overall(
      self,
      code_results: Optional[Dict],
      behavior_results: Optional[Dict],
      deterministic_results: Optional[Dict],
      scoring_mode: str
  ) -> float:
    """Calculate overall score."""
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
      # Same logic as in score.py
      total_score = 0.0
      total_weight = 0.0
      
      if deterministic_results:
        total_score += deterministic_results["overall_score"] * 0.4
        total_weight += 0.4
      
      if code_results:
        total_score += code_results["overall_score"] * 0.4
        total_weight += 0.4
      
      if behavior_results:
        total_score += behavior_results["overall_score"] * 0.2
        total_weight += 0.2
      
      return total_score / total_weight if total_weight > 0 else 0.0
    
    return 0.0
  
  def _generate_recommendations(
      self,
      code_results: Optional[Dict],
      behavior_results: Optional[Dict],
      deterministic_results: Optional[Dict]
  ) -> list[str]:
    """Generate recommendations based on results."""
    recommendations = []
    
    # Check deterministic metrics
    if deterministic_results:
      for component, score in deterministic_results["component_scores"].items():
        if score < 0.7:  # Threshold for recommendations
          recommendations.append(
            f"- Improve {component.replace('_', ' ')}: Currently at {score:.1%}"
          )
    
    # Check LLM code quality metrics
    if code_results:
      for metric_name, result in code_results["metrics"].items():
        if not result["success"]:
          recommendations.append(
            f"- Improve {metric_name}: Currently at {result['score']:.1%}, "
            f"needs {result['threshold']:.1%}"
          )
    
    # Check behavior metrics
    if behavior_results:
      for metric_name, result in behavior_results["metrics"].items():
        if not result["success"]:
          recommendations.append(
            f"- Improve {metric_name}: Currently at {result['score']:.1%}, "
            f"needs {result['threshold']:.1%}"
          )
    
    if not recommendations:
      recommendations.append("- All metrics passed! Great work! 🎉")
    
    return recommendations
