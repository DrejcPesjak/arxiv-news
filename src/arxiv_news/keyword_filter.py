from __future__ import annotations

from typing import Iterable, List

from .models import Paper


# Static keyword list for simple pre-filtering. Case-insensitive substring match.
_KEYWORDS: List[str] = [
	"LLM",
	" LLM ",
	" LLMs ",
	"Large Language Model",
	"interpretability",
	"VLM",
	"MLLM",
]


def _text_matches_keywords(text: str) -> bool:
	if not text:
		return False
	for kw in _KEYWORDS:
		if kw in text:
			return True
	return False


def is_keyword_match(paper: Paper) -> bool:
	"""
	Return True if any keyword appears in the title or abstract.
	"""
	return _text_matches_keywords(paper.title) or _text_matches_keywords(paper.abstract)


def filter_by_keywords(papers: Iterable[Paper]) -> List[Paper]:
	"""
	Filter papers by static keyword list, returning only those that match.
	"""
	kept: List[Paper] = []
	for paper in papers:
		if is_keyword_match(paper):
			kept.append(paper)
	return kept


