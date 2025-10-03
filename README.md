# arxiv-news

Fetch daily cs.AI arXiv papers and filter for LLM/mechanistic interpretability via local Ollama `llama3.2`.

## Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) installed and running (`ollama serve`)
- A local model named `llama3.2` pulled:
  
  ```bash
  ollama pull llama3.2
  ```

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd src
```

## Usage
Fetch the last day of cs.AI papers, filter with `llama3.2`, print matches, and save to `data/YYYY-MM-DD_HH-MM-SS.jsonl`:
```bash
python -m arxiv_news.cli fetch-filter --days 1
```

Note: For daily "news" runs, it's recommended to use `--days 2` due to arXiv's indexing delay.

Options:
- `--days INT` (default 1): lookback window in days
- `--limit INT` (default 200): max results pulled from arXiv before filtering
- `--no-limit`: fetch all papers within the date range (ignores `--limit`)
- `--model TEXT` (default `llama3.2`): Ollama model to use
- `--ollama-url TEXT` (default `http://127.0.0.1:11434`)
- `--out PATH` (default `data/YYYY-MM-DD_HH-MM-SS.jsonl`): path to write JSONL results
- `--no-save`: do not write file, only print

### Fetch all papers from a date range
To fetch all papers from the last 3 days without any limit:
```bash
python -m arxiv_news.cli fetch-filter --days 3 --no-limit
```

### Classify a single arXiv ID
Fetch a single paper and run the classifier:
```bash
python -m arxiv_news.cli classify-id 2509.00698
```
You can override model or URL:
```bash
python -m arxiv_news.cli classify-id 2509.00698 --model llama3.2 --ollama-url http://127.0.0.1:11434
```

## Output
Each matched paper is printed and written as JSON lines with fields: `title`, `link`, `abstract`, `published`.

Output files are automatically timestamped (e.g., `data/2024-10-02_14-30-45.jsonl`) to avoid overwrites.

## Keyword Pre-filtering
- A simple, case-sensitive keyword pre-filter runs before LLM classification to reduce model calls.
- Current static keywords: `{"LLM", " LLM ", " LLMs ", "Large Language Model", "interpretability", "VLM", "MLLM"}`
- Only papers whose title or abstract contains any of these keywords are sent to the LLM.

## How it Works
The tool now uses an improved fetching strategy:
1. **Complete date range coverage**: Fetches all papers within the specified date window (not just the newest N)
2. **Client-side sorting**: Downloads a large batch, then sorts by publication date and applies limits
3. **Flexible limiting**: Use `--no-limit` to get all papers from the date range, or `--limit N` for the newest N papers

This ensures you get the complete picture of recent research activity rather than missing papers due to arXiv's API pagination.

## Notes
- Ensure Ollama is running on `http://127.0.0.1:11434`.
- You can adjust the prompt in `arxiv_news/ollama_filter.py`.
- The tool fetches papers efficiently by downloading in batches and filtering client-side.
- **API Delay**: arXiv's API has a 24-hour delay in reflecting new submissions.
- **Real-time alternative**: For immediate updates, use RSS: https://rss.arxiv.org/rss/cs.AI
