from __future__ import annotations

import json
from typing import Iterable, List

import requests

from .models import Paper, ClassificationResult
from .config import OLLAMA_URL, CLASSIFICATION_MODEL, CLASSIFICATION_PROMPT


def _call_ollama_generate(model: str, prompt: str, url: str = OLLAMA_URL) -> str:
	resp = requests.post(
		f"{url}/api/generate",
		json={"model": model, "prompt": prompt, "stream": False},
		timeout=60,
	)
	resp.raise_for_status()
	data = resp.json()
	return data.get("response", "")


def classify_paper(paper: Paper, model: str = CLASSIFICATION_MODEL, url: str = OLLAMA_URL) -> ClassificationResult:
	user_prompt = (
		f"{CLASSIFICATION_PROMPT}\n\n"
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


def filter_interpretability(papers: Iterable[Paper], model: str = CLASSIFICATION_MODEL, url: str = OLLAMA_URL) -> List[Paper]:
	kept: List[Paper] = []
	for paper in papers:
		res = classify_paper(paper, model=model, url=url)
		if res.is_interpretability:
			kept.append(paper)
	return kept
