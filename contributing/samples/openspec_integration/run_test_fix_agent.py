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

"""Example script to run the TestFixAgent.

This script demonstrates how to use the TestFixAgent to fix build and test
failures after apply_agent has completed its implementation.

Usage:
    python run_test_fix_agent.py --id <CHANGE_ID>
    
Example:
    python run_test_fix_agent.py --id implement-wdt-initial
"""

import argparse
import sys
from pathlib import Path

# Add the src directory to the path for ADK imports
current_dir = Path(__file__).parent
adk_src_dir = current_dir.parent.parent.parent / "src"
if adk_src_dir.exists():
    sys.path.insert(0, str(adk_src_dir))

from test_fix_agent import test_fix_agent


def main():
    parser = argparse.ArgumentParser(
        description="Run TestFixAgent to fix build and test failures"
    )
    parser.add_argument(
        "--id", 
        required=True,
        help="OpenSpec change ID to fix (e.g., implement-wdt-initial)"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Construct the fix command
    fix_command = f"/fix --id {args.id}"
    
    print(f"🔧 Starting TestFixAgent for change: {args.id}")
    print(f"📝 Command: {fix_command}")
    print("=" * 60)
    
    try:
        # Run the test fix agent
        result = test_fix_agent.run(fix_command)
        
        print("\n" + "=" * 60)
        print("🎯 TestFixAgent Results:")
        print("=" * 60)
        
        if hasattr(result, 'change_id'):
            print(f"Change ID: {result.change_id}")
            print(f"Initial Build Status: {result.initial_build_status}")
            print(f"Initial Test Status: {result.initial_test_status}")
            print(f"Final Build Status: {result.final_build_status}")
            print(f"Final Test Status: {result.final_test_status}")
            
            if result.fixes_applied:
                print(f"\n🔧 Fixes Applied ({len(result.fixes_applied)}):")
                for i, fix in enumerate(result.fixes_applied, 1):
                    print(f"  {i}. {fix.error_type}: {fix.fix_description}")
                    if fix.files_modified:
                        print(f"     Files: {', '.join(fix.files_modified)}")
                    print(f"     Success: {'✅' if fix.success else '❌'}")
            
            if result.preserved_functionality:
                print(f"\n✅ Preserved Functionality ({len(result.preserved_functionality)}):")
                for func in result.preserved_functionality:
                    print(f"  - {func}")
            
            if result.improvements_made:
                print(f"\n🚀 Improvements Made ({len(result.improvements_made)}):")
                for improvement in result.improvements_made:
                    print(f"  - {improvement}")
            
            if result.remaining_issues:
                print(f"\n⚠️  Remaining Issues ({len(result.remaining_issues)}):")
                for issue in result.remaining_issues:
                    print(f"  - {issue}")
            
            print(f"\n📋 Summary:")
            print(f"  {result.summary}")
            
        else:
            print("Result:", result)
            
    except Exception as e:
        print(f"❌ Error running TestFixAgent: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    print("\n🏁 TestFixAgent completed!")


if __name__ == "__main__":
    main()