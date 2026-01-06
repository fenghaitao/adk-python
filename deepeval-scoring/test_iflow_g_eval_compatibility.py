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

"""Test G-Eval compatibility with iflow and GitHub Copilot models."""

from __future__ import annotations

import os
from deepeval.metrics import GEval
from deepeval.metrics.g_eval import Rubric
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.models import LiteLLMModel
from deepeval import evaluate


def test_iflow_g_eval_compatibility():
  """Test if G-Eval works with iflow models through LiteLLM."""
  
  print("🔍 Testing G-Eval compatibility with iflow models...")
  
  # Check if IFLOW_API_KEY is set
  if not os.getenv("IFLOW_API_KEY"):
    print("❌ IFLOW_API_KEY not set. Please set it to test iflow compatibility.")
    print("   export IFLOW_API_KEY='your-key'")
    return False
  
  try:
    # Method 1: Use LiteLLMModel directly with iflow configuration
    print("\n📋 Method 1: Using LiteLLMModel with iflow configuration")
    
    iflow_model = LiteLLMModel(
      model="dashscope/qwen3-coder-plus",  # iflow uses dashscope/ prefix in LiteLLM
      api_key=os.getenv("IFLOW_API_KEY"),
      base_url="https://apis.iflow.cn/v1/"
    )
    
    # Create a simple G-Eval metric
    g_eval_metric = GEval(
      name="Instruction Following Test",
      evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
      criteria="Evaluate how well the response follows the given instruction",
      rubric=[
        Rubric(score_range=(8, 10), expected_outcome="Excellent instruction following"),
        Rubric(score_range=(5, 7), expected_outcome="Good instruction following"),
        Rubric(score_range=(0, 4), expected_outcome="Poor instruction following")
      ],
      model=iflow_model,  # Pass the LiteLLMModel instance
      threshold=0.6
    )
    
    # Create test case
    test_case = LLMTestCase(
      input="Write a simple Python function that adds two numbers",
      actual_output="def add_numbers(a, b):\n    return a + b"
    )
    
    # Test evaluation
    print("   Running G-Eval with iflow model...")
    results = evaluate([test_case], [g_eval_metric])
    
    print("✅ Method 1 successful!")
    for result in results.test_results:
      for metric_data in result.metrics_data:
        print(f"   Score: {metric_data.score:.2f}")
        print(f"   Success: {metric_data.success}")
        print(f"   Reason: {metric_data.reason[:100]}...")
    
    return True
    
  except Exception as e:
    print(f"❌ Method 1 failed: {e}")
    
    # Method 2: Try with string model name (may not work directly)
    try:
      print("\n📋 Method 2: Using string model name (fallback)")
      
      # This approach requires DeepEval to handle iflow models natively
      # which it may not support directly
      g_eval_metric_str = GEval(
        name="Instruction Following Test",
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        criteria="Evaluate how well the response follows the given instruction",
        model="iflow/qwen3-coder-plus",  # String model name
        threshold=0.6
      )
      
      test_case = LLMTestCase(
        input="Write a simple Python function that adds two numbers",
        actual_output="def add_numbers(a, b):\n    return a + b"
      )
      
      print("   Running G-Eval with string model name...")
      results = evaluate([test_case], [g_eval_metric_str])
      
      print("✅ Method 2 successful!")
      return True
      
    except Exception as e2:
      print(f"❌ Method 2 failed: {e2}")
      return False


def test_github_copilot_g_eval_compatibility():
  """Test if G-Eval works with GitHub Copilot models through LiteLLM."""
  
  print("🔍 Testing G-Eval compatibility with GitHub Copilot models...")
  
  # GitHub Copilot doesn't require GITHUB_TOKEN for basic usage
  print("   GitHub Copilot models don't require API tokens for testing")
  
  try:
    print("\n📋 Using LiteLLMModel with GitHub Copilot configuration")
    
    copilot_model = LiteLLMModel(
      model="github_copilot/gpt-4o",
      generation_kwargs={
        "extra_headers": {
          "Editor-Version": "vscode/1.85.0",
          "Copilot-Integration-Id": "vscode-chat"
        }
      }
    )
    
    # Create a simple G-Eval metric
    g_eval_metric = GEval(
      name="Code Quality Test",
      evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
      criteria="Evaluate the quality and correctness of the generated code",
      rubric=[
        Rubric(score_range=(8, 10), expected_outcome="Excellent code quality with best practices"),
        Rubric(score_range=(5, 7), expected_outcome="Good code quality with minor issues"),
        Rubric(score_range=(0, 4), expected_outcome="Poor code quality with significant issues")
      ],
      model=copilot_model,  # Pass the LiteLLMModel instance
      threshold=0.6
    )
    
    # Create test case
    test_case = LLMTestCase(
      input="Write a Python function that calculates factorial recursively",
      actual_output="def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)"
    )
    
    # Test evaluation
    print("   Running G-Eval with GitHub Copilot model...")
    results = evaluate([test_case], [g_eval_metric])
    
    print("✅ GitHub Copilot G-Eval test successful!")
    for result in results.test_results:
      for metric_data in result.metrics_data:
        print(f"   Score: {metric_data.score:.2f}")
        print(f"   Success: {metric_data.success}")
        print(f"   Reason: {metric_data.reason[:100]}...")
    
    return True
    
  except Exception as e:
    print(f"❌ GitHub Copilot G-Eval test failed: {e}")
    return False


def test_litellm_iflow_basic():
  """Test basic LiteLLM functionality with iflow."""
  
  print("\n🔍 Testing basic LiteLLM functionality with iflow...")
  
  if not os.getenv("IFLOW_API_KEY"):
    print("❌ IFLOW_API_KEY not set. Skipping basic test.")
    return False
  
  try:
    iflow_model = LiteLLMModel(
      model="dashscope/qwen3-coder-plus",
      api_key=os.getenv("IFLOW_API_KEY"),
      base_url="https://apis.iflow.cn/v1/"
    )
    
    print("   Testing basic generation...")
    response, cost = iflow_model.generate("Say hello in Python code")
    
    print(f"✅ Basic LiteLLM test successful!")
    print(f"   Response: {response[:100]}...")
    print(f"   Cost: ${cost:.6f}")
    
    return True
    
  except Exception as e:
    print(f"❌ Basic LiteLLM test failed: {e}")
    return False


def test_litellm_github_copilot_basic():
  """Test basic LiteLLM functionality with GitHub Copilot."""
  
  print("\n🔍 Testing basic LiteLLM functionality with GitHub Copilot...")
  
  # GitHub Copilot doesn't require GITHUB_TOKEN for basic testing
  print("   GitHub Copilot models don't require API tokens")
  
  try:
    copilot_model = LiteLLMModel(
      model="github_copilot/gpt-4o",
      generation_kwargs={
        "extra_headers": {
          "Editor-Version": "vscode/1.85.0",
          "Copilot-Integration-Id": "vscode-chat"
        }
      }
    )
    
    print("   Testing basic generation...")
    response, cost = copilot_model.generate("Write a simple hello world in Python")
    
    print(f"✅ Basic GitHub Copilot test successful!")
    print(f"   Response: {response[:100]}...")
    print(f"   Cost: ${cost:.6f}")
    
    return True
    
  except Exception as e:
    print(f"❌ Basic GitHub Copilot test failed: {e}")
    return False


if __name__ == "__main__":
  print("🧪 Testing iflow and GitHub Copilot compatibility with G-Eval")
  print("=" * 60)
  
  # Test basic LiteLLM functionality first
  iflow_basic_success = test_litellm_iflow_basic()
  copilot_basic_success = test_litellm_github_copilot_basic()
  
  results = []
  
  if iflow_basic_success:
    # Test G-Eval compatibility with iflow
    iflow_g_eval_success = test_iflow_g_eval_compatibility()
    results.append(("iflow", iflow_g_eval_success))
  else:
    results.append(("iflow", False))
  
  if copilot_basic_success:
    # Test G-Eval compatibility with GitHub Copilot
    copilot_g_eval_success = test_github_copilot_g_eval_compatibility()
    results.append(("GitHub Copilot", copilot_g_eval_success))
  else:
    results.append(("GitHub Copilot", False))
  
  # Summary
  print("\n" + "=" * 60)
  print("📊 COMPATIBILITY SUMMARY")
  print("=" * 60)
  
  for model_type, success in results:
    status = "✅ Compatible" if success else "❌ Issues found"
    print(f"{model_type:15} | {status}")
  
  print("\n💡 RECOMMENDATIONS:")
  if any(success for _, success in results):
    print("✅ G-Eval works with supported models!")
    print("   Use LiteLLMModel with proper configuration for best results")
  else:
    print("⚠️  Consider using GPT-4 or other supported models for G-Eval")
    print("   Check API keys and network connectivity")
  
  print("\n🔧 SETUP REQUIREMENTS:")
  print("   iflow: export IFLOW_API_KEY='your-key'")
  print("   GitHub Copilot: No API key required (uses built-in authentication)")
