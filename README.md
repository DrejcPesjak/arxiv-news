# arxiv-news

Fetch daily cs.AI arXiv papers, filter for LLM/mechanistic interpretability via local Ollama, and rank results using tournament-style selection.

## Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) installed and running (`ollama serve`)
- A local model for filtering. For example, `llama3.2`:
  
  ```bash
  ollama pull llama3.2
  ```

- **For ranking**: We recommend a reasoning LLM like `qwen3` for better paper selection:
  
  ```bash
  ollama pull qwen3
  ```

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd src
```

## Configuration

All project settings are centralized in `config.yaml` at the project root. You can customize:

- **Research focus**: Update `ranking.research_focus` to match your research area
- **Models**: Set default models for classification and ranking
- **Prompts**: Customize classification and ranking prompts
- **Keywords**: Modify the pre-filter keyword list
- **Tournament settings**: Adjust top-k values for ranking stages
- **Output paths**: Change where files are saved

Example config section:
```yaml
ranking:
  model: "qwen3"
  research_focus: "my PhD LLM interpretability research"
  tournament_topk: [2, 5]  # [first_stage_top_k, final_stage_top_k]
```

CLI flags override config defaults when specified.

## Usage

### Fetch, Filter, and Rank Papers
The `fetch-filter` command provides a complete pipeline that:
1. Fetches recent cs.AI papers from arXiv
2. Pre-filters by keywords
3. Filters for interpretability using an LLM
4. Automatically ranks results using tournament-style selection

Basic usage:
```bash
python -m arxiv_news.cli fetch-filter --days 1
```

**Using a reasoning model for better ranking** (recommended):
```bash
python -m arxiv_news.cli fetch-filter --days 2 --model qwen3
```

Note: For daily "news" runs, it's recommended to use `--days 2` due to arXiv's indexing delay.

The command will:
- Save raw paper links to `data/all/YYYY-MM-DD_HH-MM-SS.txt`
- Save filtered papers to `data/filtered/YYYY-MM-DD_HH-MM-SS.jsonl`
- Save ranked results to `data/ranked/YYYY-MM-DD_HH-MM-SS.md`

**Tournament Ranking Process:**
- Papers are processed in batches of 10
- First stage: Select top 2 papers from each batch
- Final stage: From all batch winners, select the final top 5
- Reasoning LLMs like `qwen3` produce better rankings through extended thinking (automatically filtered from output)

Options:
- `--days INT` (default 1): lookback window in days
- `--limit INT` (default 200): max results pulled from arXiv before filtering
- `--no-limit`: fetch all papers within the date range (ignores `--limit`)
- `--model TEXT` (default `llama3.2`): Ollama model to use for both filtering and ranking
- `--ollama-url TEXT` (default `http://127.0.0.1:11434`)
- `--out PATH` (default `data/filtered/YYYY-MM-DD_HH-MM-SS.jsonl`): path to write filtered JSONL results
- `--no-save`: do not write files, only print

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
The tool organizes output into three directories:
- `data/all/`: Raw fetched papers for the date range
- `data/filtered/`: LLM-filtered papers matching interpretability criteria (JSONL format with fields: `title`, `link`, `abstract`, `published`)
- `data/ranked/`: Tournament-ranked top papers with reasoning (Markdown format)

Output files are automatically timestamped (e.g., `2025-10-02_14-30-45.jsonl`) to avoid overwrites.

## Keyword Pre-filtering
- A simple, case-sensitive keyword pre-filter runs before LLM classification to reduce model calls.
- Current static keywords: `{"LLM", " LLM ", " LLMs ", "Large Language Model", "interpretability", "VLM", "MLLM"}`
- Only papers whose title or abstract contains any of these keywords are sent to the LLM.

## How it Works
The tool provides a complete research paper discovery pipeline:

1. **Complete date range coverage**: Fetches all papers within the specified date window (not just the newest N)
2. **Client-side sorting**: Downloads a large batch, then sorts by publication date and applies limits
3. **Flexible limiting**: Use `--no-limit` to get all papers from the date range, or `--limit N` for the newest N papers
4. **Keyword pre-filtering**: Fast pre-filter reduces unnecessary LLM calls
5. **LLM filtering**: Uses local Ollama models to identify relevant interpretability papers
6. **Tournament ranking**: Automatically ranks filtered papers in batches to select the most important ones

This ensures you get the complete picture of recent research activity, filtered and ranked by relevance.

## Notes
- Ensure Ollama is running on `http://127.0.0.1:11434`.
- You can adjust the prompt in `arxiv_news/ollama_filter.py`.
- The tool fetches papers efficiently by downloading in batches and filtering client-side.
- **API Delay**: arXiv's API has a 24-hour delay in reflecting new submissions.
- **Real-time alternative**: For immediate updates, use RSS: https://rss.arxiv.org/rss/cs.AI
