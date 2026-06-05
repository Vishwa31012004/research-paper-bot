"""
app/services/arxiv_service.py
------------------------------
Fetches papers from arXiv API.
DAY 3: Now generates AI summaries for each paper.
"""

import requests
import xml.etree.ElementTree as ET
from typing import List

from app.config import ARXIV_BASE_URL, REQUEST_TIMEOUT, ENABLE_SUMMARIES
from app.models.paper import Paper
from app.services.summarizer import get_summary   # NEW in Day 3

NAMESPACE = "http://www.w3.org/2005/Atom"


def search_papers(query: str, limit: int = 10) -> List[Paper]:
    """Search arXiv and return papers with optional AI summaries."""

    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": limit,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }

    try:
        response = requests.get(
            ARXIV_BASE_URL,
            params=params,
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": "ResearchPaperBot/3.0"},
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise Exception("arXiv API timed out.")
    except requests.exceptions.ConnectionError:
        raise Exception("Cannot connect to arXiv.")
    except requests.exceptions.HTTPError as e:
        raise Exception(f"arXiv API error: {e}")

    root = ET.fromstring(response.text)
    entries = root.findall(f"{{{NAMESPACE}}}entry")

    papers = []
    for entry in entries:
        paper = _parse_entry(entry)
        if paper.title and paper.title != "Untitled":
            papers.append(paper)

    return papers


def _parse_entry(entry: ET.Element) -> Paper:
    """Convert XML entry to Paper object with optional AI summary."""

    def get_text(tag):
        el = entry.find(f"{{{NAMESPACE}}}{tag}")
        return el.text.strip() if el is not None and el.text else ""

    title = get_text("title")

    author_elements = entry.findall(f"{{{NAMESPACE}}}author")
    authors = []
    for a in author_elements:
        name_el = a.find(f"{{{NAMESPACE}}}name")
        if name_el is not None and name_el.text:
            authors.append(name_el.text.strip())

    published = get_text("published")
    year = int(published[:4]) if published and len(published) >= 4 else None

    abstract = get_text("summary")
    url = get_text("id")

    # ── DAY 3: Generate AI summary ─────────────────────────────────────────
    ai_summary = None
    if ENABLE_SUMMARIES and abstract:
        print(f"🤖 Summarizing: {title[:50]}...")
        ai_summary = get_summary(abstract)
    # ──────────────────────────────────────────────────────────────────────

    return Paper(
        title=title or "Untitled",
        authors=authors,
        year=year,
        abstract=abstract,
        citation_count=0,
        url=url,
        source="arxiv",
        ai_summary=ai_summary,   # NEW field
    )
