from __future__ import annotations

import json
import re
from typing import List, Tuple
import click
import requests

from .models import Paper


DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"

# Tournament configuration: [first_stage_top_k, final_stage_top_k]
TOURNAMENT_TOPK = [2, 5]

# PROMPT = """You are a research paper ranking expert. Given a list of papers about LLM interpretability, 
# select the {num} most relevant and interesting articles.
# Focus on papers that are most relevant to LLM interpretability PhD research. 
# Return your selection as plain markdown text with the paper titles and brief reasoning for each choice."""

PROMPT = """From the following papers, select exactly top {num} most relevant and important for my phd LLM interpretability research. 
Return your selection as plain markdown text with the paper titles and brief reasoning/summary for each choice. 
Do not include any other text. Also do not rank them (use unordered list). 
The final answer should be exactly {num} paragraphs.
Think for maximum of 60 seconds before selecting the papers."""


def _filter_think_blocks(text: str) -> str:
	"""Remove <think> blocks from LLM response."""
	# Remove <think>...</think> blocks (case insensitive, handles multiline)
	filtered = re.sub(r'<think>.*?</think>', '', text, flags=re.IGNORECASE | re.DOTALL)
	# Clean up extra whitespace that might be left
	filtered = re.sub(r'\n\s*\n\s*\n+', '\n\n', filtered)
	return filtered.strip()


def _call_ollama_generate(model: str, prompt: str, url: str = DEFAULT_OLLAMA_URL) -> str:
	"""Call Ollama API to generate response."""
	resp = requests.post(
		f"{url}/api/generate",
		json={"model": model, "prompt": prompt, "stream": False},
		timeout=250,
	)
	resp.raise_for_status()
	data = resp.json()
	response = data.get("response", "")
	return response


def _create_batches(papers: List[Paper], batch_size: int = 10) -> List[List[Paper]]:
	"""
	Split papers into batches of 10. If the last batch has 4 or fewer papers,
	merge it with the second-to-last batch.
	"""
	if len(papers) <= batch_size:
		return [papers]
	
	batches = []
	for i in range(0, len(papers), batch_size):
		batch = papers[i:i + batch_size]
		batches.append(batch)
	
	# Merge last batch if it has 4 or fewer papers
	if len(batches) > 1 and len(batches[-1]) <= 4:
		batches[-2].extend(batches[-1])
		batches.pop()
	
	return batches


def _rank_batch(batch_string: str, num: int, model: str = "qwen3", url: str = "http://127.0.0.1:11434") -> str:
	"""
	Rank papers using LLM and return plain text response.
	"""	
	# Format prompt with num parameter
	prompt = PROMPT.format(num=num)
	# print(prompt)
	user_prompt = f"{prompt}\n\nPapers:\n{batch_string}"

	# print(user_prompt.replace('\n', ''))
	try:
		raw = _call_ollama_generate(model=model, prompt=user_prompt, url=url).strip()
		click.echo(f"  LLM response: {raw}")
		# Filter out <think> blocks if present
		return _filter_think_blocks(raw)
		
	except Exception as e:
		click.echo(f"  LLM ranking failed: {e}")
		return ""


def tournament_rank_papers(papers: List[Paper], model: str = "qwen3", url: str = "http://127.0.0.1:11434") -> str:
	"""
	Two-level tournament ranking using configurable top-k values.
	First stage: rank batches, get text responses
	Second stage: rank all batch results, return final text

    TODO: might want to also preserve arxiv links/ids
	"""
	if not papers:
		return "No papers to rank."
	
	first_top_k, final_top_k = TOURNAMENT_TOPK
	
	
	click.echo(f"Starting tournament ranking with {len(papers)} papers...")
	click.echo(f"Tournament config: first_stage_top_k={first_top_k}, final_stage_top_k={final_top_k}")

	if len(papers) > final_top_k:
	
		# Step 1: Create batches and rank each batch
		batches = _create_batches(papers)
		click.echo(f"Created {len(batches)} batches: {[len(batch) for batch in batches]}")
		
		batch_results = []
		for i, batch in enumerate(batches):
			click.echo(f"Ranking batch {i+1}/{len(batches)} ({len(batch)} papers)...")
			str_batch = "\n".join([f"{paper.title}\n   {paper.abstract}" for paper in batch])
			batch_text = _rank_batch(str_batch, num=first_top_k, model=model, url=url)
			batch_results.append(batch_text)
			click.echo(f"  Completed batch {i+1}\n\n")
	
	else:
		batch_results = ["\n".join([f"{paper.title}\n   {paper.abstract}" for paper in papers])]
	
	click.echo(f"Final ranking of {len(batch_results)} batch results...")
	

    # Step 2: Final ranking of all batch results
	batch_results_string = "\n\n".join(batch_results)
	final_result = _rank_batch(batch_results_string, num=final_top_k, model=model, url=url)
	
	return (
		final_result +
		"\n\n\n\n### --------------- Ranked results for each batch: --------------------\n" +
		batch_results_string
	)

