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

"""Compilation success metric."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


class CompilationMetric(BaseMetric):
    """Metric that checks if the DML code compiles successfully.
    
    Runs `make <device>` and checks if compilation succeeds.
    Score: 100 if compiles, 0 if fails.
    """
    
    def __init__(
        self,
        workdir: str,
        device_name: str,
        threshold: float = 1.0,
        timeout: int = 300
    ):
        self.workdir = Path(workdir)
        self.device_name = device_name
        self.threshold = threshold
        self.timeout = timeout
        self.compilation_output = ""
        self.compilation_success = False
    
    def measure(self, test_case: LLMTestCase) -> float:
        """Run compilation and return score (0.0 or 1.0)."""
        
        # Navigate to simics-project directory
        simics_project_dir = self.workdir / "simics-project"
        
        if not simics_project_dir.exists():
            self.reason = f"Simics project directory not found: {simics_project_dir}"
            self.compilation_success = False
            self.score = 0.0
            self.success = False
            return self.score
        
        try:
            # Run make <device>
            cmd = ["make", self.device_name]
            result = subprocess.run(
                cmd,
                cwd=simics_project_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            self.compilation_output = result.stdout + result.stderr
            self.compilation_success = (result.returncode == 0)
            
            if self.compilation_success:
                self.score = 1.0
                self.reason = f"✅ Compilation successful for device '{self.device_name}'"
                self.success = True
            else:
                self.score = 0.0
                # Extract relevant error messages
                error_lines = [line for line in self.compilation_output.split('\n') 
                              if 'error:' in line.lower() or 'failed' in line.lower()]
                error_summary = '\n'.join(error_lines[:5])  # First 5 errors
                self.reason = f"❌ Compilation failed for device '{self.device_name}'\n{error_summary}"
                self.success = False
            
        except subprocess.TimeoutExpired:
            self.score = 0.0
            self.reason = f"⏱️ Compilation timeout after {self.timeout}s"
            self.compilation_success = False
            self.success = False
        except Exception as e:
            self.score = 0.0
            self.reason = f"❌ Compilation error: {str(e)}"
            self.compilation_success = False
            self.success = False
        
        return self.score
    
    async def a_measure(self, test_case: LLMTestCase) -> float:
        """Async version (calls sync version)."""
        return self.measure(test_case)
    
    def is_successful(self) -> bool:
        """Return whether the metric passed the threshold."""
        return self.score >= self.threshold
    
    @property
    def __name__(self):
        return "Compilation Success"
