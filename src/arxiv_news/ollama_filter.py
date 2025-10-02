from __future__ import annotations

import json
from typing import Iterable, List

import requests

from .models import Paper, ClassificationResult


DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"

# _CLASSIFICATION_PROMPT = (
# 	"You are a precise research classifier. Given a paper title and abstract, "
# 	"answer ONLY with strict JSON: {\"reason\": string, \"is_interpretability\": boolean}. "
# 	"Mark is_interpretability=true if and only if the paper is about LLM interpretability, "
# 	"mechanistic interpretability, circuits, attribution, probing, representation analysis, "
# 	"or closely related interpretability methods and evaluations. Exclude general alignment, "
# 	"RLHF, safety, dataset curation, or purely application papers."
# )
# _CLASSIFICATION_PROMPT = (
# 	"You are a precise research classifier. Given a paper title and abstract, "
# 	"answer ONLY with strict JSON: {\"reason\": string, \"is_interpretability\": boolean}. "
# 	"Mark is_interpretability=true if and only if the paper is about Large Language Models (LLMs) and their interpretability."
# 	"If not, mark is_interpretability=false. And provide three sentence reason for your answer."
# )

_CLASSIFICATION_PROMPT = (
	"You are a precise research classifier. Given a paper title and abstract, "
	"answer ONLY with strict JSON: {\"reason\": string, \"is_interpretability\": boolean}. "
	"Mark is_interpretability=true if and only if the paper is about Large Language Models (LLMs) and their interpretability."
	"If not, mark is_interpretability=false. But first, give me three sentence reason for your answer under the reason field."
)


def _call_ollama_generate(model: str, prompt: str, url: str = DEFAULT_OLLAMA_URL) -> str:
	resp = requests.post(
		f"{url}/api/generate",
		json={"model": model, "prompt": prompt, "stream": False},
		timeout=60,
	)
	resp.raise_for_status()
	data = resp.json()
	return data.get("response", "")


def classify_paper(paper: Paper, model: str = "llama3.2", url: str = DEFAULT_OLLAMA_URL) -> ClassificationResult:
	user_prompt = (
		f"{_CLASSIFICATION_PROMPT}\n\n"
		f"Title: {paper.title}\n"
		f"Abstract: {paper.abstract}\n\n"
		"JSON:"
	)
	raw = _call_ollama_generate(model=model, prompt=user_prompt, url=url).strip()
	print(f"Title: {paper.title}\nURL: {paper.link}\nRaw Response: {raw}")
	# Try to extract JSON from response
	start = raw.find("{")
	end = raw.rfind("}")
	if start >= 0 and end > start:
		raw_json = raw[start : end + 1]
	else:
		raw_json = raw
	try:
		parsed = json.loads(raw_json)
		is_interpretability = bool(parsed.get("is_interpretability", False))
		reason = parsed.get("reason")
		return ClassificationResult(is_interpretability=is_interpretability, reason=reason)
	except Exception:
		# Fallback: conservative false if invalid response
		return ClassificationResult(is_interpretability=False, reason="Unparseable model output")


def filter_interpretability(papers: Iterable[Paper], model: str = "llama3.2", url: str = DEFAULT_OLLAMA_URL) -> List[Paper]:
	kept: List[Paper] = []
	for paper in papers:
		res = classify_paper(paper, model=model, url=url)
		if res.is_interpretability:
			kept.append(paper)
	return kept
