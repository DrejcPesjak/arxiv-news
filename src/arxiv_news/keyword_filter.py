from __future__ import annotations

from typing import Iterable, List

from .models import Paper
from .config import KEYWORD_LIST


def _text_matches_keywords(text: str) -> bool:
	if not text:
		return False
	for kw in KEYWORD_LIST:
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


