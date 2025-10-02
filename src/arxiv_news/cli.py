from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import click

from .arxiv_fetcher import fetch_recent_papers, stream_recent_papers, fetch_paper_by_id
from .ollama_filter import classify_paper, filter_interpretability


@click.group()
def cli() -> None:
	pass


@cli.command(name="fetch-filter")
@click.option("--days", type=int, default=1, show_default=True, help="Lookback window in days")
@click.option("--limit", type=int, default=200, show_default=True, help="Max arXiv results before filtering")
@click.option("--no-limit", is_flag=True, default=False, help="Fetch all papers within the date range (ignores --limit)")
@click.option("--model", type=str, default="llama3.2", show_default=True, help="Ollama model name")
@click.option("--ollama-url", type=str, default="http://127.0.0.1:11434", show_default=True, help="Ollama base URL")
@click.option("--out", type=click.Path(path_type=Path), default=None, help="Path to write JSONL")
@click.option("--no-save", is_flag=True, default=False, help="Do not write output file")
def fetch_and_filter(days: int, limit: int, no_limit: bool, model: str, ollama_url: str, out: Path | None, no_save: bool) -> None:
	"""
	Fetch recent cs.AI papers, stream and print links as they arrive, then filter with
	Ollama model, print and optionally save JSONL of matches.
	"""
	# Set limit to None if no-limit flag is used
	effective_limit = None if no_limit else limit
	
	streamed = list()
	for p in stream_recent_papers(days=days, limit=effective_limit):
		streamed.append(p)
		click.echo(str(p.link))

	if not streamed:
		click.echo("No recent papers found in cs.AI for the given window.")
		return

	click.echo(f"Found {len(streamed)} recent papers in the last {days} days.\n")
	
	matches = filter_interpretability(streamed, model=model, url=ollama_url)

	# Print matches succinctly
	for p in matches:
		click.echo("- " + p.title)
		click.echo("  " + str(p.link))
		click.echo("  " + p.abstract)
		click.echo("")

	# Save JSONL
	if not no_save:
		if out is None:
			now = datetime.now(timezone.utc)
			timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
			out = Path("data") / f"{timestamp}.jsonl"
		out.parent.mkdir(parents=True, exist_ok=True)
		with out.open("w", encoding="utf-8") as f:
			for p in matches:
				f.write(json.dumps(p.model_dump(), default=str) + "\n")
		click.echo(f"Saved {len(matches)} matches to {out}")


@cli.command(name="classify-id")
@click.argument("arxiv_id", type=str)
@click.option("--model", type=str, default="llama3.2", show_default=True, help="Ollama model name")
@click.option("--ollama-url", type=str, default="http://127.0.0.1:11434", show_default=True, help="Ollama base URL")
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
