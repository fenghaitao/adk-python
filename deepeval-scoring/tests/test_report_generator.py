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

"""Tests for report generator."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from report_generator import ReportGenerator


def test_calculate_overall_score():
  """Test overall score calculation."""
  generator = ReportGenerator()
  
  code_results = {"overall_score": 0.8}
  behavior_results = {"overall_score": 0.9}
  
  overall = generator._calculate_overall(code_results, behavior_results)
  assert abs(overall - 0.85) < 0.001  # Use approximate comparison
  
  # Test without behavior results
  overall_code_only = generator._calculate_overall(code_results, None)
  assert abs(overall_code_only - 0.8) < 0.001


def test_generate_json_report():
  """Test JSON report generation."""
  generator = ReportGenerator()
  
  code_results = {
    "overall_score": 0.8,
    "metrics": {
      "Code Correctness": {
        "score": 0.9,
        "success": True,
        "threshold": 0.8,
        "reason": "Good implementation"
      }
    }
  }
  
  report = generator._generate_json(code_results, None)
  data = json.loads(report)
  
  assert "timestamp" in data
  assert "overall_score" in data
  assert "code_quality" in data
  assert data["overall_score"] == 0.8


def test_generate_markdown_report():
  """Test markdown report generation."""
  generator = ReportGenerator()
  
  code_results = {
    "overall_score": 0.8,
    "metrics": {
      "Code Correctness": {
        "score": 0.9,
        "success": True,
        "threshold": 0.8,
        "reason": "Good implementation"
      }
    }
  }
  
  report = generator._generate_markdown(
    code_results, None, "wdt", "iflow/qwen3-coder-plus"
  )
  
  assert "# DeepEval Scoring Report" in report
  assert "Code Correctness" in report
  assert "80.0%" in report or "80%" in report


def test_generate_recommendations():
  """Test recommendation generation."""
  generator = ReportGenerator()
  
  # Test with failing metrics
  code_results = {
    "overall_score": 0.6,
    "metrics": {
      "Code Correctness": {
        "score": 0.6,
        "success": False,
        "threshold": 0.8,
        "reason": "Needs improvement"
      }
    }
  }
  
  recommendations = generator._generate_recommendations(code_results, None)
  assert len(recommendations) > 0
  assert any("Code Correctness" in rec for rec in recommendations)
  
  # Test with all passing metrics
  code_results_passing = {
    "overall_score": 0.9,
    "metrics": {
      "Code Correctness": {
        "score": 0.9,
        "success": True,
        "threshold": 0.8,
        "reason": "Great work"
      }
    }
  }
  
  recommendations_passing = generator._generate_recommendations(
    code_results_passing, None
  )
  assert any("passed" in rec.lower() for rec in recommendations_passing)


if __name__ == "__main__":
  # Run tests manually
  test_calculate_overall_score()
  test_generate_json_report()
  test_generate_markdown_report()
  test_generate_recommendations()
  print("✅ All report generator tests passed!")
