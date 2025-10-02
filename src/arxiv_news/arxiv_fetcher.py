from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Generator, Iterable, List, Optional

import arxiv

from .models import Paper


CATEGORY = "cs.AI"

def stream_recent_papers(days: int = 1, limit: Optional[int] = 200) -> Generator[Paper, None, None]:
	"""
	Yield recent papers in cs.AI as they are fetched. Always fetches a large number
	of results to ensure we get all papers within the date range, then applies 
	client-side date cutoff and sorting.
	
	If limit is None, returns all papers within the date range.
	If limit is specified, returns the newest N papers within the date range.
	"""
	now = datetime.now(timezone.utc)
	# Calculate the date 'days' ago, then set its time components to 00:00:00
	cutoff = (now - timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)

	# Always fetch a large number to ensure we get all papers in date range
	search = arxiv.Search(
		query=f"cat:{CATEGORY}",
		sort_by=arxiv.SortCriterion.SubmittedDate,
		sort_order=arxiv.SortOrder.Descending,  # Newest first
		max_results=10000,  # Large number to ensure we get all papers
	)

	client = arxiv.Client()
	papers_in_range = []
	
	try:
		for result in client.results(search):
			print(result.published, result.entry_id)
			if result.published is None:
				print("No published date")
				continue
				
			# Apply date cutoff - collect all papers within the date range
			if result.published >= cutoff:
				primary_pdf = result.pdf_url if result.pdf_url else None
				link = primary_pdf or result.entry_id
				paper = Paper(
					title=(result.title or "").strip(),
					link=link,
					abstract=(result.summary or "").strip(),
					published=result.published,
				)
				papers_in_range.append(paper)
			else:
				# Since results are sorted by submission date (newest first),
				# we can break when we hit papers older than our cutoff
				break
			
		# Sort by published date (newest first) to ensure proper ordering
		papers_in_range.sort(key=lambda p: p.published, reverse=True)
		
		# Apply limit if specified - take the newest papers
		if limit is not None:
			papers_in_range = papers_in_range[:limit]
			
		# Yield the sorted and optionally limited papers
		for paper in papers_in_range:
			yield paper
			
	except Exception:
		# Stop streaming on pagination/empty page or transient errors
		return


def fetch_recent_papers(days: int = 1, limit: Optional[int] = 200) -> List[Paper]:
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
