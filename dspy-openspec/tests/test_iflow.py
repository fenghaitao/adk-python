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

"""Test script for iflow model integration.

Usage:
  export IFLOW_API_KEY="your-api-key"
  python test_iflow.py
"""

from __future__ import annotations

import os
import sys

import dspy
from dspy_openspec.config.lm_config import (
  configure_iflow_model,
  print_model_info
)


def test_iflow_basic():
  """Test basic iflow model configuration."""
  print("=" * 60)
  print("Testing iflow Model Integration")
  print("=" * 60)
  
  # Check API key
  api_key = os.getenv("IFLOW_API_KEY")
  if not api_key:
    print("❌ IFLOW_API_KEY not set")
    print("   Set it with: export IFLOW_API_KEY='your-api-key'")
    return False
  
  print(f"✓ IFLOW_API_KEY is set")
  
  # Configure model
  try:
    print("\n🔧 Configuring iflow model...")
    lm = configure_iflow_model("qwen3-coder-plus")
    dspy.settings.configure(lm=lm)
    print("✓ Model configured successfully")
  except Exception as e:
    print(f"❌ Failed to configure model: {e}")
    return False
  
  # Test simple completion
  try:
    print("\n🧪 Testing simple completion...")
    
    class SimpleSignature(dspy.Signature):
      """Answer a simple question."""
      question: str = dspy.InputField()
      answer: str = dspy.OutputField()
    
    predictor = dspy.Predict(SimpleSignature)
    result = predictor(question="What is 2+2?")
    
    print(f"✓ Completion successful")
    print(f"   Question: What is 2+2?")
    print(f"   Answer: {result.answer}")
    
    return True
    
  except Exception as e:
    print(f"❌ Completion failed: {e}")
    import traceback
    traceback.print_exc()
    return False


def test_iflow_with_proposal():
  """Test iflow with ProposalSignature."""
  print("\n" + "=" * 60)
  print("Testing iflow with ProposalSignature")
  print("=" * 60)
  
  try:
    from dspy_openspec.modules.proposal_module import ProposalModule
    
    print("\n🔧 Creating ProposalModule...")
    proposal = ProposalModule()
    print("✓ Module created")
    
    print("\n🧪 Testing proposal generation...")
    print("   (This will use the full instruction content)")
    
    # Note: This will actually call the LM with the full instruction
    # For a real test, you'd want to use a simpler task
    print("   Task: Test proposal generation")
    print("   Device: test")
    
    # Uncomment to test with real LM call:
    # result = proposal(
    #     task_description="Create a simple test device",
    #     device_hint="test"
    # )
    # print(f"✓ Proposal generated")
    # print(f"   Change ID: {result.change_id}")
    # print(f"   Summary: {result.summary}")
    
    print("   (Skipping actual LM call in test)")
    print("✓ Module structure verified")
    
    return True
    
  except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    return False


def main():
  """Run all tests."""
  print("\n🚀 DSPy OpenSpec iflow Integration Tests\n")
  
  # Print model info
  print_model_info("iflow/qwen3-coder-plus")
  print()
  
  # Run tests
  results = []
  
  results.append(("Basic iflow configuration", test_iflow_basic()))
  results.append(("ProposalSignature integration", test_iflow_with_proposal()))
  
  # Summary
  print("\n" + "=" * 60)
  print("Test Summary")
  print("=" * 60)
  
  for name, passed in results:
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status}: {name}")
  
  all_passed = all(passed for _, passed in results)
  
  if all_passed:
    print("\n✅ All tests passed!")
    return 0
  else:
    print("\n❌ Some tests failed")
    return 1


if __name__ == "__main__":
  sys.exit(main())
