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

"""Verbose ReAct module that shows thoughts and actions in real-time."""

from __future__ import annotations

import sys

import dspy


class VerboseReAct(dspy.ReAct):
  """ReAct with verbose output showing thoughts and actions."""
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._iteration = 0
  
  def forward(self, **input_args):
    """Override forward to show thoughts in real-time."""
    trajectory = {}
    max_iters = input_args.pop("max_iters", self.max_iters)
    self._iteration = 0
    
    for idx in range(max_iters):
      try:
        pred = self._call_with_potential_trajectory_truncation(
          self.react, trajectory, **input_args
        )
      except ValueError as err:
        print(f"\n⚠️  Agent failed to select valid tool: {err}")
        break
      
      # Display thought and action in real-time
      print(f"\n💭 Iteration {idx + 1}:")
      print(f"   Thought: {pred.next_thought}")
      print(f"   Action: {pred.next_tool_name}")
      if pred.next_tool_args:
        print(f"   Args: {pred.next_tool_args}")
      sys.stdout.flush()
      
      trajectory[f"thought_{idx}"] = pred.next_thought
      trajectory[f"tool_name_{idx}"] = pred.next_tool_name
      trajectory[f"tool_args_{idx}"] = pred.next_tool_args
      
      try:
        observation = self.tools[pred.next_tool_name](**pred.next_tool_args)
        trajectory[f"observation_{idx}"] = observation
        # Show observation preview
        obs_preview = str(observation)[:150]
        if len(str(observation)) > 150:
          obs_preview += "..."
        print(f"   Observation: {obs_preview}")
      except Exception as err:
        error_msg = f"Execution error in {pred.next_tool_name}: {err}"
        trajectory[f"observation_{idx}"] = error_msg
        print(f"   ❌ {error_msg}")
      
      sys.stdout.flush()
      
      if pred.next_tool_name == "finish":
        print(f"\n✅ Agent finished after {idx + 1} iterations")
        break
    
    extract = self._call_with_potential_trajectory_truncation(
      self.extract, trajectory, **input_args
    )
    return dspy.Prediction(trajectory=trajectory, **extract)
