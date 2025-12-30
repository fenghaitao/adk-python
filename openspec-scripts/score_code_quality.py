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

"""Automated scoring script for code quality evaluation.

This script evaluates DML code quality, test quality, build success,
and test pass rate for an OpenSpec implementation.
"""

import os
import sys
import subprocess
import re
import json
from pathlib import Path

def score_code_quality(workdir: str, device_name: str) -> dict:
    """Score code quality based on objective criteria.
    
    Args:
        workdir: Working directory containing the OpenSpec project
        device_name: Name of the device being evaluated
        
    Returns:
        dict with scores and evidence for each criterion
    """
    scores = {
        "build_pass": 0,
        "test_pass": 0,
        "dml_quality": 0,
        "test_quality": 0,
        "evidence": {}
    }
    
    simics_project = Path(workdir) / "simics-project"
    device_dir = simics_project / "modules" / device_name
    test_dir = device_dir / "test"
    
    # 1. Build Test (30 points)
    print("=" * 60)
    print("1. TESTING BUILD (30 points)")
    print("=" * 60)
    try:
        os.chdir(simics_project)
        result = subprocess.run(
            ["make", device_name],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            scores["build_pass"] = 30
            scores["evidence"]["build"] = "✅ Build passed successfully"
            print("✅ Build PASSED (+30 points)")
        else:
            scores["evidence"]["build"] = f"❌ Build failed with return code {result.returncode}"
            print(f"❌ Build FAILED (0 points)")
            print("Build errors:")
            print(result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr)
    except Exception as e:
        scores["evidence"]["build"] = f"❌ Build error: {str(e)}"
        print(f"❌ Build ERROR: {e}")
    
    # 2. Test Pass Rate (10 points)
    print("\n" + "=" * 60)
    print("2. TESTING TESTS (10 points)")
    print("=" * 60)
    try:
        test_runner = simics_project / "bin" / "test-runner"
        test_path = f"modules/{device_name}/test"
        
        result = subprocess.run(
            [str(test_runner), test_path],
            capture_output=True,
            text=True,
            timeout=600,
            cwd=simics_project
        )
        
        # Parse test results
        output = result.stdout + result.stderr
        
        # Look for test summary patterns
        # Pattern 1: "X of Y tests passed"
        match = re.search(r'(\d+)\s+of\s+(\d+)\s+tests?\s+passed', output, re.IGNORECASE)
        if match:
            passed = int(match.group(1))
            total = int(match.group(2))
        else:
            # Pattern 2: Count PASSED/FAILED markers
            passed = len(re.findall(r'\bPASSED\b', output, re.IGNORECASE))
            total = passed + len(re.findall(r'\bFAILED\b', output, re.IGNORECASE))
        
        if total > 0:
            test_score = int((passed / total) * 10)
            scores["test_pass"] = test_score
            scores["evidence"]["test_pass"] = f"Tests: {passed}/{total} passed ({test_score}/10 points)"
            print(f"✅ Tests: {passed}/{total} passed (+{test_score} points)")
        else:
            scores["evidence"]["test_pass"] = "⚠️ No tests found or could not parse results"
            print("⚠️ No tests found or could not parse results")
            
    except Exception as e:
        scores["evidence"]["test_pass"] = f"❌ Test error: {str(e)}"
        print(f"❌ Test ERROR: {e}")
    
    # 3. DML Code Quality Checks (30 points)
    print("\n" + "=" * 60)
    print("3. DML CODE QUALITY (30 points)")
    print("=" * 60)
    
    dml_file = device_dir / f"{device_name}.dml"
    if dml_file.exists():
        with open(dml_file, 'r') as f:
            dml_content = f.read()
        
        # 3a. Register count matches XML (5 points)
        # Find XML file
        xml_files = list(Path(workdir).rglob(f"*{device_name}*.xml"))
        if xml_files:
            with open(xml_files[0], 'r') as f:
                xml_content = f.read()
            xml_regs = len(re.findall(r'<register>', xml_content))
            dml_regs = len(re.findall(r'register\s+\w+', dml_content))
            
            if xml_regs > 0 and dml_regs >= xml_regs:
                scores["dml_quality"] += 5
                scores["evidence"]["dml_registers"] = f"✅ Register count: {dml_regs}/{xml_regs} (+5)"
                print(f"✅ Register count: {dml_regs}/{xml_regs} (+5)")
            else:
                scores["evidence"]["dml_registers"] = f"❌ Register count: {dml_regs}/{xml_regs} (0)"
                print(f"❌ Register count mismatch: {dml_regs}/{xml_regs}")
        
        # 3b. Uses Simics event (5 points)
        if re.search(r'\bevent\s+\w+', dml_content):
            scores["dml_quality"] += 5
            scores["evidence"]["dml_event"] = "✅ Uses Simics event (+5)"
            print("✅ Uses Simics event (+5)")
        else:
            scores["evidence"]["dml_event"] = "❌ No Simics event usage (0)"
            print("❌ No Simics event usage")
        
        # 3c. Lazy evaluation (5 points)
        if re.search(r'(sim_time|SIM_cycle_count)\s*\(', dml_content):
            scores["dml_quality"] += 5
            scores["evidence"]["dml_lazy_eval"] = "✅ Uses lazy evaluation (+5)"
            print("✅ Uses lazy evaluation (+5)")
        else:
            scores["evidence"]["dml_lazy_eval"] = "❌ No lazy evaluation (0)"
            print("❌ No lazy evaluation")
        
        # 3d. Interrupt signal output (5 points)
        if re.search(r'(interrupt|irq).*signal', dml_content, re.IGNORECASE):
            scores["dml_quality"] += 5
            scores["evidence"]["dml_interrupt"] = "✅ Implements interrupt signal (+5)"
            print("✅ Implements interrupt signal (+5)")
        else:
            scores["evidence"]["dml_interrupt"] = "❌ No interrupt signal (0)"
            print("❌ No interrupt signal")
        
        # 3e. Reset signal output (5 points)
        if re.search(r'reset.*signal', dml_content, re.IGNORECASE):
            scores["dml_quality"] += 5
            scores["evidence"]["dml_reset_signal"] = "✅ Implements reset signal (+5)"
            print("✅ Implements reset signal (+5)")
        else:
            scores["evidence"]["dml_reset_signal"] = "❌ No reset signal (0)"
            print("❌ No reset signal")
        
        # 3f. Test mode (5 points)
        if re.search(r'test.*mode', dml_content, re.IGNORECASE):
            scores["dml_quality"] += 5
            scores["evidence"]["dml_test_mode"] = "✅ Implements test mode (+5)"
            print("✅ Implements test mode (+5)")
        else:
            scores["evidence"]["dml_test_mode"] = "❌ No test mode (0)"
            print("❌ No test mode")
        
        # 3g. Interrupt clear logic (5 points)
        if re.search(r'(clear|ack).*interrupt', dml_content, re.IGNORECASE):
            scores["dml_quality"] += 5
            scores["evidence"]["dml_int_clear"] = "✅ Implements interrupt clear (+5)"
            print("✅ Implements interrupt clear (+5)")
        else:
            scores["evidence"]["dml_int_clear"] = "❌ No interrupt clear logic (0)"
            print("❌ No interrupt clear logic")
        
        # 3h. Device reset logic (5 points)
        if re.search(r'method\s+reset', dml_content):
            scores["dml_quality"] += 5
            scores["evidence"]["dml_reset_logic"] = "✅ Implements device reset (+5)"
            print("✅ Implements device reset (+5)")
        else:
            scores["evidence"]["dml_reset_logic"] = "❌ No device reset logic (0)"
            print("❌ No device reset logic")
    else:
        scores["evidence"]["dml_code"] = f"❌ DML file not found: {dml_file}"
        print(f"❌ DML file not found: {dml_file}")
    
    # 4. Test Code Quality (20 points)
    print("\n" + "=" * 60)
    print("4. TEST CODE QUALITY (20 points)")
    print("=" * 60)
    
    if test_dir.exists():
        test_files = list(test_dir.glob("s-*.py"))
        num_tests = len(test_files)
        
        # 4a. Number of test files (10 points max)
        if num_tests >= 8:
            test_count_score = 10
        elif num_tests >= 3:
            test_count_score = 5 + int((num_tests - 3) / 5 * 5)
        else:
            test_count_score = int(num_tests / 3 * 5)
        
        scores["test_quality"] += test_count_score
        scores["evidence"]["test_count"] = f"Test files: {num_tests} (+{test_count_score}/10)"
        print(f"✅ Test files: {num_tests} (+{test_count_score}/10)")
        
        # Check test file content
        correct_patterns = 0
        has_sim_continue = 0
        one_case_per_file = 0
        
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
            
            # 4b. Correct register access pattern
            if re.search(r'dev_util\.bank_regs|regs\.\w+\.(read|write)', content):
                correct_patterns += 1
            
            # 4c. Uses SIM_continue
            if 'SIM_continue' in content:
                has_sim_continue += 1
            
            # 4d. One test case per file (check for single test definition)
            test_defs = len(re.findall(r'^def test_', content, re.MULTILINE))
            if test_defs <= 1:
                one_case_per_file += 1
        
        if num_tests > 0:
            # 4b. Register access pattern (5 points)
            if correct_patterns / num_tests >= 0.8:
                scores["test_quality"] += 5
                scores["evidence"]["test_reg_access"] = f"✅ Correct register access: {correct_patterns}/{num_tests} (+5)"
                print(f"✅ Correct register access: {correct_patterns}/{num_tests} (+5)")
            else:
                scores["evidence"]["test_reg_access"] = f"⚠️ Register access: {correct_patterns}/{num_tests} (0)"
                print(f"⚠️ Register access: {correct_patterns}/{num_tests} (0)")
            
            # 4c. SIM_continue usage (5 points)
            if has_sim_continue / num_tests >= 0.8:
                scores["test_quality"] += 5
                scores["evidence"]["test_sim_continue"] = f"✅ SIM_continue usage: {has_sim_continue}/{num_tests} (+5)"
                print(f"✅ SIM_continue usage: {has_sim_continue}/{num_tests} (+5)")
            else:
                scores["evidence"]["test_sim_continue"] = f"⚠️ SIM_continue usage: {has_sim_continue}/{num_tests} (0)"
                print(f"⚠️ SIM_continue usage: {has_sim_continue}/{num_tests} (0)")
    else:
        scores["evidence"]["test_code"] = f"❌ Test directory not found: {test_dir}"
        print(f"❌ Test directory not found: {test_dir}")
    
    scores["total_code_score"] = (
        scores["build_pass"] + 
        scores["test_pass"] + 
        scores["dml_quality"] + 
        scores["test_quality"]
    )
    
    print("\n" + "=" * 60)
    print(f"TOTAL CODE QUALITY SCORE: {scores['total_code_score']}/90")
    print("=" * 60)
    
    return scores

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: score_code_quality.py <workdir> <device_name>")
        sys.exit(1)
    
    workdir = sys.argv[1]
    device_name = sys.argv[2]
    
    result = score_code_quality(workdir, device_name)
    print("\n" + json.dumps(result, indent=2))
