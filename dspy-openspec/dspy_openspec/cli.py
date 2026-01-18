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

"""CLI for DSPy-based OpenSpec implementation.

Provides commands for proposal, apply, and archive operations using DSPy modules.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import dspy

from dspy_openspec.modules.proposal_module import ProposalModule
from dspy_openspec.modules.apply_module import ApplyModule
from dspy_openspec.modules.archive_module import ArchiveModule
from dspy_openspec.config.lm_config import (
  configure_model_from_string,
  print_model_info
)
from dspy_openspec.session_logger import SessionLogger


def configure_dspy(model: str = "iflow/qwen3-coder-plus", verbose: bool = False):
  """Configure DSPy with the specified model.
  
  Args:
    model: Model identifier (e.g., "openai/gpt-4", "iflow/qwen3-coder-plus")
    verbose: Enable verbose logging of LLM interactions
  """
  print_model_info(model)
  lm = configure_model_from_string(model)
  
  # Configure DSPy settings with trace enabled for verbose mode
  if verbose:
    dspy.settings.configure(lm=lm, trace=[])
  else:
    dspy.settings.configure(lm=lm)


def proposal_command(args):
  """Handle proposal command."""
  configure_dspy(args.model, args.verbose)
  
  # Initialize session logger
  session = SessionLogger()
  session.set_metadata(
    command="proposal",
    model=args.model,
    device_hint=args.device or ""
  )
  
  # Read proposal text from file if it's a path
  task_description = args.proposal
  if Path(args.proposal).exists():
    task_description = Path(args.proposal).read_text()
  
  # Log user input
  session.log_user_input(task_description, device=args.device)
  
  # Create proposal module
  proposal_agent = ProposalModule()
  
  # Generate proposal with interactive display
  print(f"🧩 Generating proposal with {args.model}...")
  print(f"{'='*60}")
  
  # Enable trace to capture ReAct steps
  dspy.settings.configure(lm=dspy.settings.lm, trace=[])
  
  result = proposal_agent(
    task_description=task_description,
    device_hint=args.device or ""
  )
  
  # Display ReAct trace interactively
  if dspy.settings.trace:
    print(f"\n🔄 ReAct Reasoning Trace:")
    print(f"{'='*60}")
    for i, step in enumerate(dspy.settings.trace, 1):
      print(f"\n📍 Step {i}:")
      print(f"  Type: {type(step).__name__}")
      
      # Print all attributes of the step for debugging
      if hasattr(step, '__dict__'):
        for key, value in step.__dict__.items():
          if not key.startswith('_'):
            value_str = str(value)
            if len(value_str) > 200:
              value_str = value_str[:200] + '...'
            print(f"  {key}: {value_str}")
      else:
        print(f"  {step}")
  else:
    print(f"\n⚠️  No trace data captured")
    print(f"  This might indicate the agent completed without tool calls")
  
  # Capture LLM history
  session.capture_dspy_history("proposal_agent")
  
  # Log agent response
  session.log_agent_response(
    "proposal_agent",
    f"Change ID: {result.change_id}\nSummary: {result.summary}",
    change_id=result.change_id,
    summary=result.summary
  )
  
  # Display results
  print(f"\n{'='*60}")
  print(f"✅ Proposal generated:")
  print(f"  Change ID: {result.change_id}")
  print(f"  Summary: {result.summary}")
  
  # Save session logs
  log_paths = session.save()
  print(f"\n📝 Session logs saved:")
  for format_type, path in log_paths.items():
    print(f"  {format_type}: {path}")
  
  # Print LLM history if verbose
  if args.verbose:
    print("\n📋 LLM Interaction History:")
    lm = dspy.settings.lm
    if hasattr(lm, 'history') and lm.history:
      for i, entry in enumerate(lm.history, 1):
        print(f"\n{'='*60}")
        print(f"Call {i}")
        print(f"{'='*60}")
        if 'messages' in entry:
          for msg in entry['messages']:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            print(f"\n[{role.upper()}]")
            print(content[:500] + ('...' if len(content) > 500 else ''))
        if 'response' in entry:
          print(f"\n[RESPONSE]")
          resp = entry['response']
          if hasattr(resp, 'choices') and resp.choices:
            content = resp.choices[0].message.content
            print(content[:500] + ('...' if len(content) > 500 else ''))
  
  return 0


def apply_command(args):
  """Handle apply command."""
  configure_dspy(args.model, args.verbose)
  
  # Initialize session logger
  session = SessionLogger()
  session.set_metadata(
    command="apply",
    model=args.model,
    change_id=args.id
  )
  
  # Log user input
  session.log_user_input(f"Apply change: {args.id}", change_id=args.id)
  
  # Create apply module
  apply_agent = ApplyModule()
  
  # Apply change with interactive display
  print(f"🔧 Applying change {args.id} with {args.model}...")
  print(f"{'='*60}")
  
  # Enable trace to capture ReAct steps
  dspy.settings.configure(lm=dspy.settings.lm, trace=[])
  
  result = apply_agent(change_id=args.id)
  
  # Display ReAct trace interactively
  if dspy.settings.trace:
    print(f"\n🔄 ReAct Reasoning Trace:")
    print(f"{'='*60}")
    for i, step in enumerate(dspy.settings.trace, 1):
      print(f"\n📍 Step {i}:")
      print(f"  Type: {type(step).__name__}")
      
      # Print all attributes of the step for debugging
      if hasattr(step, '__dict__'):
        for key, value in step.__dict__.items():
          if not key.startswith('_'):
            value_str = str(value)
            if len(value_str) > 200:
              value_str = value_str[:200] + '...'
            print(f"  {key}: {value_str}")
      else:
        print(f"  {step}")
  else:
    print(f"\n⚠️  No trace data captured")
    print(f"  This might indicate the agent completed without tool calls")
  
  # Capture LLM history
  session.capture_dspy_history("apply_agent")
  
  # Log agent response
  session.log_agent_response(
    "apply_agent",
    f"Status: {result.implementation_status}\nFiles: {result.files_modified}",
    implementation_status=result.implementation_status,
    files_modified=result.files_modified,
    validation_result=result.validation_result
  )
  
  # Display results
  print(f"\n{'='*60}")
  print(f"✅ Apply completed:")
  print(f"  Status: {result.implementation_status}")
  print(f"  Files modified: {result.files_modified}")
  print(f"  Validation: {result.validation_result}")
  
  # Save session logs
  log_paths = session.save()
  print(f"\n📝 Session logs saved:")
  for format_type, path in log_paths.items():
    print(f"  {format_type}: {path}")
  
  # Print LLM history if verbose
  if args.verbose:
    print("\n📋 LLM Interaction History:")
    lm = dspy.settings.lm
    if hasattr(lm, 'history') and lm.history:
      for i, entry in enumerate(lm.history, 1):
        print(f"\n{'='*60}")
        print(f"Call {i}")
        print(f"{'='*60}")
        if 'messages' in entry:
          for msg in entry['messages']:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            print(f"\n[{role.upper()}]")
            print(content[:500] + ('...' if len(content) > 500 else ''))
        if 'response' in entry:
          print(f"\n[RESPONSE]")
          resp = entry['response']
          if hasattr(resp, 'choices') and resp.choices:
            content = resp.choices[0].message.content
            print(content[:500] + ('...' if len(content) > 500 else ''))
  
  return 0 if result.implementation_status == "success" else 1


def archive_command(args):
  """Handle archive command."""
  configure_dspy(args.model, args.verbose)
  
  # Create archive module
  archive_agent = ArchiveModule()
  
  # Archive change
  print(f"📦 Archiving change {args.id} with {args.model}...")
  result = archive_agent(
    change_id=args.id,
    skip_specs=args.skip_specs
  )
  
  # Display results
  print(f"\n✅ Archive completed:")
  print(f"  Status: {result.archive_status}")
  print(f"  Path: {result.archive_path}")
  
  return 0 if result.archive_status == "success" else 1


def main():
  """Main CLI entry point."""
  parser = argparse.ArgumentParser(
    description="DSPy-based OpenSpec CLI"
  )
  parser.add_argument(
    "--model",
    default="iflow/qwen3-coder-plus",
    help="Model to use (default: iflow/qwen3-coder-plus)"
  )
  parser.add_argument(
    "--verbose",
    "-v",
    action="store_true",
    help="Enable verbose logging of LLM interactions"
  )
  
  subparsers = parser.add_subparsers(dest="command", help="Command to run")
  
  # Proposal command
  proposal_parser = subparsers.add_parser(
    "proposal",
    help="Generate OpenSpec proposal"
  )
  proposal_parser.add_argument(
    "proposal",
    help="Proposal text or path to proposal file"
  )
  proposal_parser.add_argument(
    "--device",
    help="Device name hint"
  )
  
  # Apply command
  apply_parser = subparsers.add_parser(
    "apply",
    help="Apply OpenSpec change"
  )
  apply_parser.add_argument(
    "--id",
    required=True,
    help="Change ID to apply"
  )
  
  # Archive command
  archive_parser = subparsers.add_parser(
    "archive",
    help="Archive OpenSpec change"
  )
  archive_parser.add_argument(
    "--id",
    required=True,
    help="Change ID to archive"
  )
  archive_parser.add_argument(
    "--skip-specs",
    action="store_true",
    help="Skip spec updates"
  )
  
  args = parser.parse_args()
  
  if not args.command:
    parser.print_help()
    return 1
  
  # Route to appropriate command handler
  if args.command == "proposal":
    return proposal_command(args)
  elif args.command == "apply":
    return apply_command(args)
  elif args.command == "archive":
    return archive_command(args)
  else:
    print(f"Unknown command: {args.command}")
    return 1


if __name__ == "__main__":
  sys.exit(main())
