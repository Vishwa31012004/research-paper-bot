"""
app/services/semantic_scholar.py
----------------------------------
Fetches papers from Semantic Scholar API.
DAY 3: Now calls summarizer for each paper's abstract.
"""

import requests
from typing import List

from app.config import (
    SEMANTIC_SCHOLAR_BASE_URL,
    REQUEST_TIMEOUT,
    ENABLE_SUMMARIES,
    get_semantic_scholar_headers,
)
from app.models.paper import Paper
from app.services.summarizer import get_summary   # NEW in Day 3


REQUESTED_FIELDS = "title,authors,year,abstract,citationCount,externalIds,openAccessPdf"


def search_papers(query: str, limit: int = 10) -> List[Paper]:
    """
    Search Semantic Scholar and return papers with optional AI summaries.
    """

    url = f"{SEMANTIC_SCHOLAR_BASE_URL}/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": REQUESTED_FIELDS,
    }
    headers = get_semantic_scholar_headers()

    try:
        response = requests.get(url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.Timeout:
        raise Exception("Semantic Scholar API timed out.")
    except requests.exceptions.ConnectionError:
        raise Exception("Cannot connect to Semantic Scholar. Check your internet.")

    if response.status_code == 429:
        raise Exception(
            "Rate limited by Semantic Scholar (429). "
            "Add your API key to .env or wait 60 seconds."
        )
    if response.status_code == 401:
        raise Exception("Invalid Semantic Scholar API key.")
    if not response.ok:
        raise Exception(f"Semantic Scholar API error: HTTP {response.status_code}")

    data = response.json()
    raw_papers = data.get("data", [])

    papers = []
    for raw in raw_papers:
        paper = _parse_paper(raw)
        if paper.title:
            papers.append(paper)

    return papers


def _parse_paper(raw: dict) -> Paper:
    """Convert raw API dict to Paper object, with optional AI summary."""

    authors = [
        author.get("name", "Unknown")
        for author in raw.get("authors", [])
    ]

    # Build URL
    url = None
    open_access = raw.get("openAccessPdf")
    if open_access and isinstance(open_access, dict):
        url = open_access.get("url")
    if not url:
        external_ids = raw.get("externalIds") or {}
        doi = external_ids.get("DOI")
        if doi:
            url = f"https://doi.org/{doi}"
    if not url:
        external_ids = raw.get("externalIds") or {}
        arxiv_id = external_ids.get("ArXiv")
        if arxiv_id:
            url = f"https://arxiv.org/abs/{arxiv_id}"

    abstract = raw.get("abstract")

    # ── DAY 3: Generate AI summary ─────────────────────────────────────────
    # ENABLE_SUMMARIES is read from the .env file
    # If true, we call get_summary() for each paper
    # If false, ai_summary stays None (faster responses)
    ai_summary = None
    if ENABLE_SUMMARIES and abstract:
        print(f"🤖 Summarizing: {raw.get('title', '')[:50]}...")
        ai_summary = get_summary(abstract)
    # ──────────────────────────────────────────────────────────────────────

    return Paper(
        title=raw.get("title") or "Untitled",
        authors=authors,
        year=raw.get("year"),
        abstract=abstract,
        citation_count=raw.get("citationCount") or 0,
        url=url,
        source="semantic_scholar",
        ai_summary=ai_summary,   # NEW field
    )
