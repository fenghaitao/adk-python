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

from __future__ import annotations

import argparse
import dataclasses
import math
import re
import sys
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
import json

WORD_RE = re.compile(r"[A-Za-z0-9_]+")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)\s*$")


@dataclasses.dataclass
class Section:
  file_path: Path
  heading_level: int
  heading_text: str
  section_id: str
  text: str

  @property
  def doc_title(self) -> str:
    return self.file_path.name


@dataclasses.dataclass
class CorpusIndex:
  sections: List[Section]
  # term -> document frequency (# sections containing term)
  df: Dict[str, int]
  # per-section term frequency
  tf: List[Counter]
  # normalized section lengths in tokens
  lengths: List[int]


def tokenize(text: str) -> List[str]:
  return [t.lower() for t in WORD_RE.findall(text)]


def read_markdown_sections(path: Path) -> Iterable[Section]:
  try:
    data = path.read_text(encoding="utf-8")
  except Exception:
    return []

  lines = data.splitlines()
  sections: List[Section] = []
  cur_level = 0
  cur_heading = path.stem
  cur_id = cur_heading
  buf: List[str] = []

  def push():
    if buf:
      sections.append(
          Section(
              file_path=path,
              heading_level=cur_level or 1,
              heading_text=cur_heading,
              section_id=cur_id,
              text="\n".join(buf).strip(),
          )
      )

  for line in lines:
    m = HEADING_RE.match(line)
    if m:
      # new section starts
      push()
      cur_level = len(m.group(1))
      cur_heading = m.group(2).strip()
      # create a local anchor-like id
      slug = re.sub(r"[^a-z0-9]+", "-", cur_heading.lower()).strip("-")
      cur_id = f"{path.stem}#{slug}" if slug else path.stem
      buf = []
    else:
      buf.append(line)
  push()
  # If file had no headings, create one synthetic section
  if not sections:
    sections.append(
        Section(
            file_path=path,
            heading_level=1,
            heading_text=path.stem,
            section_id=path.stem,
            text=data,
        )
    )
  return sections


def build_index(root: Path) -> CorpusIndex:
  md_files = sorted(root.glob("*.md"))
  sections: List[Section] = []
  for fp in md_files:
    sections.extend(list(read_markdown_sections(fp)))

  tf: List[Counter] = []
  df: Dict[str, int] = defaultdict(int)
  lengths: List[int] = []

  for sec in sections:
    toks = tokenize(sec.text + "\n" + sec.heading_text)
    counts = Counter(toks)
    tf.append(counts)
    lengths.append(sum(counts.values()))
  # compute df
  for counts in tf:
    for term in counts.keys():
      df[term] += 1

  return CorpusIndex(sections=sections, df=dict(df), tf=tf, lengths=lengths)


def tfidf_score(query_terms: List[str], idx: CorpusIndex, i: int) -> float:
  # cosine-like tf-idf score
  tf_i = idx.tf[i]
  N = max(1, len(idx.sections))
  score = 0.0
  for t in query_terms:
    if t not in idx.df:
      continue
    idf = math.log((N + 1) / (idx.df[t] + 0.5)) + 1.0
    tf_val = tf_i.get(t, 0)
    if tf_val == 0:
      continue
    score += (1 + math.log(1 + tf_val)) * idf
  # normalize by length to reduce section size bias
  denom = math.sqrt(idx.lengths[i]) if idx.lengths[i] > 0 else 1.0
  return score / denom


def fuzzy_bonus(query: str, sec: Section) -> float:
  # Add a small bonus based on similarity to heading and filename
  title = f"{sec.doc_title} {sec.heading_text}"
  r = SequenceMatcher(None, query.lower(), title.lower()).ratio()
  # weight small: 0..0.5
  return 0.5 * r


def highlight_snippet(text: str, terms: List[str], width: int = 160) -> str:
  if not text:
    return ""
  low = text.lower()
  positions: List[int] = []
  for t in terms:
    p = low.find(t)
    if p != -1:
      positions.append(p)
  start = 0
  if positions:
    start = max(0, min(positions) - width // 4)
  snippet = text[start:start + width]
  # simple highlighting with [] around matches
  for t in sorted(set(terms), key=len, reverse=True):
    snippet = re.sub(
        rf"(?i)\b({re.escape(t)})\b",
        r"[\1]",
        snippet,
    )
  return snippet.replace("\n", " ")


def search(idx: CorpusIndex, query: str, top_k: int, snippet_width: int) -> List[Tuple[float, int]]:
  q_terms = tokenize(query)
  scored: List[Tuple[float, int]] = []
  for i, sec in enumerate(idx.sections):
    base = tfidf_score(q_terms, idx, i)
    bonus = fuzzy_bonus(query, sec)
    total = base + bonus
    if total > 0:
      scored.append((total, i))
  scored.sort(key=lambda x: x[0], reverse=True)
  return scored[:top_k]


def print_results(results: List[Tuple[float, int]], idx: CorpusIndex, query: str, snippet_width: int) -> None:
  if not results:
    print("No results.")
    return
  q_terms = tokenize(query)
  for rank, (score, i) in enumerate(results, start=1):
    sec = idx.sections[i]
    rel_path = sec.file_path.as_posix()
    print(f"{rank}. {rel_path} :: {sec.heading_text}  [score={score:.3f}]")
    snippet = highlight_snippet(sec.text, q_terms, width=snippet_width)
    if snippet:
      print(f"   … {snippet} …")


def results_as_json(results: List[Tuple[float, int]], idx: CorpusIndex, query: str, snippet_width: int) -> str:
  items = []
  q_terms = tokenize(query)
  for score, i in results:
    sec = idx.sections[i]
    items.append({
        "file_path": sec.file_path.as_posix(),
        "heading": sec.heading_text,
        "heading_level": sec.heading_level,
        "section_id": sec.section_id,
        "score": round(float(score), 6),
        "snippet": highlight_snippet(sec.text, q_terms, width=snippet_width),
    })
  return json.dumps({
      "query": query,
      "total_sections": len(idx.sections),
      "results": items,
  }, ensure_ascii=False)


def main(argv: List[str]) -> int:
  p = argparse.ArgumentParser(
      description=(
          "Lightweight search across openspec-memories markdown files. "
          "Ranks sections using TF-IDF plus a fuzzy title bonus."
      )
  )
  p.add_argument("query", help="Search query (keywords)")
  p.add_argument(
      "--root",
      default=str(Path(__file__).resolve().parent),
      help="Root folder containing .md files (default: openspec-memories)",
  )
  p.add_argument("--top-k", type=int, default=10, help="Number of results to return (default: 10)")
  p.add_argument("--snippet", type=int, default=160, help="Snippet width in characters (default: 160)")
  p.add_argument("--json", action="store_true", help="Output results as JSON")

  args = p.parse_args(argv)
  root = Path(args.root)
  if not root.exists():
    print(f"Root not found: {root}", file=sys.stderr)
    return 2

  idx = build_index(root)
  results = search(idx, args.query, args.top_k, args.snippet)
  if args.json:
    print(results_as_json(results, idx, args.query, args.snippet))
  else:
    print_results(results, idx, args.query, args.snippet)
  return 0


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
