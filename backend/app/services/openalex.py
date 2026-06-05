"""
app/services/openalex.py
-------------------------
Fetches papers from OpenAlex API (250M+ papers, completely free).
"""

import requests
from typing import List
from app.config import REQUEST_TIMEOUT, ENABLE_SUMMARIES
from app.models.paper import Paper
from app.services.summarizer import get_summary

OPENALEX_BASE_URL = "https://api.openalex.org/works"
OPENALEX_EMAIL = "research-bot@example.com"


def search_papers(query: str, limit: int = 10) -> List[Paper]:
    params = {
        "search": query,
        "per-page": limit,
        "select": "id,title,authorships,publication_year,abstract_inverted_index,cited_by_count,doi,primary_location",
        "sort": "cited_by_count:desc",
        "mailto": OPENALEX_EMAIL,
    }
    try:
        response = requests.get(OPENALEX_BASE_URL, params=params,
                                timeout=REQUEST_TIMEOUT,
                                headers={"User-Agent": "ResearchPaperBot/1.0"})
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise Exception("OpenAlex API timed out.")
    except requests.exceptions.ConnectionError:
        raise Exception("Cannot connect to OpenAlex.")
    except requests.exceptions.HTTPError as e:
        raise Exception(f"OpenAlex error: {e}")

    data = response.json()
    raw_papers = data.get("results", [])
    papers = []
    for raw in raw_papers:
        paper = _parse_paper(raw)
        if paper.title:
            papers.append(paper)
    return papers


def _reconstruct_abstract(inverted_index: dict) -> str:
    """
    OpenAlex stores abstracts as inverted index:
    {"word": [position1, position2], ...}
    We reverse it back to readable text.
    """
    if not inverted_index:
        return None
    try:
        max_pos = max(pos for positions in inverted_index.values() for pos in positions)
        words = [""] * (max_pos + 1)
        for word, positions in inverted_index.items():
            for pos in positions:
                words[pos] = word
        abstract = " ".join(words).strip()
        return abstract if abstract else None
    except Exception:
        return None


def _parse_paper(raw: dict) -> Paper:
    title = raw.get("title") or "Untitled"
    authorships = raw.get("authorships", [])
    authors = [a.get("author", {}).get("display_name", "Unknown") for a in authorships]
    year = raw.get("publication_year")
    citation_count = raw.get("cited_by_count", 0)
    doi = raw.get("doi")
    url = doi if doi else None
    if not url:
        primary = raw.get("primary_location") or {}
        url = primary.get("landing_page_url")
    abstract = _reconstruct_abstract(raw.get("abstract_inverted_index"))
    ai_summary = None
    if ENABLE_SUMMARIES and abstract:
        print(f"🤖 Summarizing (OpenAlex): {title[:50]}...")
        ai_summary = get_summary(abstract)
    return Paper(title=title, authors=authors, year=year, abstract=abstract,
                 citation_count=citation_count, url=url, source="openalex",
                 ai_summary=ai_summary)
