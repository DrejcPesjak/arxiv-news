from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Generator, Iterable, List, Optional

import arxiv

from .models import Paper


CATEGORY = "cs.AI"

def stream_recent_papers(days: int = 1, limit: int = 200) -> Generator[Paper, None, None]:
	"""
	Yield recent papers in cs.AI as they are fetched. Applies client-side cutoff by
	`days`. This function is resilient to occasional empty page errors from the
	arXiv API by stopping iteration gracefully.
	"""
	now = datetime.now(timezone.utc)
	cutoff = now - timedelta(days=days)

	search = arxiv.Search(
		query=f"cat:{CATEGORY}",
		sort_by=arxiv.SortCriterion.SubmittedDate,
		max_results=limit,
	)

	client = arxiv.Client()
	try:
		for result in client.results(search):
			if result.published is None or result.published < cutoff:
				continue
			primary_pdf = result.pdf_url if result.pdf_url else None
			link = primary_pdf or result.entry_id
			yield Paper(
				title=(result.title or "").strip(),
				link=link,
				abstract=(result.summary or "").strip(),
				published=result.published,
			)
	except Exception:
		# Stop streaming on pagination/empty page or transient errors
		return


def fetch_recent_papers(days: int = 1, limit: int = 200) -> List[Paper]:
	"""
	Collect recent papers into a list. See `stream_recent_papers` for streaming.
	"""
	return list(stream_recent_papers(days=days, limit=limit))


def fetch_paper_by_id(arxiv_id: str) -> Optional[Paper]:
	"""
	Fetch a single paper by its arXiv ID (e.g., "2509.00698"). Returns None if not found.
	"""
	client = arxiv.Client()
	try:
		search = arxiv.Search(id_list=[arxiv_id])
		for result in client.results(search):
			primary_pdf = result.pdf_url if result.pdf_url else None
			link = primary_pdf or result.entry_id
			return Paper(
				title=(result.title or "").strip(),
				link=link,
				abstract=(result.summary or "").strip(),
				published=result.published or datetime.now(timezone.utc),
			)
		return None
	except Exception:
		return None
