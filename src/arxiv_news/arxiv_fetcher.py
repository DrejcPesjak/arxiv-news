from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Generator, Iterable, List, Optional

import arxiv

from .models import Paper
from .config import ARXIV_CATEGORY

def stream_recent_papers(days: int = 1, limit: Optional[int] = None) -> Generator[Paper, None, None]:
	"""
	Yield recent papers in the configured arXiv category as they are fetched. Fetches ALL results from the API
	to ensure we get all papers within the date range, then applies client-side date 
	cutoff and sorting.
	
	If limit is None, returns all papers within the date range.
	If limit is specified, returns the newest N papers within the date range.
	"""
	now = datetime.now(timezone.utc)
	# Calculate the date 'days' ago, then set its time components to 00:00:00
	cutoff = (now - timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)
	print(f"Cutoff: {cutoff}")
	print(f"Limit: {limit if limit is not None else 'No limit (fetching all papers in date range)'}")

	# Set max_results to None to fetch ALL results from the API
	# The arxiv library will handle pagination automatically
	search = arxiv.Search(
		query=f"cat:{ARXIV_CATEGORY}",
		sort_by=arxiv.SortCriterion.SubmittedDate,
		sort_order=arxiv.SortOrder.Descending,  # Newest first
		max_results=None,  # Fetch ALL results - library handles pagination
	)

	# Configure client with more aggressive settings to handle large result sets
	# page_size controls how many results per API call (max is 2000 for arXiv API)
	client = arxiv.Client(
		num_retries=5, 
		delay_seconds=3,
		page_size=2000  # Use maximum page size to minimize API calls
	)
	papers_in_range = []
	
	print(f"Starting to fetch papers from arXiv API...")
	fetched_count = 0

	try:
		for result in client.results(search):
			fetched_count += 1
			if fetched_count % 100 == 0:
				print(f"Fetched {fetched_count} papers so far...")
			
			if result.published is None:
				print("No published date")
				continue
			
			# Apply date cutoff - collect all papers within the date range
			if result.published >= cutoff:
				try:
					primary_pdf = result.pdf_url if result.pdf_url else None
					link = primary_pdf or result.entry_id
					paper = Paper(
						title=(result.title or "").strip(),
						link=link,
						abstract=(result.summary or "").strip(),
						published=result.published,
					)
					papers_in_range.append(paper)

				except Exception as e:
					print(f"Error processing paper: {e}")
					# Skip items that fail validation or parsing, continue with others
					continue
			else:
				# Since results are sorted by submission date (newest first),
				# we can break when we hit papers older than our cutoff
				print(f"Reached papers older than cutoff after fetching {fetched_count} total papers")
				break
			
	except Exception as e:
		print(f"Error fetching papers: {e}")
		# arxiv library can raise UnexpectedEmptyPageError intermittently; keep collected items
		pass
	
	print(f"Total papers within date range: {len(papers_in_range)}")

	# Sort by published date (newest first) to ensure proper ordering
	papers_in_range.sort(key=lambda p: p.published, reverse=True)

	# Apply limit if specified - take the newest papers
	if limit is not None:
		papers_in_range = papers_in_range[:limit]

	# Yield the sorted and optionally limited papers
	for paper in papers_in_range:
		yield paper


def fetch_recent_papers(days: int = 1, limit: Optional[int] = None) -> List[Paper]:
	"""
	Collect recent papers into a list. See `stream_recent_papers` for streaming.
	
	If limit is None, returns all papers within the date range.
	If limit is specified, returns the newest N papers within the date range.
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
