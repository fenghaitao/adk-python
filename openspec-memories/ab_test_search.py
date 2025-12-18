#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any

ROOT = Path(__file__).resolve().parent
CLI = ROOT / 'search_cli.py'

COMMON_QUERIES = [
  'timer',
  'register bank',
  'freq_mhz clock',
  'DMA descriptor',
  'watchdog interrupt',
  'troubleshooting compile error',
]

def run_cli(query: str, *, bm25: bool) -> Dict[str, Any]:
  cmd = [sys.executable, str(CLI), query, '--top-k', '5', '--json']
  if bm25:
    cmd.append('--bm25')
  out = subprocess.check_output(cmd, cwd=str(ROOT))
  return json.loads(out.decode('utf-8'))


def compare_queries(queries: List[str]) -> List[Dict[str, Any]]:
  rows = []
  for q in queries:
    t = run_cli(q, bm25=False)
    b = run_cli(q, bm25=True)
    def topsig(res):
      if not res['results']:
        return None
      r0 = res['results'][0]
      return f"{Path(r0['file_path']).name} :: {r0['heading']}"
    rows.append({
      'query': q,
      'tfidf_top': topsig(t),
      'bm25_top': topsig(b),
      'tfidf_first_score': (t['results'][0]['score'] if t['results'] else None),
      'bm25_first_score': (b['results'][0]['score'] if b['results'] else None),
      'tfidf_count': len(t['results']),
      'bm25_count': len(b['results']),
    })
  return rows


def write_csv(rows: List[Dict[str, Any]], path: Path) -> None:
  with path.open('w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=[
      'query','tfidf_top','bm25_top','tfidf_first_score','bm25_first_score','tfidf_count','bm25_count'
    ])
    w.writeheader()
    for r in rows:
      w.writerow(r)


def write_json(rows: List[Dict[str, Any]], path: Path) -> None:
  path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')


def load_queries(path: Path) -> List[str]:
  lines = path.read_text(encoding='utf-8').splitlines()
  return [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith('#')]


def main():
  ap = argparse.ArgumentParser(description='A/B compare TF-IDF vs BM25 for common queries')
  ap.add_argument('--queries', help='Path to a file containing one query per line')
  ap.add_argument('--csv', help='Write results to CSV at this path')
  ap.add_argument('--json', dest='json_out', help='Write results to JSON at this path')
  args = ap.parse_args()

  queries = COMMON_QUERIES
  if args.queries:
    qpath = Path(args.queries)
    if not qpath.exists():
      print(f"Queries file not found: {qpath}", file=sys.stderr)
      sys.exit(2)
    queries = load_queries(qpath)

  rows = compare_queries(queries)

  if args.csv:
    write_csv(rows, Path(args.csv))
  if args.json_out:
    write_json(rows, Path(args.json_out))

  # Always print a compact table to stdout
  print("Query | TF-IDF top | BM25 top | TF-IDF score | BM25 score | TF-IDF n | BM25 n")
  print("------|------------|----------|--------------|------------|----------|--------")
  for r in rows:
    print(
      f"{r['query']} | {r['tfidf_top']} | {r['bm25_top']} | {r['tfidf_first_score']} | {r['bm25_first_score']} | {r['tfidf_count']} | {r['bm25_count']}"
    )

if __name__ == '__main__':
  main()
