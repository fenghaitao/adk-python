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

"""Tests for MLflow integration."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tracking.mlflow_tracker import MLflowTracker
from tracking.experiment_manager import ExperimentManager
from tracking.utils import is_mlflow_available, sanitize_experiment_name


class TestMLflowIntegration(unittest.TestCase):
  """Test MLflow integration functionality."""
  
  def setUp(self):
    """Set up test environment."""
    self.temp_dir = tempfile.mkdtemp()
    self.tracking_uri = f"file://{self.temp_dir}/mlruns"
  
  def test_mlflow_availability(self):
    """Test MLflow availability check."""
    # This should return True if MLflow is properly installed
    available = is_mlflow_available()
    self.assertIsInstance(available, bool)
  
  def test_sanitize_experiment_name(self):
    """Test experiment name sanitization."""
    test_cases = [
      ("wdt-device", "wdt-device"),
      ("device/with/slashes", "device_with_slashes"),
      ("device\\with\\backslashes", "device_with_backslashes"),
      ("device@#$%special", "devicespecial"),
      ("", "default_experiment"),
    ]
    
    for input_name, expected in test_cases:
      result = sanitize_experiment_name(input_name)
      self.assertEqual(result, expected)
  
  @unittest.skipUnless(is_mlflow_available(), "MLflow not available")
  def test_mlflow_tracker_initialization(self):
    """Test MLflow tracker initialization."""
    tracker = MLflowTracker(tracking_uri=self.tracking_uri)
    self.assertEqual(tracker.get_tracking_uri(), self.tracking_uri)
    self.assertIsNone(tracker.get_run_id())
  
  @unittest.skipUnless(is_mlflow_available(), "MLflow not available")
  def test_experiment_manager_initialization(self):
    """Test experiment manager initialization."""
    manager = ExperimentManager(tracking_uri=self.tracking_uri)
    experiments = manager.list_experiments()
    self.assertIsInstance(experiments, list)


if __name__ == "__main__":
  unittest.main()