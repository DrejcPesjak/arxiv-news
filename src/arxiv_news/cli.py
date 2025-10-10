from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import click

from .models import Paper

from .arxiv_fetcher import fetch_recent_papers, stream_recent_papers, fetch_paper_by_id
from .ollama_filter import classify_paper, filter_interpretability
from .keyword_filter import filter_by_keywords
from .ranking_agent import tournament_rank_papers
from .config import (
	ARXIV_DEFAULT_DAYS,
	ARXIV_DEFAULT_LIMIT,
	CLASSIFICATION_MODEL,
	OLLAMA_URL,
	OUTPUT_ALL_DIR,
	OUTPUT_FILTERED_DIR,
	OUTPUT_RANKED_DIR,
)


def _write_lines(path: Path, lines) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	with path.open("w", encoding="utf-8") as f:
		for line in lines:
			f.write(str(line) + "\n")


@click.group()
def cli() -> None:
	pass


@cli.command(name="fetch-filter")
@click.option("--days", type=int, default=ARXIV_DEFAULT_DAYS, show_default=True, help="Lookback window in days")
@click.option("--limit", type=int, default=ARXIV_DEFAULT_LIMIT, show_default=True, help="Max arXiv results before filtering")
@click.option("--no-limit", is_flag=True, default=False, help="Fetch all papers within the date range (ignores --limit)")
@click.option("--model", type=str, default=CLASSIFICATION_MODEL, show_default=True, help="Ollama model name")
@click.option("--ollama-url", type=str, default=OLLAMA_URL, show_default=True, help="Ollama base URL")
@click.option("--out", type=click.Path(path_type=Path), default=None, help="Path to write JSONL")
@click.option("--no-save", is_flag=True, default=False, help="Do not write output file")
def fetch_and_filter(days: int, limit: int, no_limit: bool, model: str, ollama_url: str, out: Path | None, no_save: bool) -> None:
	"""
	Fetch recent cs.AI papers, stream and print links as they arrive, then filter with
	Ollama model, print and optionally save JSONL of matches.
	"""
	# Compute timestamps once for consistent filenames across outputs
	now = datetime.now(timezone.utc)
	timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
	
	# Set limit to None if no-limit flag is used
	effective_limit = None if no_limit else limit
	

	# =========================
	# STEP 1: STREAM RECENT PAPERS
	# =========================
	streamed = list()
	for p in stream_recent_papers(days=days, limit=effective_limit):
		streamed.append(p)
		click.echo(f"{p.published} {p.link}")

	if not streamed:
		click.echo("No recent papers found in cs.AI for the given window.")
		return

	click.echo(f"Found {len(streamed)} recent papers in the last {days} days.")

	# Save only links to data/all/<date>.txt
	if not no_save:
		all_path = OUTPUT_ALL_DIR / f"{timestamp}.txt"
		_write_lines(all_path, (str(p.link) for p in streamed))
		click.echo(f"Saved {len(streamed)} links to {all_path}")

	
	# =========================
	# STEP 2: KEYWORD PRE-FILTER
	# =========================
	# Pre-filter by simple keyword matching to reduce LLM calls
	keyword_matches = filter_by_keywords(streamed)

	if not keyword_matches:
		click.echo("No papers matched keyword pre-filter.")
		return
	
	click.echo(f"Keyword matches: {len(keyword_matches)} (pre-filtered)")


	# =========================
	# STEP 3: LLM INTERPRETABILITY FILTER
	# =========================
	matches = filter_interpretability(keyword_matches, model=model, url=ollama_url)

	click.echo(f"Matches: {len(matches)} (filtered)")

	# Print matches succinctly
	for p in matches:
		click.echo("- " + p.title)
		click.echo("  " + str(p.link))
		click.echo("  " + p.abstract)
		click.echo("")

	# Save JSONL (all matches)
	if not no_save:
		if out is None:
			out = OUTPUT_FILTERED_DIR / f"{timestamp}.jsonl"
		out.parent.mkdir(parents=True, exist_ok=True)
		with out.open("w", encoding="utf-8") as f:
			for p in matches:
				f.write(json.dumps(p.model_dump(), default=str) + "\n")
		click.echo(f"Saved {len(matches)} matches to {out}")

	
	# =========================
	# STEP 4: TOURNAMENT RANKING
	# =========================

	# # test code to load data/filtered/2025-10-03_07-05-53.jsonl
	# matches = [Paper.model_validate_json(line) for line in Path("data/filtered/2025-10-03_07-05-53.jsonl").read_text().splitlines()]
	# click.echo(f"Loaded {len(matches)} matches")
	
	ranking_result = tournament_rank_papers(matches, model=model, url=ollama_url)
	click.echo("Final ranking result:")
	click.echo(ranking_result)

	# Save ranking result to data/ranked/
	if not no_save:
		ranked_path = OUTPUT_RANKED_DIR / f"{timestamp}.md"
		ranked_path.parent.mkdir(parents=True, exist_ok=True)
		with ranked_path.open("w", encoding="utf-8") as f:
			f.write(ranking_result)
		click.echo(f"Saved ranking result to {ranked_path}")


@cli.command(name="classify-id")
@click.argument("arxiv_id", type=str)
@click.option("--model", type=str, default=CLASSIFICATION_MODEL, show_default=True, help="Ollama model name")
@click.option("--ollama-url", type=str, default=OLLAMA_URL, show_default=True, help="Ollama base URL")
def classify_id(arxiv_id: str, model: str, ollama_url: str) -> None:
	"""
	Fetch a single arXiv paper by ID and run the interpretability classifier.
	"""
	paper = fetch_paper_by_id(arxiv_id)
	if paper is None:
		click.echo(f"Could not fetch arXiv:{arxiv_id}")
		return

	res = classify_paper(paper, model=model, url=ollama_url)
	click.echo(paper.title)
	click.echo(str(paper.link))
	click.echo(paper.abstract)
	click.echo(json.dumps({"reason": res.reason, "is_interpretability": res.is_interpretability}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
	cli()
