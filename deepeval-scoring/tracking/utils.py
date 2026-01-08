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

"""Utility functions for MLflow tracking."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


def get_default_tracking_uri() -> str:
  """Get default MLflow tracking URI.
  
  Returns:
    Default tracking URI based on environment or fallback
  """
  # Check environment variable first
  if uri := os.getenv("MLFLOW_TRACKING_URI"):
    return uri
  
  # Check for local mlruns directory
  local_mlruns = Path.cwd() / "mlruns"
  if local_mlruns.exists():
    return f"file://{local_mlruns.absolute()}"
  
  # Default to temp directory
  return "file:///tmp/mlruns"


def sanitize_experiment_name(name: str) -> str:
  """Sanitize experiment name for MLflow.
  
  Args:
    name: Raw experiment name
  
  Returns:
    Sanitized experiment name
  """
  # Replace invalid characters
  sanitized = name.replace("/", "_").replace("\\", "_")
  sanitized = "".join(c for c in sanitized if c.isalnum() or c in "-_.")
  
  # Ensure it's not empty
  if not sanitized:
    sanitized = "default_experiment"
  
  return sanitized


def format_run_name(
    device_name: str,
    model: str,
    scoring_mode: str,
    timestamp: Optional[str] = None
) -> str:
  """Format a run name.
  
  Args:
    device_name: Device name
    model: Model name
    scoring_mode: Scoring mode
    timestamp: Optional timestamp
  
  Returns:
    Formatted run name
  """
  # Sanitize model name
  model_clean = model.replace("/", "_").replace(":", "_")
  
  parts = [device_name, model_clean, scoring_mode]
  if timestamp:
    parts.insert(0, timestamp)
  
  return "_".join(parts)


def is_mlflow_available() -> bool:
  """Check if MLflow is available and properly configured.
  
  Returns:
    True if MLflow is available, False otherwise
  """
  try:
    import mlflow
    # Try to get the tracking URI to ensure it's working
    mlflow.get_tracking_uri()
    return True
  except ImportError:
    return False
  except Exception:
    # MLflow is installed but may have configuration issues
    return False


def get_run_url(tracking_uri: str, experiment_id: str, run_id: str) -> str:
  """Generate MLflow UI URL for a run.
  
  Args:
    tracking_uri: MLflow tracking URI
    experiment_id: Experiment ID
    run_id: Run ID
  
  Returns:
    URL to view the run in MLflow UI
  """
  if tracking_uri.startswith("http"):
    base_url = tracking_uri.rstrip("/")
    return f"{base_url}/#/experiments/{experiment_id}/runs/{run_id}"
  else:
    # For local file storage, assume MLflow UI is running on localhost:5000
    return f"http://localhost:5000/#/experiments/{experiment_id}/runs/{run_id}"