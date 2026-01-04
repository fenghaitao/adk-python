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
      code_results: Dict,
      behavior_results: Optional[Dict],
      format: str = "markdown",
      device_name: str = "",
      model: str = ""
  ) -> str:
    """Generate evaluation report.
    
    Args:
      code_results: Code evaluation results
      behavior_results: Behavior evaluation results (optional)
      format: Output format (markdown, json, html)
      device_name: Device name
      model: Model used for evaluation
    
    Returns:
      Report as string
    """
    if format == "markdown":
      return self._generate_markdown(
        code_results, behavior_results, device_name, model
      )
    elif format == "json":
      return self._generate_json(code_results, behavior_results)
    elif format == "html":
      return self._generate_html(
        code_results, behavior_results, device_name, model
      )
    else:
      raise ValueError(f"Unsupported format: {format}")
  
  def _generate_markdown(
      self,
      code_results: Dict,
      behavior_results: Optional[Dict],
      device_name: str,
      model: str
  ) -> str:
    """Generate markdown report."""
    lines = []
    
    # Header
    lines.append("# DeepEval Scoring Report")
    lines.append("")
    lines.append(f"**Device**: {device_name}")
    lines.append(f"**Model**: {model}")
    lines.append(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    # Overall score
    overall = self._calculate_overall(code_results, behavior_results)
    total_points = 180 if behavior_results else 90
    lines.append("## Overall Score")
    lines.append("")
    lines.append(f"**{overall:.1%}** ({overall * total_points:.0f}/{total_points} points)")
    lines.append("")
    
    # Code quality section
    lines.append("## Code Quality (90 points)")
    lines.append("")
    code_score = code_results["overall_score"]
    lines.append(f"**Score**: {code_score:.1%} ({code_score * 90:.0f}/90)")
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
      lines.append("## Agent Behavior (90 points)")
      lines.append("")
      behavior_score = behavior_results["overall_score"]
      lines.append(f"**Score**: {behavior_score:.1%} ({behavior_score * 90:.0f}/90)")
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
    lines.extend(self._generate_recommendations(code_results, behavior_results))
    
    return "\n".join(lines)
  
  def _generate_json(
      self,
      code_results: Dict,
      behavior_results: Optional[Dict]
  ) -> str:
    """Generate JSON report."""
    data = {
      "timestamp": datetime.now().isoformat(),
      "overall_score": self._calculate_overall(code_results, behavior_results),
      "code_quality": code_results,
      "agent_behavior": behavior_results
    }
    return json.dumps(data, indent=2)
  
  def _generate_html(
      self,
      code_results: Dict,
      behavior_results: Optional[Dict],
      device_name: str,
      model: str
  ) -> str:
    """Generate HTML report."""
    # Simple HTML template
    overall = self._calculate_overall(code_results, behavior_results)
    total_points = 180 if behavior_results else 90
    
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
  <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
  
  <h2>Overall Score</h2>
  <p class="score">{overall:.1%} ({overall * total_points:.0f}/{total_points} points)</p>
  
  <h2>Code Quality</h2>
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
      code_results: Dict,
      behavior_results: Optional[Dict]
  ) -> float:
    """Calculate overall score."""
    if behavior_results:
      return (code_results["overall_score"] + behavior_results["overall_score"]) / 2
    return code_results["overall_score"]
  
  def _generate_recommendations(
      self,
      code_results: Dict,
      behavior_results: Optional[Dict]
  ) -> list[str]:
    """Generate recommendations based on results."""
    recommendations = []
    
    # Check code quality metrics
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
