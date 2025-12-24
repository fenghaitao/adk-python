#!/usr/bin/env python3
"""
Script to collect and summarize META_IMPROVE_ANALYSIS files from multiple test folders.

Usage:
    python summarize_meta_analysis.py [--results-path PATH] [--start NUM] [--count NUM]

Default:
    results_path: /nfs/pdx/home/yongzhuo/wp5/ai_agents/tests/adk-mcp-rag/g5m_openspec_osdml/wdt_dbg
    start: 45
    count: 10
"""

import os
import re
import glob
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


def parse_duration(duration_str: str) -> Optional[float]:
    """
    Parse duration string like "11.4 minutes" or "5.2 minutes" into minutes.
    Returns None if parsing fails.
    """
    try:
        match = re.search(r'([\d.]+)\s*minutes?', duration_str, re.IGNORECASE)
        if match:
            return float(match.group(1))
    except Exception:
        pass
    return None


def parse_build_attempts(build_str: str) -> Tuple[int, int, int]:
    """
    Parse build attempts string like "18 (2 failed initially, 16 successful)" or just "18".
    Returns (total, failed, successful).
    """
    try:
        # Try to extract total - look for first number
        total_match = re.search(r'(\d+)', build_str)
        total = int(total_match.group(1)) if total_match else 0
        
        # Try to extract failed
        failed_match = re.search(r'(\d+)\s+failed', build_str, re.IGNORECASE)
        failed = int(failed_match.group(1)) if failed_match else 0
        
        # Try to extract successful
        success_match = re.search(r'(\d+)\s+successful', build_str, re.IGNORECASE)
        successful = int(success_match.group(1)) if success_match else (total - failed if total > 0 else 0)
        
        return (total, failed, successful)
    except Exception:
        return (0, 0, 0)


def parse_test_runs(test_str: str) -> Tuple[int, int, int]:
    """
    Parse test runs string like "24 (23 failed, 1 successful at the end)" or just "24".
    Returns (total, failed, passed).
    """
    try:
        # Try to extract total - look for first number
        total_match = re.search(r'(\d+)', test_str)
        total = int(total_match.group(1)) if total_match else 0
        
        # Try to extract failed
        failed_match = re.search(r'(\d+)\s+failed', test_str, re.IGNORECASE)
        failed = int(failed_match.group(1)) if failed_match else 0
        
        # Try to extract passed/successful
        pass_match = re.search(r'(\d+)\s+(successful|passed?|passing)', test_str, re.IGNORECASE)
        passed = int(pass_match.group(1)) if pass_match else (total - failed if total > 0 else 0)
        
        return (total, failed, passed)
    except Exception:
        return (0, 0, 0)


def extract_summary_section(content: str) -> Dict[str, str]:
    """
    Extract the Session Summary section from a META_IMPROVE_ANALYSIS file.
    Returns a dictionary with parsed fields.
    """
    summary = {
        'session_file': 'N/A',
        'duration': 'N/A',
        'duration_minutes': None,
        'build_attempts': 'N/A',
        'build_total': 0,
        'build_failed': 0,
        'build_successful': 0,
        'test_runs': 'N/A',
        'test_total': 0,
        'test_failed': 0,
        'test_passed': 0,
        'final_status': 'N/A',
        'raw_summary': ''  # Store raw summary text
    }
    
    try:
        # Find Session Summary section
        summary_match = re.search(r'## Session Summary\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if not summary_match:
            return summary
        
        summary_text = summary_match.group(1)
        summary['raw_summary'] = summary_text.strip()  # Store the raw text
        
        # Extract session file
        try:
            session_match = re.search(r'Session File:\s*(.+)', summary_text)
            if session_match:
                summary['session_file'] = session_match.group(1).strip()
        except Exception:
            pass
        
        # Extract duration
        try:
            duration_match = re.search(r'Duration:\s*(.+)', summary_text)
            if duration_match:
                duration_str = duration_match.group(1).strip()
                summary['duration'] = duration_str
                summary['duration_minutes'] = parse_duration(duration_str)
        except Exception:
            pass
        
        # Extract build attempts
        try:
            build_match = re.search(r'Build Attempts:\s*(.+)', summary_text)
            if build_match:
                build_str = build_match.group(1).strip()
                summary['build_attempts'] = build_str
                total, failed, successful = parse_build_attempts(build_str)
                summary['build_total'] = total
                summary['build_failed'] = failed
                summary['build_successful'] = successful
        except Exception:
            pass
        
        # Extract test runs
        try:
            test_match = re.search(r'Test Runs:\s*(.+)', summary_text)
            if test_match:
                test_str = test_match.group(1).strip()
                summary['test_runs'] = test_str
                total, failed, passed = parse_test_runs(test_str)
                summary['test_total'] = total
                summary['test_failed'] = failed
                summary['test_passed'] = passed
        except Exception:
            pass
        
        # Extract final status
        try:
            status_match = re.search(r'Final Status:\s*(.+)', summary_text)
            if status_match:
                summary['final_status'] = status_match.group(1).strip()
        except Exception:
            pass
    
    except Exception as e:
        # If any major error occurs, return the default summary
        print(f"Warning: Error parsing summary section: {e}")
    
    return summary


def find_meta_file(folder_path: str) -> Optional[str]:
    """
    Find META_IMPROVE_ANALYSIS_*.md file in the given folder.
    Returns the file path or None if not found.
    """
    try:
        project_path = os.path.join(folder_path, 'adk_openspec_project')
        if not os.path.exists(project_path):
            return None
        
        pattern = os.path.join(project_path, 'META_IMPROVE_ANALYSIS_*.md')
        files = glob.glob(pattern)
        
        # Return the first (or most recent) file found
        if files:
            return sorted(files)[-1]  # Get the latest one if multiple exist
    except Exception as e:
        print(f"Warning: Error searching for META file in {folder_path}: {e}")
    return None


def collect_summaries(results_path: str, start: int, count: int) -> List[Dict]:
    """
    Collect summaries from all specified folders.
    """
    summaries = []
    
    for i in range(start, start + count):
        folder_name = f"{results_path}{i}"
        meta_file = find_meta_file(folder_name)
        
        if meta_file is None:
            # No META file found
            summaries.append({
                'folder': f"wdt_dbg{i}",
                'meta_file': 'N/A',
                'summary': None,
                'error': 'No META_IMPROVE_ANALYSIS file found'
            })
        else:
            try:
                with open(meta_file, 'r') as f:
                    content = f.read()
                
                summary = extract_summary_section(content)
                summaries.append({
                    'folder': f"wdt_dbg{i}",
                    'meta_file': os.path.basename(meta_file),
                    'summary': summary,
                    'error': None
                })
            except Exception as e:
                summaries.append({
                    'folder': f"wdt_dbg{i}",
                    'meta_file': os.path.basename(meta_file) if meta_file else 'N/A',
                    'summary': None,
                    'error': f"Error reading file: {str(e)}"
                })
    
    return summaries


def calculate_statistics(summaries: List[Dict]) -> Dict:
    """
    Calculate statistics from all summaries.
    """
    durations = []
    build_stats = {'total': 0, 'successful': 0, 'failed': 0}
    test_stats = {'total': 0, 'passed': 0, 'failed': 0}
    valid_count = 0
    
    for item in summaries:
        try:
            summary = item.get('summary')
            if summary and not item.get('error'):
                valid_count += 1
                
                # Duration statistics
                if summary['duration_minutes'] is not None:
                    durations.append(summary['duration_minutes'])
                
                # Build statistics
                build_stats['total'] += summary['build_total']
                build_stats['successful'] += summary['build_successful']
                build_stats['failed'] += summary['build_failed']
                
                # Test statistics
                test_stats['total'] += summary['test_total']
                test_stats['passed'] += summary['test_passed']
                test_stats['failed'] += summary['test_failed']
        except Exception as e:
            print(f"Warning: Error calculating statistics for {item.get('folder', 'unknown')}: {e}")
            continue
    
    stats = {
        'valid_count': valid_count,
        'total_count': len(summaries),
        'duration_avg': sum(durations) / len(durations) if durations else None,
        'duration_min': min(durations) if durations else None,
        'duration_max': max(durations) if durations else None,
        'build_total': build_stats['total'],
        'build_successful': build_stats['successful'],
        'build_failed': build_stats['failed'],
        'build_success_rate': (build_stats['successful'] / build_stats['total'] * 100) if build_stats['total'] > 0 else 0,
        'test_total': test_stats['total'],
        'test_passed': test_stats['passed'],
        'test_failed': test_stats['failed'],
        'test_pass_rate': (test_stats['passed'] / test_stats['total'] * 100) if test_stats['total'] > 0 else 0
    }
    
    return stats


def generate_summary_markdown(summaries: List[Dict], stats: Dict, start: int, count: int) -> str:
    """
    Generate the summary markdown content.
    """
    md = []
    md.append(f"# Meta Improvement Analysis Summary Report")
    md.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    md.append(f"")
    md.append(f"## Overview Statistics")
    md.append(f"")
    md.append(f"### Analysis Range")
    md.append(f"- **Test Folders**: wdt_dbg{start} to wdt_dbg{start + count - 1}")
    md.append(f"- **Total Folders Analyzed**: {stats['total_count']}")
    md.append(f"- **Valid Results**: {stats['valid_count']}")
    md.append(f"- **Missing/Error**: {stats['total_count'] - stats['valid_count']}")
    md.append(f"")
    
    # Duration statistics
    md.append(f"### Time Statistics")
    if stats['duration_avg'] is not None:
        md.append(f"- **Average Duration**: {stats['duration_avg']:.2f} minutes")
        md.append(f"- **Min Duration**: {stats['duration_min']:.2f} minutes")
        md.append(f"- **Max Duration**: {stats['duration_max']:.2f} minutes")
    else:
        md.append(f"- **Duration Data**: N/A")
    md.append(f"")
    
    # Build statistics
    md.append(f"### Build Statistics")
    md.append(f"- **Total Build Attempts**: {stats['build_total']}")
    md.append(f"- **Successful Builds**: {stats['build_successful']}")
    md.append(f"- **Failed Builds**: {stats['build_failed']}")
    md.append(f"- **Success Rate**: {stats['build_success_rate']:.1f}%")
    md.append(f"")
    
    # Test statistics
    md.append(f"### Test Statistics")
    md.append(f"- **Total Test Runs**: {stats['test_total']}")
    md.append(f"- **Passed Tests**: {stats['test_passed']}")
    md.append(f"- **Failed Tests**: {stats['test_failed']}")
    md.append(f"- **Pass Rate**: {stats['test_pass_rate']:.1f}%")
    md.append(f"")
    
    # Detailed table
    md.append(f"## Detailed Session Summaries")
    md.append(f"")
    md.append(f"| Folder | Duration | Build Attempts | Test Runs | Final Status | Notes |")
    md.append(f"|--------|----------|----------------|-----------|--------------|-------|")
    
    for item in summaries:
        folder = item['folder']
        summary = item.get('summary')
        error = item.get('error')
        
        if error:
            md.append(f"| {folder} | N/A | N/A | N/A | N/A | {error} |")
        elif summary:
            duration = summary['duration']
            # Format: successful/total (showing build success count / total attempts)
            builds = f"{summary['build_successful']}/{summary['build_total']}" if summary['build_total'] > 0 else "N/A"
            # Format: passed/total (showing test pass count / total runs)
            tests = f"{summary['test_passed']}/{summary['test_total']}" if summary['test_total'] > 0 else "N/A"
            status = summary['final_status']
            md.append(f"| {folder} | {duration} | {builds} | {tests} | {status} | - |")
        else:
            md.append(f"| {folder} | N/A | N/A | N/A | N/A | Unknown error |")
    
    md.append(f"")
    md.append(f"## Notes")
    md.append(f"- **Duration**: Time taken for the entire session")
    md.append(f"- **Build Attempts**: Successful builds / Total build attempts")
    md.append(f"- **Test Runs**: Passed tests / Total test runs")
    md.append(f"- **Final Status**: Build ✅/❌ | Tests ✅/❌")
    md.append(f"")
    
    # Append raw session summaries
    md.append(f"---")
    md.append(f"")
    md.append(f"## Appendix: Raw Session Summaries")
    md.append(f"")
    md.append(f"Below are the complete Session Summary sections from each META_IMPROVE_ANALYSIS file:")
    md.append(f"")
    
    for item in summaries:
        folder = item['folder']
        summary = item.get('summary')
        error = item.get('error')
        
        md.append(f"### {folder}")
        md.append(f"")
        
        if error:
            md.append(f"**Status**: {error}")
            md.append(f"")
        elif summary and summary.get('raw_summary'):
            # Add the raw summary content
            md.append(f"```")
            md.append(summary['raw_summary'])
            md.append(f"```")
            md.append(f"")
        else:
            md.append(f"**Status**: No summary data available")
            md.append(f"")
    
    return "\n".join(md)


def main():
    parser = argparse.ArgumentParser(
        description='Summarize META_IMPROVE_ANALYSIS files from multiple test folders.'
    )
    parser.add_argument(
        '--results-path',
        default='/nfs/pdx/home/yongzhuo/wp5/ai_agents/tests/adk-mcp-rag/g5m_openspec_osdml/wdt_dbg',
        help='Base path for test result folders (default: /nfs/pdx/home/yongzhuo/wp5/ai_agents/tests/adk-mcp-rag/g5m_openspec_osdml/wdt_dbg)'
    )
    parser.add_argument(
        '--start',
        type=int,
        default=45,
        help='Starting folder number (default: 45)'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=10,
        help='Number of folders to process (default: 10)'
    )
    
    args = parser.parse_args()
    
    print(f"Collecting META_IMPROVE_ANALYSIS files...")
    print(f"Results path: {args.results_path}")
    print(f"Range: {args.start} to {args.start + args.count - 1}")
    print()
    
    # Collect summaries
    summaries = collect_summaries(args.results_path, args.start, args.count)
    
    # Calculate statistics
    stats = calculate_statistics(summaries)
    
    # Generate summary markdown
    summary_md = generate_summary_markdown(summaries, stats, args.start, args.count)
    
    # Write output file
    output_filename = f"META_IMPROVE_ANALYSIS_{args.start}_to_{args.start + args.count - 1}_summary.md"
    with open(output_filename, 'w') as f:
        f.write(summary_md)
    
    print(f"Summary report generated: {output_filename}")
    print()
    print("Statistics:")
    print(f"  Valid results: {stats['valid_count']}/{stats['total_count']}")
    if stats['duration_avg'] is not None:
        print(f"  Avg duration: {stats['duration_avg']:.2f} minutes")
    print(f"  Build success rate: {stats['build_success_rate']:.1f}%")
    print(f"  Test pass rate: {stats['test_pass_rate']:.1f}%")


if __name__ == '__main__':
    main()
