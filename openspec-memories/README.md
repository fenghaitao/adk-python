# openspec-memories Search CLI

A lightweight, dependency-free search tool for the markdown knowledge base in this folder. It indexes all `.md` files, splits them into section-level units (by headings), and returns ranked results with short contextual snippets. Suitable for terminal use, editor integration, or piping JSON to other tools.

## Quick start

```bash
# Keyword search with ranked section-level results
python3 search_cli.py timer --top-k 5

# JSON output for tooling/editor integration
python3 search_cli.py "register bank" --top-k 8 --json
```

## Command-line options

- query (positional): Search terms, e.g., "timer", "register bank"
- --root <path>: Root folder containing .md files (default: this folder)
- --top-k <N>: Max results to return (default: 10)
- --snippet <N>: Snippet width in characters (default: 160)
- --json: Emit machine-readable JSON instead of pretty text

## Output (JSON schema)

```json
{
  "query": "register bank",
  "total_sections": 123,
  "results": [
    {
      "file_path": "openspec-memories/03_Test_Register_Access.md",
      "heading": "Bank Access Basics",
      "heading_level": 2,
      "section_id": "03_Test_Register_Access#bank-access-basics",
      "score": 2.735102,
      "snippet": "… use dev_util.bank_regs(device.bank.<bank_name>) …"
    }
  ]
}
```

- total_sections: Count of indexed sections across all markdown files
- section_id: Local anchor you can turn into links in a docs site ("<filename>#<slug>")
- score: Ranking score (use for ordering; values are not comparable across runs)

## How it works (algorithms)

The CLI is designed to be fast, simple, and dependency-free while returning useful, granular results:

1) Section-based indexing
- Each markdown file is split into sections at headings (`#`..`######`).
- Every section stores: file path, heading level, heading text, computed section id, and the section body.
- Benefits: Smaller, more focused results; headings work as strong signals.

2) Tokenization
- Tokens are word-like sequences `[A-Za-z0-9_]+` lowercased.
- Both section body and heading text are tokenized to compute term statistics.

3) TF–IDF ranking (body + heading)
- For each section `i` and query term `t`:
  - `tf_i(t)` = frequency of `t` in that section (body + heading)
  - `idf(t)` = `log((N + 1) / (df(t) + 0.5)) + 1`, where `N` is number of sections and `df(t)` is the number of sections containing `t`.
  - Term contribution = `(1 + log(1 + tf_i(t))) * idf(t)`
- Section score = sum of contributions over all query terms, normalized by `sqrt(section_length)` to reduce long-text bias.
- Rationale: Simple, proven weighting that rewards rare-but-relevant terms and multiple hits.

4) Fuzzy title bonus (lightweight recall boost)
- Compute `ratio = SequenceMatcher(query, title).ratio()` where `title = "<filename> <heading>"`.
- Add a small bonus: `0.5 * ratio` to the TF–IDF score.
- Effect: Prefer sections whose headings/filenames roughly match the query, without full fuzzy search over the body.

5) Snippet generation
- Pick the earliest occurrence of any query term and extract a centered window (default ~160 chars).
- Highlight matches with square brackets `[term]`.
- Aim: Provide quick context without heavy parsing.

### Design trade-offs
- No external deps (fast, portable) vs. limited linguistic features (no stemming/lemmatization).
- Simple TF–IDF + title bonus vs. full-featured fuzzy search (keeps performance and implementation simple).
- Section-level indexing improves result precision but can increase index size; acceptable for this repo scale.

## Tips for better results
- Use specific nouns and function names present in docs (e.g., `dev_util.bank_regs`, `freq_mhz`).
- Combine terms to narrow (e.g., "timer reload event").
- Keep docs consistent: include clear headings, keywords, and explicit names for banks/registers.

## Limitations
- No phrase queries or boolean operators (terms are treated independently).
- No stemming; plural/singular variants are distinct tokens.
- Scores are not calibrated across runs; use rank ordering only.

## Roadmap (optional enhancements)
- Tags: Add a lightweight `Tags:` footer to each doc to improve match quality.
- --json schema stability: version the JSON and add a `version` field.
- Editor integration: small VSCode task or script to show results inline.
- Docs site: Publish with MkDocs Material for client-side search and deep linking.
- Semantic search (optional): Add embedding-based reranking or retrieval for intent-based queries.

## Maintenance
- The script scans `*.md` in this folder; new docs are picked up automatically.
- Keep headings descriptive—headings strongly influence ranking.
- Validate links/anchors if you turn `section_id` into real URLs in a docs site.

---

Tags: readme
