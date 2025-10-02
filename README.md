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
```

## Usage
Fetch the last day of cs.AI papers, filter with `llama3.2`, print matches, and save to `data/YYYY-MM-DD.jsonl`:
```bash
python -m arxiv_news.cli fetch-filter --days 1
```

Options:
- `--days INT` (default 1): lookback window
- `--limit INT` (default 200): max results pulled from arXiv before filtering
- `--model TEXT` (default `llama3.2`): Ollama model to use
- `--ollama-url TEXT` (default `http://127.0.0.1:11434`)
- `--out PATH` (default `data/<date>.jsonl`): path to write JSONL results
- `--no-save`: do not write file, only print

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

## Notes
- Ensure Ollama is running on `http://127.0.0.1:11434`.
- You can adjust the prompt in `arxiv_news/ollama_filter.py`.
