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

"""Identify gaps in memory files - errors that no existing file addresses.

This script analyzes historical sessions to find error patterns that occur
even when agents read relevant memory files, or errors that have no
corresponding memory file at all.

Usage:
  python identify_memory_gaps.py \\
    --sessions historical_sessions.json \\
    --memory-dir ../openspec-memories \\
    --output memory_gaps_report.json
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
  """Extract memory files read during session."""
  files_read = set()
  patterns = [
    r'openspec-memories/([0-9]+_[A-Za-z_]+\.md)',
    r'Reading.*?([0-9]+_[A-Za-z_]+\.md)',
  ]
  for pattern in patterns:
    matches = re.findall(pattern, session_log, re.IGNORECASE)
    files_read.update(matches)
  return files_read


def extract_all_errors(session: Dict) -> List[Tuple[str, str]]:
  """Extract all errors with their types.
  
  Returns:
    List of (error_type, error_description) tuples
  """
  errors = []
  implementation = session.get('implementation', '')
  tests = session.get('tests', '')
  
  # DML compilation errors
  if "'this' is not available" in implementation or "scope error" in implementation.lower():
    errors.append(('scope_error', "'this' not available in current scope"))
  
  if "undefined method" in implementation.lower():
    errors.append(('undefined_method', "Method not found or not declared"))
  
  if "type mismatch" in implementation.lower() or "incompatible types" in implementation.lower():
    errors.append(('type_error', "Type mismatch or incompatible types"))
  
  # Anti-patterns
  if re.search(r'method\s+\w*update\w*\s*\([^)]*\)\s*{', implementation):
    if 'after' not in implementation:
      errors.append(('cycle_by_cycle', "Cycle-by-cycle updates instead of event-based"))
  
  if re.search(r'method\s+init\s*\([^)]*\).*SIM_cycle_count', implementation, re.DOTALL):
    errors.append(('sim_cycle_count_in_init', "SIM_cycle_count used in init method"))
  
  # Missing session keyword
  if re.search(r'(uint\d+|int\d+)\s+\w+\s*;', implementation):
    if 'session' not in implementation:
      errors.append(('missing_session', "State variables without session keyword"))
  
  # Interrupt handling issues
  if 'interrupt' in implementation.lower():
    if not re.search(r'(raise|lower|set).*interrupt', implementation, re.IGNORECASE):
      errors.append(('incomplete_interrupt', "Interrupt declared but not raised/lowered"))
  
  # Register access issues
  if re.search(r'this\.val\s*=', implementation):
    errors.append(('direct_register_write', "Direct register write without side-effects"))
  
  # Test issues
  if tests:
    if 'clk.freq_mhz' not in tests:
      errors.append(('missing_clock_setup', "Clock frequency not configured in tests"))
    
    if 'dev.queue' not in tests and 'timer' in implementation.lower():
      errors.append(('missing_queue', "Queue not assigned for timing device"))
    
    if not re.search(r'def\s+test_', tests):
      errors.append(('no_test_functions', "No test functions defined"))
  
  # Memory/resource leaks
  if 'malloc' in implementation and 'free' not in implementation:
    errors.append(('memory_leak', "Memory allocated but not freed"))
  
  # Hardcoded values
  if re.search(r'=\s*0x[0-9a-fA-F]{8,}', implementation):
    errors.append(('hardcoded_address', "Hardcoded memory addresses"))
  
  return errors


def load_existing_memory_files(memory_dir: Path) -> Dict[str, Dict]:
  """Load and categorize existing memory files.
  
  Returns:
    Dict mapping file names to their metadata
  """
  memory_files = {}
  
  for file_path in memory_dir.glob('*.md'):
    if file_path.name.startswith('00_'):
      continue  # Skip index files
    
    content = file_path.read_text()
    
    # Extract topics covered (simple keyword extraction)
    topics = set()
    
    # Common keywords
    keywords = [
      'scope', 'register', 'timer', 'interrupt', 'session', 'event',
      'anti-pattern', 'troubleshooting', 'test', 'clock', 'queue',
      'syntax', 'pattern', 'modeling', 'philosophy'
    ]
    
    for keyword in keywords:
      if keyword in content.lower():
        topics.add(keyword)
    
    memory_files[file_path.name] = {
      'path': str(file_path),
      'topics': topics,
      'size': len(content),
      'lines': len(content.split('\n'))
    }
  
  return memory_files


def map_errors_to_files(
    error_type: str,
    memory_files: Dict[str, Dict]
) -> List[str]:
  """Map an error type to relevant memory files.
  
  Args:
    error_type: Type of error
    memory_files: Available memory files
    
  Returns:
    List of file names that should cover this error
  """
  # Mapping of error types to relevant topics
  error_to_topics = {
    'scope_error': ['scope', 'register'],
    'undefined_method': ['syntax', 'troubleshooting'],
    'type_error': ['syntax', 'troubleshooting'],
    'cycle_by_cycle': ['anti-pattern', 'timer', 'event'],
    'sim_cycle_count_in_init': ['anti-pattern', 'timer'],
    'missing_session': ['session', 'syntax'],
    'incomplete_interrupt': ['interrupt', 'pattern'],
    'direct_register_write': ['register', 'pattern'],
    'missing_clock_setup': ['test', 'clock'],
    'missing_queue': ['test', 'timer', 'queue'],
    'no_test_functions': ['test'],
    'memory_leak': ['pattern', 'troubleshooting'],
    'hardcoded_address': ['pattern', 'anti-pattern'],
  }
  
  relevant_topics = error_to_topics.get(error_type, [])
  relevant_files = []
  
  for file_name, file_info in memory_files.items():
    if any(topic in file_info['topics'] for topic in relevant_topics):
      relevant_files.append(file_name)
  
  return relevant_files


def analyze_memory_gaps(
    sessions_file: Path,
    memory_dir: Path
) -> Dict:
  """Analyze gaps in memory file coverage.
  
  Returns:
    Dictionary with gap analysis results
  """
  # Load sessions
  with open(sessions_file) as f:
    sessions = json.load(f)
  
  # Load existing memory files
  memory_files = load_existing_memory_files(memory_dir)
  
  # Track errors
  error_stats = defaultdict(lambda: {
    'total_occurrences': 0,
    'sessions_with_error': [],
    'files_read_when_error_occurred': Counter(),
    'relevant_files_available': [],
    'relevant_files_read': Counter(),
    'relevant_files_not_read': Counter(),
    'no_relevant_file_exists': False
  })
  
  # Analyze each session
  for session in sessions:
    session_log = session.get('session_log', '')
    device_name = session.get('device_name', 'unknown')
    files_read = extract_files_read(session_log)
    errors = extract_all_errors(session)
    
    for error_type, error_desc in errors:
      stats = error_stats[error_type]
      stats['total_occurrences'] += 1
      stats['sessions_with_error'].append(device_name)
      
      # Track which files were read
      for file in files_read:
        stats['files_read_when_error_occurred'][file] += 1
      
      # Find relevant files for this error
      relevant_files = map_errors_to_files(error_type, memory_files)
      stats['relevant_files_available'] = relevant_files
      
      if not relevant_files:
        stats['no_relevant_file_exists'] = True
      else:
        # Check if relevant files were read
        for file in relevant_files:
          if file in files_read:
            stats['relevant_files_read'][file] += 1
          else:
            stats['relevant_files_not_read'][file] += 1
  
  # Convert to regular dict for JSON serialization
  result = {}
  for error_type, stats in error_stats.items():
    result[error_type] = {
      'total_occurrences': stats['total_occurrences'],
      'sessions_affected': len(set(stats['sessions_with_error'])),
      'relevant_files_available': stats['relevant_files_available'],
      'relevant_files_read': dict(stats['relevant_files_read']),
      'relevant_files_not_read': dict(stats['relevant_files_not_read']),
      'no_relevant_file_exists': stats['no_relevant_file_exists'],
      'gap_type': classify_gap(stats)
    }
  
  return result


def classify_gap(stats: Dict) -> str:
  """Classify the type of gap.
  
  Returns:
    Gap classification: 'missing_file', 'file_not_read', 'file_ineffective', 'no_gap'
  """
  if stats['no_relevant_file_exists']:
    return 'missing_file'
  
  # Check if relevant files exist but weren't read
  total_not_read = sum(stats['relevant_files_not_read'].values())
  total_read = sum(stats['relevant_files_read'].values())
  
  if total_not_read > total_read:
    return 'file_not_read'
  
  # If files were read but errors still occurred
  if total_read > 0:
    return 'file_ineffective'
  
  return 'no_gap'


def print_gap_report(gap_analysis: Dict):
  """Print human-readable gap analysis report."""
  
  print("\n" + "="*70)
  print("MEMORY FILE GAP ANALYSIS")
  print("="*70)
  
  # Group by gap type
  gaps_by_type = defaultdict(list)
  for error_type, stats in gap_analysis.items():
    gaps_by_type[stats['gap_type']].append((error_type, stats))
  
  # 1. Missing files (highest priority)
  if 'missing_file' in gaps_by_type:
    print("\n🔴 CRITICAL: MISSING MEMORY FILES")
    print("   These errors have NO corresponding memory file!\n")
    
    for error_type, stats in sorted(
      gaps_by_type['missing_file'],
      key=lambda x: x[1]['total_occurrences'],
      reverse=True
    ):
      print(f"   • {error_type.replace('_', ' ').title()}")
      print(f"     Occurrences: {stats['total_occurrences']}")
      print(f"     Sessions affected: {stats['sessions_affected']}")
      print(f"     📝 ACTION: Create new memory file covering this topic")
      print()
  
  # 2. Files not being read (medium priority)
  if 'file_not_read' in gaps_by_type:
    print("\n🟡 MEDIUM PRIORITY: RELEVANT FILES NOT BEING READ")
    print("   Memory files exist but agents aren't reading them!\n")
    
    for error_type, stats in sorted(
      gaps_by_type['file_not_read'],
      key=lambda x: x[1]['total_occurrences'],
      reverse=True
    ):
      print(f"   • {error_type.replace('_', ' ').title()}")
      print(f"     Occurrences: {stats['total_occurrences']}")
      print(f"     Relevant files available: {', '.join(stats['relevant_files_available'])}")
      print(f"     Times NOT read: {dict(stats['relevant_files_not_read'])}")
      print(f"     📝 ACTION: Update index file or instructions to recommend these files")
      print()
  
  # 3. Files ineffective (low priority - use optimizer)
  if 'file_ineffective' in gaps_by_type:
    print("\n🟢 LOW PRIORITY: FILES READ BUT INEFFECTIVE")
    print("   Agents read the files but still made errors.\n")
    
    for error_type, stats in sorted(
      gaps_by_type['file_ineffective'],
      key=lambda x: x[1]['total_occurrences'],
      reverse=True
    )[:5]:  # Show top 5
      print(f"   • {error_type.replace('_', ' ').title()}")
      print(f"     Occurrences: {stats['total_occurrences']}")
      print(f"     Files read: {dict(stats['relevant_files_read'])}")
      print(f"     📝 ACTION: Optimize these files with optimize_memory_file.py")
      print()
  
  # Summary and recommendations
  print("\n" + "="*70)
  print("RECOMMENDATIONS")
  print("="*70)
  
  missing_count = len(gaps_by_type.get('missing_file', []))
  not_read_count = len(gaps_by_type.get('file_not_read', []))
  ineffective_count = len(gaps_by_type.get('file_ineffective', []))
  
  print(f"\n📊 Summary:")
  print(f"   • {missing_count} error types need NEW memory files")
  print(f"   • {not_read_count} error types have files that aren't being read")
  print(f"   • {ineffective_count} error types have ineffective files")
  
  print(f"\n💡 Action Plan:")
  
  if missing_count > 0:
    print(f"\n   1. CREATE NEW MEMORY FILES (Priority: HIGH)")
    for error_type, stats in gaps_by_type.get('missing_file', [])[:3]:
      print(f"      • Create file for: {error_type.replace('_', ' ')}")
      print(f"        Suggested name: 0X_{error_type.title()}.md")
  
  if not_read_count > 0:
    print(f"\n   2. UPDATE INDEX FILES (Priority: MEDIUM)")
    print(f"      • Update 00_DML_Best_Practices_Index.md")
    print(f"      • Update 00_Test_Best_Practices_Index.md")
    print(f"      • Add recommendations in apply_agent_instruction.md")
  
  if ineffective_count > 0:
    print(f"\n   3. OPTIMIZE EXISTING FILES (Priority: LOW)")
    print(f"      • Run: python optimize_memory_file.py ...")
    print(f"      • Focus on files with highest error rates")
  
  print("\n" + "="*70 + "\n")


def main():
  parser = argparse.ArgumentParser(
    description="Identify gaps in memory file coverage"
  )
  parser.add_argument(
    "--sessions",
    required=True,
    help="Path to historical sessions JSON"
  )
  parser.add_argument(
    "--memory-dir",
    required=True,
    help="Path to openspec-memories directory"
  )
  parser.add_argument(
    "--output",
    help="Output JSON file for detailed analysis (optional)"
  )
  
  args = parser.parse_args()
  
  sessions_file = Path(args.sessions)
  memory_dir = Path(args.memory_dir)
  
  if not sessions_file.exists():
    print(f"❌ Error: Sessions file not found: {sessions_file}")
    sys.exit(1)
  
  if not memory_dir.exists():
    print(f"❌ Error: Memory directory not found: {memory_dir}")
    sys.exit(1)
  
  print(f"📊 Analyzing memory file gaps...")
  print(f"📂 Sessions: {sessions_file}")
  print(f"📁 Memory dir: {memory_dir}")
  
  # Run analysis
  gap_analysis = analyze_memory_gaps(sessions_file, memory_dir)
  
  # Print report
  print_gap_report(gap_analysis)
  
  # Save detailed analysis if requested
  if args.output:
    output_path = Path(args.output)
    with open(output_path, 'w') as f:
      json.dump(gap_analysis, f, indent=2)
    print(f"💾 Detailed analysis saved to: {output_path}\n")


if __name__ == "__main__":
  main()
