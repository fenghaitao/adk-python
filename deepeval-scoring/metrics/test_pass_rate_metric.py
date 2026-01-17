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

"""Test pass rate metric."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


class TestPassRateMetric(BaseMetric):
    """Metric that measures test pass rate.
    
    Runs `make test` in the device module directory and calculates:
    - Score = (passed_tests / total_tests) * 100
    - Requires at least min_passing_tests to pass
    
    Example output parsing:
    BEGIN s-basic-timer-operation
    RESULT s-basic-timer-operation *** failed (exit-status 2) ***
    END s-basic-timer-operation
    BEGIN s-clock-divider
    RESULT s-clock-divider --- passed ---
    END s-clock-divider
    """
    
    def __init__(
        self,
        workdir: str,
        device_name: str,
        threshold: float = 0.5,
        min_passing_tests: int = 2,
        timeout: int = 600
    ):
        self.workdir = Path(workdir)
        self.device_name = device_name
        self.threshold = threshold
        self.min_passing_tests = min_passing_tests
        self.timeout = timeout
        self.test_output = ""
        self.test_results: List[Tuple[str, bool]] = []
        self.passed_count = 0
        self.total_count = 0
    
    def measure(self, test_case: LLMTestCase) -> float:
        """Run tests and return pass rate score."""
        
        # Navigate to device module directory
        module_dir = (
            self.workdir / 
            "simics-project" / 
            "modules" / 
            self.device_name
        )
        
        if not module_dir.exists():
            self.reason = f"Device module directory not found: {module_dir}"
            self.score = 0.0
            self.success = False
            return self.score
        
        try:
            # Run make test
            cmd = ["make", "test"]
            result = subprocess.run(
                cmd,
                cwd=module_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            self.test_output = result.stdout + result.stderr
            
            # Parse test results
            self._parse_test_results()
            
            # Calculate score
            if self.total_count == 0:
                self.score = 0.0
                self.reason = "❌ No tests found or test execution failed"
                self.success = False
            elif self.passed_count < self.min_passing_tests:
                self.score = 0.0
                self.reason = (
                    f"❌ Only {self.passed_count}/{self.total_count} tests passed "
                    f"(minimum {self.min_passing_tests} required)"
                )
                self.success = False
            else:
                self.score = self.passed_count / self.total_count
                pass_rate_percent = self.score * 100
                self.reason = (
                    f"✅ Test pass rate: {self.passed_count}/{self.total_count} "
                    f"({pass_rate_percent:.1f}%)\n"
                    f"Passed tests: {self._get_passed_test_names()}\n"
                    f"Failed tests: {self._get_failed_test_names()}"
                )
                self.success = self.score >= self.threshold
            
        except subprocess.TimeoutExpired:
            self.score = 0.0
            self.reason = f"⏱️ Test execution timeout after {self.timeout}s"
            self.success = False
        except Exception as e:
            self.score = 0.0
            self.reason = f"❌ Test execution error: {str(e)}"
            self.success = False
        
        return self.score
    
    def _parse_test_results(self):
        """Parse test output to extract pass/fail results.
        
        Expected format:
        BEGIN <test-name>
        RESULT <test-name> --- passed ---
        END <test-name>
        
        or:
        BEGIN <test-name>
        RESULT <test-name> *** failed (exit-status N) ***
        END <test-name>
        """
        self.test_results = []
        
        # Pattern to match RESULT lines
        # Example: "RESULT s-clock-divider --- passed ---"
        # Example: "RESULT s-basic-timer *** failed (exit-status 2) ***"
        result_pattern = re.compile(
            r'RESULT\s+(\S+)\s+(?:---\s*passed\s*---|' +
            r'\*\*\*\s*failed(?:\s+\(exit-status\s+\d+\))?\s*\*\*\*)'
        )
        
        for line in self.test_output.split('\n'):
            match = result_pattern.search(line)
            if match:
                test_name = match.group(1)
                passed = 'passed' in line.lower()
                self.test_results.append((test_name, passed))
        
        self.total_count = len(self.test_results)
        self.passed_count = sum(1 for _, passed in self.test_results if passed)
    
    def _get_passed_test_names(self) -> str:
        """Get comma-separated list of passed test names."""
        passed = [name for name, passed in self.test_results if passed]
        return ', '.join(passed) if passed else 'none'
    
    def _get_failed_test_names(self) -> str:
        """Get comma-separated list of failed test names."""
        failed = [name for name, passed in self.test_results if not passed]
        return ', '.join(failed) if failed else 'none'
    
    def get_test_summary(self) -> Dict:
        """Get detailed test summary."""
        return {
            "total_tests": self.total_count,
            "passed_tests": self.passed_count,
            "failed_tests": self.total_count - self.passed_count,
            "pass_rate": self.score,
            "test_results": {
                name: "passed" if passed else "failed"
                for name, passed in self.test_results
            }
        }
    
    async def a_measure(self, test_case: LLMTestCase) -> float:
        """Async version (calls sync version)."""
        return self.measure(test_case)
    
    def is_successful(self) -> bool:
        """Return whether the metric passed the threshold."""
        return self.score >= self.threshold
    
    @property
    def __name__(self):
        return "Test Pass Rate"
