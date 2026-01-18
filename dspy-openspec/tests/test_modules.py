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

"""Tests for DSPy OpenSpec modules."""

from __future__ import annotations

import pytest

from dspy_openspec.modules.proposal_module import ProposalModule
from dspy_openspec.modules.apply_module import ApplyModule
from dspy_openspec.modules.archive_module import ArchiveModule


def test_proposal_module_init():
  """Test ProposalModule initialization."""
  module = ProposalModule()
  assert module is not None
  assert hasattr(module, "generate")


def test_apply_module_init():
  """Test ApplyModule initialization."""
  module = ApplyModule(interactive=False)
  assert module is not None
  assert hasattr(module, "apply")


def test_archive_module_init():
  """Test ArchiveModule initialization."""
  module = ArchiveModule()
  assert module is not None
  assert hasattr(module, "archive")


def test_proposal_signature_has_instruction():
  """Test that ProposalSignature loads instruction content."""
  from dspy_openspec.signatures.proposal import ProposalSignature
  
  # Check that docstring is loaded from instruction file
  assert ProposalSignature.__doc__ is not None
  assert len(ProposalSignature.__doc__) > 100
  assert "ProposalInitialAgent" in ProposalSignature.__doc__


def test_apply_signature_has_instruction():
  """Test that ApplySignature loads instruction content."""
  from dspy_openspec.signatures.apply import ApplySignature
  
  # Check that docstring is loaded from instruction file
  assert ApplySignature.__doc__ is not None
  assert len(ApplySignature.__doc__) > 100
  assert "ApplyAgent" in ApplySignature.__doc__


def test_archive_signature_has_instruction():
  """Test that ArchiveSignature loads instruction content."""
  from dspy_openspec.signatures.archive import ArchiveSignature
  
  # Check that docstring is loaded from instruction file
  assert ArchiveSignature.__doc__ is not None
  assert len(ArchiveSignature.__doc__) > 100
  assert "ArchiveAgent" in ArchiveSignature.__doc__
