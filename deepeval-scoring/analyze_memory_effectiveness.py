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

"""Analyze memory file effectiveness based on historical sessions.

This script identifies which memory/best practices files need optimization
by analyzing error patterns that occur even after agents read those files.

Usage:
  python analyze_memory_effectiveness.py \\
    --sessions historical_sessions.json \\
    --output memory_effectiveness_report.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple


def extract_files_read(session_log: str) -> Set[str]:
  """Extract memory files that were read during session.
  
  Args:
    session_log: Session log content
    
  Returns:
    Set of memory file names that were read
  """
  files_read = set()
  
  # Look for patterns like:
  # - "Reading openspec-memories/02_DML_Anti_Patterns.md"
  # - "Loaded 02_DML_Anti_Patterns.md"
  # - "openspec-memories/02_DML_Anti_Patterns.md"
  
  patterns = [
    r'openspec-memories/([0-9]+_[A-Za-z_]+\.md)',
    r'Reading.*?([0-9]+_[A-Za-z_]+\.md)',
    r'Loaded.*?([0-9]+_[A-Za-z_]+\.md)',
  ]
  
  for pattern in patterns:
    matches = re.findall(pattern, session_log, re.IGNORECASE)
    files_read.update(matches)
  
  return files_read


def extract_compilation_errors(implementation: str) -> List[str]:
  """Extract compilation error patterns from implementation.
  
  Args:
    implementation: DML implementation code
    
  Returns:
    List of error patterns found
  """
  errors = []
  
  # Common DML compilation errors
  error_patterns = {
    'scope_error': r"'this' is not available|scope error",
    'undefined_method': r"undefined method|method not found",
    'type_error': r"type mismatch|incompatible types",
    'syntax_error': r"syntax error|unexpected token",
    'missing_import': r"undefined identifier|not declared",
  }
  
  for error_type, pattern in error_patterns.items():
    if re.search(pattern, implementation, re.IGNORECASE):
      errors.append(error_type)
  
  return errors


def extract_anti_patterns(implementation: str) -> List[str]:
  """Extract anti-pattern occurrences from implementation.
  
  Args:
    implementation: DML implementation code
    
  Returns:
    List of anti-patterns found
  """
  anti_patterns = []
  
  # Anti-Pattern #1: Cycle-by-cycle updates
  if re.search(r'method\s+\w*update\w*\s*\([^)]*\)\s*{', implementation):
    if 'after' not in implementation:
      anti_patterns.append('cycle_by_cycle_updates')
  
  # Anti-Pattern #2: SIM_cycle_count in init
  if re.search(r'method\s+init\s*\([^)]*\).*SIM_cycle_count', 
               implementation, re.DOTALL):
    anti_patterns.append('sim_cycle_count_in_init')
  
  # Anti-Pattern #3: Incomplete timer (has countdown but no event)
  if 'countdown' in implementation.lower() or 'timer' in implementation.lower():
    if 'after' not in implementation and 'event' not in implementation:
      anti_patterns.append('incomplete_timer')
  
  # Missing session keyword for state
  if re.search(r'(uint\d+|int\d+)\s+\w+\s*;', implementation):
    if 'session' not in implementation:
      anti_patterns.append('missing_session_keyword')
  
  return anti_patterns


def extract_test_issues(tests_content: str) -> List[str]:
  """Extract test quality issues.
  
  Args:
    tests_content: Test file content
    
  Returns:
    List of test issues found
  """
  issues = []
  
  if not tests_content:
    return ['no_tests']
  
  # Missing clock setup
  if 'clk.freq_mhz' not in tests_content:
    issues.append('missing_clock_setup')
  
  # Missing queue assignment
  if 'dev.queue' not in tests_content:
    issues.append('missing_queue_assignment')
  
  # No timing tests
  if 'SIM_cycle_count' not in tests_content and 'after' not in tests_content:
    issues.append('no_timing_tests')
  
  # No register access tests
  if 'read' not in tests_content.lower() and 'write' not in tests_content.lower():
    issues.append('no_register_tests')
  
  return issues


def analyze_memory_file_effectiveness(
    sessions_file: Path
) -> Dict[str, Dict]:
  """Analyze which memory files are most/least effective.
  
  Args:
    sessions_file: Path to historical sessions JSON
    
  Returns:
    Dictionary mapping file names to effectiveness stats
  """
  with open(sessions_file) as f:
    sessions = json.load(f)
  
  # Track effectiveness per file
  file_stats = defaultdict(lambda: {
    'reads': 0,
    'sessions_with_errors': 0,
    'total_sessions': 0,
    'errors_after_reading': Counter(),
    'anti_patterns_after_reading': Counter(),
    'test_issues_after_reading': Counter(),
    'success_rate': 0.0,
    'avg_score': 0.0,
    'scores': []
  })
  
  for session in sessions:
    session_log = session.get('session_log', '')
    implementation = session.get('implementation', '')
    tests = session.get('tests', '')
    score = session.get('score', 0.0)
    
    # Extract what was read
    files_read = extract_files_read(session_log)
    
    # Extract errors/issues
    compilation_errors = extract_compilation_errors(implementation)
    anti_patterns = extract_anti_patterns(implementation)
    test_issues = extract_test_issues(tests)
    
    has_errors = bool(compilation_errors or anti_patterns or test_issues)
    
    # Update stats for each file that was read
    for file in files_read:
      file_stats[file]['reads'] += 1
      file_stats[file]['total_sessions'] += 1
      file_stats[file]['scores'].append(score)
      
      if has_errors:
        file_stats[file]['sessions_with_errors'] += 1
      
      # Track specific errors after reading this file
      for error in compilation_errors:
        file_stats[file]['errors_after_reading'][error] += 1
      
      for pattern in anti_patterns:
        file_stats[file]['anti_patterns_after_reading'][pattern] += 1
      
      for issue in test_issues:
        file_stats[file]['test_issues_after_reading'][issue] += 1
  
  # Calculate effectiveness scores
  for file, stats in file_stats.items():
    if stats['total_sessions'] > 0:
      stats['success_rate'] = 1 - (
        stats['sessions_with_errors'] / stats['total_sessions']
      )
      stats['avg_score'] = sum(stats['scores']) / len(stats['scores'])
    
    # Convert Counters to dicts for JSON serialization
    stats['errors_after_reading'] = dict(stats['errors_after_reading'])
    stats['anti_patterns_after_reading'] = dict(
      stats['anti_patterns_after_reading']
    )
    stats['test_issues_after_reading'] = dict(
      stats['test_issues_after_reading']
    )
  
  return dict(file_stats)


def print_effectiveness_report(file_stats: Dict[str, Dict]):
  """Print human-readable effectiveness report.
  
  Args:
    file_stats: File effectiveness statistics
  """
  # Sort by success rate (least effective first)
  sorted_files = sorted(
    file_stats.items(),
    key=lambda x: (x[1]['success_rate'], x[1]['avg_score'])
  )
  
  print("\n" + "="*70)
  print("MEMORY FILE EFFECTIVENESS ANALYSIS")
  print("="*70)
  print("\nFiles are sorted by effectiveness (least effective first)")
  print("These are the best candidates for optimization.\n")
  
  for i, (file, stats) in enumerate(sorted_files, 1):
    print(f"\n{i}. {file}")
    print(f"   {'─'*66}")
    print(f"   Success Rate: {stats['success_rate']:.1%} "
          f"(errors in {stats['sessions_with_errors']}/{stats['total_sessions']} sessions)")
    print(f"   Average Score: {stats['avg_score']:.1%}")
    print(f"   Times Read: {stats['reads']}")
    
    # Show top issues
    all_issues = []
    all_issues.extend(stats['errors_after_reading'].items())
    all_issues.extend(stats['anti_patterns_after_reading'].items())
    all_issues.extend(stats['test_issues_after_reading'].items())
    
    if all_issues:
      all_issues.sort(key=lambda x: x[1], reverse=True)
      print(f"\n   Top Issues After Reading This File:")
      for issue, count in all_issues[:5]:
        issue_name = issue.replace('_', ' ').title()
        print(f"     • {issue_name}: {count} occurrence(s)")
  
  # Summary recommendations
  print("\n" + "="*70)
  print("OPTIMIZATION RECOMMENDATIONS")
  print("="*70)
  
  # Files with success rate < 70%
  needs_optimization = [
    (file, stats) for file, stats in sorted_files
    if stats['success_rate'] < 0.7
  ]
  
  if needs_optimization:
    print(f"\n🔴 HIGH PRIORITY ({len(needs_optimization)} files):")
    print("   These files have <70% success rate and should be optimized first.\n")
    for file, stats in needs_optimization[:3]:
      print(f"   • {file} ({stats['success_rate']:.1%} success)")
      # Get most common issue
      all_issues = list(stats['errors_after_reading'].items()) + \
                   list(stats['anti_patterns_after_reading'].items()) + \
                   list(stats['test_issues_after_reading'].items())
      if all_issues:
        top_issue = max(all_issues, key=lambda x: x[1])
        print(f"     Focus on: {top_issue[0].replace('_', ' ')}")
  
  # Files with 70-85% success rate
  moderate = [
    (file, stats) for file, stats in sorted_files
    if 0.7 <= stats['success_rate'] < 0.85
  ]
  
  if moderate:
    print(f"\n🟡 MEDIUM PRIORITY ({len(moderate)} files):")
    print("   These files work okay but could be improved.\n")
    for file, stats in moderate[:3]:
      print(f"   • {file} ({stats['success_rate']:.1%} success)")
  
  # Files with >85% success rate
  effective = [
    (file, stats) for file, stats in sorted_files
    if stats['success_rate'] >= 0.85
  ]
  
  if effective:
    print(f"\n🟢 LOW PRIORITY ({len(effective)} files):")
    print("   These files are already effective.\n")
    for file, stats in effective[:3]:
      print(f"   • {file} ({stats['success_rate']:.1%} success)")
  
  print("\n" + "="*70)
  print("\n💡 Next Steps:")
  print("   1. Run optimizer on high-priority files:")
  print("      python optimize_memory_file.py --memory-file <file> ...")
  print("   2. A/B test optimized versions")
  print("   3. Measure improvement in error rates")
  print("   4. Iterate on medium-priority files\n")


def main():
  parser = argparse.ArgumentParser(
    description="Analyze memory file effectiveness"
  )
  parser.add_argument(
    "--sessions",
    required=True,
    help="Path to historical sessions JSON file"
  )
  parser.add_argument(
    "--output",
    help="Output JSON file for detailed stats (optional)"
  )
  parser.add_argument(
    "--min-reads",
    type=int,
    default=3,
    help="Minimum number of reads to include file (default: 3)"
  )
  
  args = parser.parse_args()
  
  sessions_file = Path(args.sessions)
  if not sessions_file.exists():
    print(f"❌ Error: Sessions file not found: {sessions_file}")
    sys.exit(1)
  
  print(f"📊 Analyzing memory file effectiveness...")
  print(f"📂 Sessions file: {sessions_file}")
  
  # Analyze effectiveness
  file_stats = analyze_memory_file_effectiveness(sessions_file)
  
  # Filter by minimum reads
  file_stats = {
    file: stats for file, stats in file_stats.items()
    if stats['reads'] >= args.min_reads
  }
  
  if not file_stats:
    print(f"\n⚠️  No memory files found with at least {args.min_reads} reads")
    print("   Try lowering --min-reads or collecting more sessions")
    sys.exit(1)
  
  # Print report
  print_effectiveness_report(file_stats)
  
  # Save detailed stats if requested
  if args.output:
    output_path = Path(args.output)
    with open(output_path, 'w') as f:
      json.dump(file_stats, f, indent=2)
    print(f"\n💾 Detailed stats saved to: {output_path}")


if __name__ == "__main__":
  main()
