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

"""Test script to verify installation."""

from __future__ import annotations

import sys


def test_imports():
  """Test that all required modules can be imported."""
  print("Testing imports...")
  
  try:
    # Test metrics
    from metrics.code_correctness import CodeCorrectnessMetric
    from metrics.test_coverage import TestCoverageMetric
    from metrics.code_style import CodeStyleMetric
    from metrics.documentation_usage import DocumentationUsageMetric
    print("✅ Metrics imported successfully")
    
    # Test evaluators
    from evaluators.code_evaluator import CodeEvaluator
    from evaluators.behavior_evaluator import BehaviorEvaluator
    print("✅ Evaluators imported successfully")
    
    # Test parsers
    from parsers.dml_parser import DMLParser
    from parsers.test_parser import TestParser
    from parsers.spec_parser import SpecParser
    from parsers.session_parser import SessionParser
    print("✅ Parsers imported successfully")
    
    # Test report generator
    from report_generator import ReportGenerator
    print("✅ Report generator imported successfully")
    
    return True
    
  except ImportError as e:
    print(f"❌ Import error: {e}")
    return False


def test_dependencies():
  """Test that all required dependencies are installed."""
  print("\nTesting dependencies...")
  
  missing = []
  
  try:
    import deepeval
    print("✅ deepeval installed")
  except ImportError:
    missing.append("deepeval")
    print("❌ deepeval not installed")
  
  try:
    import litellm
    print("✅ litellm installed")
  except ImportError:
    missing.append("litellm")
    print("❌ litellm not installed")
  
  try:
    import yaml
    print("✅ pyyaml installed")
  except ImportError:
    missing.append("pyyaml")
    print("❌ pyyaml not installed")
  
  try:
    import pydantic
    print("✅ pydantic installed")
  except ImportError:
    missing.append("pydantic")
    print("❌ pydantic not installed")
  
  if missing:
    print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
    print("Run: pip install -r requirements.txt")
    return False
  
  return True


def test_package_info():
  """Test package metadata."""
  print("\nTesting package info...")
  
  try:
    import importlib.metadata
    try:
      version = importlib.metadata.version("deepeval-scoring")
      print(f"✅ Package installed: deepeval-scoring v{version}")
      return True
    except importlib.metadata.PackageNotFoundError:
      print("⚠️  Package not installed (running from source)")
      print("   To install: pip install -e .")
      return True  # Not an error, just informational
  except ImportError:
    print("⚠️  Cannot check package info (Python < 3.8)")
    return True


def main():
  """Run all tests."""
  print("="*60)
  print("DeepEval Scoring System - Installation Test")
  print("="*60)
  print()
  
  deps_ok = test_dependencies()
  imports_ok = test_imports()
  pkg_ok = test_package_info()
  
  print()
  print("="*60)
  if deps_ok and imports_ok:
    print("✅ All tests passed! Installation is complete.")
    print()
    print("Next steps:")
    print("1. Set your API key: export IFLOW_API_KEY='your-key'")
    print("2. Run scoring: python score.py --workdir /path --device wdt")
    print()
    print("Optional: Install as package with 'pip install -e .'")
    sys.exit(0)
  else:
    print("❌ Some tests failed. Please fix the issues above.")
    sys.exit(1)


if __name__ == "__main__":
  main()
