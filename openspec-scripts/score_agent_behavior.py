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

"""Automated scoring script for agent behavior evaluation.

This script analyzes the apply agent's session log to evaluate
documentation reading, efficiency, and time management.
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime

def score_agent_behavior(workdir: str, device_name: str) -> dict:
    """Score agent behavior based on session log analysis.
    
    Args:
        workdir: Working directory containing the OpenSpec project
        device_name: Name of the device being evaluated
        
    Returns:
        dict with scores and evidence for each criterion
    """
    scores = {
        "documentation_reading": 0,
        "efficiency": 0,
        "time_score": 0,
        "evidence": {}
    }
    
    # Find the most recent session file
    apply_agent_dir = Path(workdir) / "adk_openspec_apply_agent"
    session_files = list(apply_agent_dir.glob("*.session.txt"))
    
    if not session_files:
        scores["evidence"]["error"] = "❌ No session.txt file found"
        return scores
    
    # Get most recent session file
    session_file = max(session_files, key=lambda p: p.stat().st_mtime)
    
    print("=" * 60)
    print(f"ANALYZING SESSION: {session_file.name}")
    print("=" * 60)
    
    with open(session_file, 'r') as f:
        session_content = f.read()
    
    # 1. Documentation Reading (50 points)
    print("\n1. DOCUMENTATION READING (50 points)")
    print("-" * 60)
    
    doc_checks = {
        "AGENTS.md": (10, r'openspec/AGENTS\.md'),
        "proposal.md": (10, r'openspec/changes/[^/]+/proposal\.md'),
        "tasks.md": (10, r'openspec/changes/[^/]+/tasks\.md'),
        "spec.md": (10, r'specs/[^/]+/spec\.md'),
        "DML_memories": (10, r'openspec-memories/0\d+_DML.*\.md'),
        "Test_memories": (10, r'openspec-memories/0\d+_Test.*\.md'),
    }
    
    for doc_name, (points, pattern) in doc_checks.items():
        matches = re.findall(pattern, session_content)
        if matches:
            if doc_name in ["DML_memories", "Test_memories"]:
                # Count how many different memory files
                unique_docs = set(matches)
                count = len(unique_docs)
                if count >= 4:
                    score = points
                else:
                    score = min(points, count * 2)
                scores["documentation_reading"] += score
                scores["evidence"][doc_name] = f"✅ Read {count} files (+{score}/{points})"
                print(f"✅ {doc_name}: Read {count} files (+{score}/{points})")
            else:
                scores["documentation_reading"] += points
                scores["evidence"][doc_name] = f"✅ Read {doc_name} (+{points})"
                print(f"✅ {doc_name}: YES (+{points})")
        else:
            scores["evidence"][doc_name] = f"❌ Did not read {doc_name} (0/{points})"
            print(f"❌ {doc_name}: NO (0/{points})")
    
    # 2. Efficiency Analysis (30 points)
    print("\n2. EFFICIENCY ANALYSIS (30 points)")
    print("-" * 60)
    
    # Count build attempts
    build_attempts = len(re.findall(r'build_simics_project', session_content))
    test_attempts = len(re.findall(r'run_simics_test', session_content))
    
    # Count errors
    build_errors = len(re.findall(r'error:', session_content, re.IGNORECASE))
    test_failures = len(re.findall(r'test.*failed', session_content, re.IGNORECASE))
    
    total_errors = build_errors + test_failures
    
    # Check for final success
    final_success = bool(re.search(r'(build.*success|all tests passed)', session_content[-2000:], re.IGNORECASE))
    
    # 2a. Error resolution (10 points)
    if final_success and total_errors > 0:
        scores["efficiency"] += 10
        scores["evidence"]["error_resolution"] = f"✅ All errors fixed ({total_errors} total) (+10)"
        print(f"✅ All errors fixed ({total_errors} total) (+10)")
    elif final_success:
        scores["efficiency"] += 10
        scores["evidence"]["error_resolution"] = "✅ No errors encountered (+10)"
        print("✅ No errors encountered (+10)")
    else:
        scores["evidence"]["error_resolution"] = f"❌ Not all errors fixed (0/10)"
        print(f"❌ Not all errors fixed (0/10)")
    
    # 2b. Best practices compliance (10 points)
    best_practices_followed = 0
    
    # Check for DML best practice patterns
    if re.search(r'07_DML_Register_Access_Scope', session_content):
        best_practices_followed += 1
    if re.search(r'02_DML_Anti_Patterns', session_content):
        best_practices_followed += 1
    if re.search(r'03_Test_Register_Access', session_content):
        best_practices_followed += 1
    
    # Simple heuristic: if agent read best practices AND succeeded
    if best_practices_followed >= 2 and final_success:
        scores["efficiency"] += 10
        scores["evidence"]["best_practices"] = f"✅ Followed best practices ({best_practices_followed} docs) (+10)"
        print(f"✅ Followed best practices ({best_practices_followed} docs) (+10)")
    elif best_practices_followed >= 1:
        scores["efficiency"] += 5
        scores["evidence"]["best_practices"] = f"⚠️ Partially followed ({best_practices_followed} docs) (+5)"
        print(f"⚠️ Partially followed ({best_practices_followed} docs) (+5)")
    else:
        scores["evidence"]["best_practices"] = "❌ Did not follow best practices (0)"
        print("❌ Did not follow best practices (0)")
    
    # 3. Time Analysis (10 points)
    print("\n3. TIME ANALYSIS (10 points)")
    print("-" * 60)
    
    # Try to extract timestamps
    timestamps = re.findall(r'\[(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', session_content)
    
    if len(timestamps) >= 2:
        try:
            start_time = datetime.fromisoformat(timestamps[0])
            end_time = datetime.fromisoformat(timestamps[-1])
            duration_minutes = (end_time - start_time).total_seconds() / 60
            
            if duration_minutes < 20:
                time_score = 10
            elif duration_minutes <= 40:
                time_score = int(10 - (duration_minutes - 20) / 20 * 10)
            else:
                time_score = 0
            
            scores["time_score"] = time_score
            scores["evidence"]["time"] = f"Duration: {duration_minutes:.1f} min (+{time_score}/10)"
            print(f"✅ Duration: {duration_minutes:.1f} min (+{time_score}/10)")
        except:
            scores["evidence"]["time"] = "⚠️ Could not parse timestamps"
            print("⚠️ Could not parse timestamps")
    else:
        scores["evidence"]["time"] = "⚠️ Insufficient timestamp data"
        print("⚠️ Insufficient timestamp data")
    
    scores["total_behavior_score"] = (
        scores["documentation_reading"] + 
        scores["efficiency"] + 
        scores["time_score"]
    )
    
    print("\n" + "=" * 60)
    print(f"TOTAL AGENT BEHAVIOR SCORE: {scores['total_behavior_score']}/90")
    print("=" * 60)
    
    return scores

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: score_agent_behavior.py <workdir> <device_name>")
        sys.exit(1)
    
    workdir = sys.argv[1]
    device_name = sys.argv[2]
    
    import json
    result = score_agent_behavior(workdir, device_name)
    print("\n" + json.dumps(result, indent=2))
