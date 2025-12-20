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

"""Scoring system for agent evaluation chain.

This module provides scoring classes for:
- apply_agent (Level 1)
- apply_improve_agent (Level 2)
- meta_improve_agent (Level 3)
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ApplyAgentScore(BaseModel):
  """Score for apply_agent performance.
  
  Measures how well the apply_agent implemented a feature.
  """
  
  # Efficiency Metrics
  build_attempts: int = Field(..., description="Actual number of build attempts")
  build_attempts_target: int = Field(5, description="Target build attempts")
  build_attempts_score: float = Field(0.0, description="Score for build attempts (0-10)")
  
  time_minutes: float = Field(..., description="Actual time in minutes")
  time_target: float = Field(5.0, description="Target time in minutes")
  time_score: float = Field(0.0, description="Score for time (0-10)")
  
  # Quality Metrics
  error_types_count: int = Field(..., description="Number of unique error types")
  error_types_target: int = Field(2, description="Target error types")
  error_types_score: float = Field(0.0, description="Score for error types (0-10)")
  
  # Success Metrics
  final_success: bool = Field(..., description="Did it complete successfully?")
  tests_passed: int = Field(0, description="Number of tests passed")
  tests_total: int = Field(0, description="Total number of tests")
  success_score: float = Field(0.0, description="Score for success (0-10)")
  
  # Overall Score
  overall_score: float = Field(0.0, description="Weighted overall score (0-10)")
  grade: str = Field("", description="Letter grade (A-F)")
  
  def calculate_score(self) -> float:
    """Calculate weighted overall score.
    
    Returns:
      Overall score (0-10)
    """
    # Build attempts: 10 points if at target, -2 points per extra attempt
    self.build_attempts_score = max(
      0, 
      10 - (self.build_attempts - self.build_attempts_target) * 2
    )
    
    # Time: 10 points if at target, -1 point per extra minute
    self.time_score = max(
      0,
      10 - (self.time_minutes - self.time_target) * 1
    )
    
    # Error types: 10 points if at target, -3 points per extra type
    self.error_types_score = max(
      0,
      10 - (self.error_types_count - self.error_types_target) * 3
    )
    
    # Success: 10 if completed, 0 if not
    # Bonus: +1 per test passed (up to 10 total)
    if self.final_success:
      test_bonus = min(5, (self.tests_passed / max(1, self.tests_total)) * 5)
      self.success_score = 5 + test_bonus
    else:
      self.success_score = 0
    
    # Weighted average
    self.overall_score = (
      self.build_attempts_score * 0.3 +
      self.time_score * 0.2 +
      self.error_types_score * 0.2 +
      self.success_score * 0.3
    )
    
    # Assign grade
    self.grade = self._score_to_grade(self.overall_score)
    
    return self.overall_score
  
  def _score_to_grade(self, score: float) -> str:
    """Convert score to letter grade."""
    if score >= 9.0:
      return "A"
    elif score >= 8.0:
      return "B"
    elif score >= 7.0:
      return "C"
    elif score >= 6.0:
      return "D"
    else:
      return "F"
  
  def get_improvement_suggestions(self) -> List[str]:
    """Get specific improvement suggestions based on scores."""
    suggestions = []
    
    if self.build_attempts_score < 7:
      suggestions.append(
        f"Reduce build attempts from {self.build_attempts} to "
        f"<{self.build_attempts_target} (current score: "
        f"{self.build_attempts_score:.1f}/10)"
      )
    
    if self.time_score < 7:
      suggestions.append(
        f"Reduce time from {self.time_minutes:.1f} to "
        f"<{self.time_target} minutes (current score: {self.time_score:.1f}/10)"
      )
    
    if self.error_types_score < 7:
      suggestions.append(
        f"Reduce error types from {self.error_types_count} to "
        f"<{self.error_types_target} (current score: "
        f"{self.error_types_score:.1f}/10)"
      )
    
    if self.success_score < 7:
      if not self.final_success:
        suggestions.append("Complete the task successfully")
      else:
        suggestions.append(
          f"Improve test pass rate from {self.tests_passed}/"
          f"{self.tests_total} (current score: {self.success_score:.1f}/10)"
        )
    
    return suggestions


class ApplyImproveAgentScore(BaseModel):
  """Score for apply_improve_agent performance.
  
  Measures how well the apply_improve_agent analyzed and improved apply_agent.
  """
  
  # Analysis Depth
  dimensions_covered: int = Field(..., description="Dimensions analyzed")
  dimensions_expected: int = Field(7, description="Expected dimensions")
  analysis_depth_score: float = Field(0.0, description="Score for depth (0-10)")
  
  # Recommendation Quality
  recommendations_count: int = Field(..., description="Total recommendations")
  recommendations_specific: int = Field(..., description="Recommendations with code blocks")
  recommendations_actionable: int = Field(..., description="Actionable recommendations")
  recommendation_quality_score: float = Field(0.0, description="Score for quality (0-10)")
  
  # Evidence Quality
  evidence_provided: bool = Field(..., description="Evidence provided?")
  evidence_specific: bool = Field(..., description="Evidence specific (quotes)?")
  evidence_quality_score: float = Field(0.0, description="Score for evidence (0-10)")
  
  # Coverage
  error_patterns_identified: int = Field(..., description="Error patterns found")
  best_practices_analyzed: bool = Field(..., description="Best practices analyzed?")
  coverage_score: float = Field(0.0, description="Score for coverage (0-10)")
  
  # Actionability
  exact_text_provided: bool = Field(..., description="Exact text provided?")
  location_specified: bool = Field(..., description="Location specified?")
  impact_quantified: bool = Field(..., description="Impact quantified?")
  actionability_score: float = Field(0.0, description="Score for actionability (0-10)")
  
  # Overall Score
  overall_score: float = Field(0.0, description="Weighted overall score (0-10)")
  grade: str = Field("", description="Letter grade (A-F)")
  
  def calculate_score(self) -> float:
    """Calculate weighted overall score.
    
    Returns:
      Overall score (0-10)
    """
    # Analysis depth: 0-10 based on coverage
    self.analysis_depth_score = (
      self.dimensions_covered / self.dimensions_expected
    ) * 10
    
    # Recommendation quality: 0-10 based on specificity and actionability
    if self.recommendations_count > 0:
      specificity_rate = (
        self.recommendations_specific / self.recommendations_count
      )
      actionability_rate = (
        self.recommendations_actionable / self.recommendations_count
      )
      self.recommendation_quality_score = (
        (specificity_rate + actionability_rate) / 2 * 10
      )
    else:
      self.recommendation_quality_score = 0
    
    # Evidence quality: 0-10 based on presence and specificity
    self.evidence_quality_score = (
      (5 if self.evidence_provided else 0) +
      (5 if self.evidence_specific else 0)
    )
    
    # Coverage: 0-10 based on patterns and best practices
    pattern_score = min(10, self.error_patterns_identified * 2)
    bp_score = 10 if self.best_practices_analyzed else 0
    self.coverage_score = pattern_score * 0.6 + bp_score * 0.4
    
    # Actionability: 0-10 based on completeness
    actionability_checks = [
      self.exact_text_provided,
      self.location_specified,
      self.impact_quantified
    ]
    self.actionability_score = (
      sum(actionability_checks) / len(actionability_checks) * 10
    )
    
    # Weighted average
    self.overall_score = (
      self.analysis_depth_score * 0.25 +
      self.recommendation_quality_score * 0.25 +
      self.evidence_quality_score * 0.15 +
      self.coverage_score * 0.15 +
      self.actionability_score * 0.20
    )
    
    # Assign grade
    self.grade = self._score_to_grade(self.overall_score)
    
    return self.overall_score
  
  def _score_to_grade(self, score: float) -> str:
    """Convert score to letter grade."""
    if score >= 9.0:
      return "A"
    elif score >= 8.0:
      return "B"
    elif score >= 7.0:
      return "C"
    elif score >= 6.0:
      return "D"
    else:
      return "F"
  
  def get_improvement_suggestions(self) -> List[str]:
    """Get specific improvement suggestions based on scores."""
    suggestions = []
    
    if self.analysis_depth_score < 7:
      suggestions.append(
        f"Cover all {self.dimensions_expected} dimensions "
        f"(currently {self.dimensions_covered}/{self.dimensions_expected})"
      )
    
    if self.recommendation_quality_score < 7:
      suggestions.append(
        f"Provide code blocks for all recommendations "
        f"(currently {self.recommendations_specific}/"
        f"{self.recommendations_count})"
      )
    
    if self.evidence_quality_score < 7:
      if not self.evidence_provided:
        suggestions.append("Provide evidence for all claims")
      elif not self.evidence_specific:
        suggestions.append("Provide specific evidence (quotes, not summaries)")
    
    if self.coverage_score < 7:
      suggestions.append(
        f"Identify more error patterns (currently "
        f"{self.error_patterns_identified})"
      )
      if not self.best_practices_analyzed:
        suggestions.append("Analyze best practices compliance")
    
    if self.actionability_score < 7:
      if not self.exact_text_provided:
        suggestions.append("Provide exact text to add (in code blocks)")
      if not self.location_specified:
        suggestions.append("Specify where to add recommendations")
      if not self.impact_quantified:
        suggestions.append("Quantify expected impact")
    
    return suggestions


class MetaImproveAgentScore(BaseModel):
  """Score for meta_improve_agent performance.
  
  Measures how well the meta_improve_agent analyzed and improved
  apply_improve_agent by comparing to reference analyses.
  """
  
  # Reference Comparison
  reference_file: str = Field(..., description="Reference file used")
  
  # Coverage Comparison
  dimensions_covered: int = Field(..., description="Dimensions covered by agent")
  dimensions_in_reference: int = Field(..., description="Dimensions in reference")
  coverage_score: float = Field(0.0, description="Score for coverage (0-10)")
  
  # Specificity Comparison
  recommendations_with_code: int = Field(..., description="Agent's code blocks")
  recommendations_with_code_in_reference: int = Field(..., description="Reference's code blocks")
  specificity_score: float = Field(0.0, description="Score for specificity (0-10)")
  
  # Evidence Comparison
  evidence_quotes_count: int = Field(..., description="Agent's evidence quotes")
  evidence_quotes_in_reference: int = Field(..., description="Reference's evidence quotes")
  evidence_score: float = Field(0.0, description="Score for evidence (0-10)")
  
  # Structure Comparison
  follows_reference_structure: bool = Field(..., description="Same structure?")
  structure_score: float = Field(0.0, description="Score for structure (0-10)")
  
  # Impact Quantification
  impact_quantified_count: int = Field(..., description="Agent's quantified impacts")
  impact_quantified_in_reference: int = Field(..., description="Reference's quantified impacts")
  impact_score: float = Field(0.0, description="Score for impact (0-10)")
  
  # Overall Score
  overall_score: float = Field(0.0, description="Weighted overall score (0-10)")
  grade: str = Field("", description="Letter grade (A-F)")
  
  def calculate_score(self) -> float:
    """Calculate weighted overall score.
    
    Returns:
      Overall score (0-10)
    """
    # Coverage: How many dimensions vs reference
    if self.dimensions_in_reference > 0:
      self.coverage_score = min(
        10,
        (self.dimensions_covered / self.dimensions_in_reference) * 10
      )
    else:
      self.coverage_score = 10
    
    # Specificity: How many code blocks vs reference
    if self.recommendations_with_code_in_reference > 0:
      self.specificity_score = min(
        10,
        (self.recommendations_with_code / 
         self.recommendations_with_code_in_reference) * 10
      )
    else:
      self.specificity_score = 10
    
    # Evidence: How many quotes vs reference
    if self.evidence_quotes_in_reference > 0:
      self.evidence_score = min(
        10,
        (self.evidence_quotes_count / self.evidence_quotes_in_reference) * 10
      )
    else:
      self.evidence_score = 10
    
    # Structure: Binary score
    self.structure_score = 10 if self.follows_reference_structure else 5
    
    # Impact: How many quantified vs reference
    if self.impact_quantified_in_reference > 0:
      self.impact_score = min(
        10,
        (self.impact_quantified_count / 
         self.impact_quantified_in_reference) * 10
      )
    else:
      self.impact_score = 10
    
    # Weighted average
    self.overall_score = (
      self.coverage_score * 0.25 +
      self.specificity_score * 0.25 +
      self.evidence_score * 0.20 +
      self.structure_score * 0.10 +
      self.impact_score * 0.20
    )
    
    # Assign grade
    self.grade = self._score_to_grade(self.overall_score)
    
    return self.overall_score
  
  def _score_to_grade(self, score: float) -> str:
    """Convert score to letter grade."""
    if score >= 9.0:
      return "A"
    elif score >= 8.0:
      return "B"
    elif score >= 7.0:
      return "C"
    elif score >= 6.0:
      return "D"
    else:
      return "F"
  
  def get_improvement_suggestions(self) -> List[str]:
    """Get specific improvement suggestions based on scores."""
    suggestions = []
    
    if self.coverage_score < 9:
      suggestions.append(
        f"Cover all dimensions from reference "
        f"(currently {self.dimensions_covered}/"
        f"{self.dimensions_in_reference})"
      )
    
    if self.specificity_score < 9:
      suggestions.append(
        f"Provide code blocks for all recommendations like reference "
        f"(currently {self.recommendations_with_code}/"
        f"{self.recommendations_with_code_in_reference})"
      )
    
    if self.evidence_score < 9:
      suggestions.append(
        f"Provide more evidence quotes like reference "
        f"(currently {self.evidence_quotes_count}/"
        f"{self.evidence_quotes_in_reference})"
      )
    
    if self.structure_score < 9:
      suggestions.append("Follow reference structure more closely")
    
    if self.impact_score < 9:
      suggestions.append(
        f"Quantify impact for all recommendations like reference "
        f"(currently {self.impact_quantified_count}/"
        f"{self.impact_quantified_in_reference})"
      )
    
    return suggestions


# Example usage
if __name__ == "__main__":
  # Example 1: Score apply_agent
  apply_score = ApplyAgentScore(
    build_attempts=15,
    time_minutes=8.98,
    error_types_count=3,
    final_success=True,
    tests_passed=0,
    tests_total=5
  )
  apply_score.calculate_score()
  print(f"Apply Agent Score: {apply_score.overall_score:.1f}/10 "
        f"(Grade: {apply_score.grade})")
  print("Improvements needed:")
  for suggestion in apply_score.get_improvement_suggestions():
    print(f"  - {suggestion}")
  
  # Example 2: Score apply_improve_agent
  improve_score = ApplyImproveAgentScore(
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
  improve_score.calculate_score()
  print(f"\nApply Improve Agent Score: {improve_score.overall_score:.1f}/10 "
        f"(Grade: {improve_score.grade})")
  print("Improvements needed:")
  for suggestion in improve_score.get_improvement_suggestions():
    print(f"  - {suggestion}")
  
  # Example 3: Score meta_improve_agent
  meta_score = MetaImproveAgentScore(
    reference_file="reference_analysis_20251220.md",
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
  meta_score.calculate_score()
  print(f"\nMeta Improve Agent Score: {meta_score.overall_score:.1f}/10 "
        f"(Grade: {meta_score.grade})")
  print("Improvements needed:")
  for suggestion in meta_score.get_improvement_suggestions():
    print(f"  - {suggestion}")
