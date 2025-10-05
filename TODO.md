# TODO

## Completed ✅

- [x] **Fetch whole date range**: Implement fetching all articles that fall within the "days" parameter, then sort by datetime and take the newest
- [x] **No-limit option**: Add `--no-limit` flag to fetch the whole day (whatever the days limit is) 
- [x] **Timestamped filenames**: Add current time to JSON filename to avoid overwrites
- [x] **Update README**: Document the new features and improved fetching strategy
- [x] **Pre-filtering with string/regex**: Case-sensitive keyword pre-filter before LLM to reduce calls
  - Keywords: `{"LLM", " LLM ", " LLMs ", "Large Language Model", "interpretability", "VLM", "MLLM"}`
  - Only forward papers to LLM if title or abstract contains any keyword
- [x] **Organize output subfolders**: Create `data/all`, `data/filtered`, `data/ranked`
  - `all`: raw fetched papers for the day/range
  - `filtered`: LLM-filtered interpretability matches
  - `ranked`: final ranked selection artifacts/JSONL
- [x] **Ranking agent (tournament style)**: Rank papers via multi-round selection
  - Process in batches of 10; select top 2 from each batch
  - From the remaining, produce a final top-5 list overall
  - Includes filtering of `<think>` blocks from reasoning LLM responses

## In Progress 🚧

## Pending ⏳

- [ ] **Graceful interruption handling**: When user does Ctrl+C, still save current work and add "T" (terminated) to end of filename (before .jsonl extension)
- [ ] **Simple user inputs/config**: Single place (e.g., a YAML file) to set core run parameters
  - arXiv category (e.g., `cs.AI`)
  - keyword filters (list)
  - prompt filter (string template for LLM)
  - N final ranked outputs (int)

## Future Enhancements 💡

- [ ] **Progress indicators**: Add progress bars for long-running operations
- [ ] **Parallel processing**: Process multiple papers simultaneously with LLM
- [ ] **Caching**: Cache LLM responses to avoid re-processing same papers
- [ ] **Export formats**: Support additional output formats (CSV, markdown)
- [ ] **Author-based prioritization**: Extract authors and their organizations from papers
  - Give higher priority to established prominent big players in the field
  - Use author/institution reputation as a ranking signal

## Notes 📝

- Current implementation successfully handles complete date range coverage
- Timestamped outputs prevent file overwrites
- The `--no-limit` option works well for comprehensive daily fetches
