"""
app/services/pubmed.py
-----------------------
Fetches papers from PubMed API (medical/biology papers).

What is PubMed?
  - Run by the US National Library of Medicine
  - 35 million+ biomedical papers
  - Best source for medical, biology, clinical research
  - Free, no API key needed
  - API: E-utilities (NCBI Entrez)
"""

import requests
import xml.etree.ElementTree as ET
from typing import List
from app.config import REQUEST_TIMEOUT, ENABLE_SUMMARIES
from app.models.paper import Paper
from app.services.summarizer import get_summary

# Step 1: Search returns IDs
PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
# Step 2: Fetch details for those IDs
PUBMED_FETCH_URL  = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

TOOL_NAME  = "ResearchPaperBot"
TOOL_EMAIL = "research-bot@example.com"


def search_papers(query: str, limit: int = 10) -> List[Paper]:
    """
    PubMed search requires TWO API calls:
    1. esearch → get list of paper IDs matching the query
    2. efetch  → get full details for those IDs
    """

    # ── Step 1: Get paper IDs ──────────────────────────────────
    search_params = {
        "db": "pubmed",        # Search PubMed database
        "term": query,         # Search term
        "retmax": limit,       # Max results
        "retmode": "json",     # Return JSON
        "sort": "relevance",   # Sort by relevance
        "tool": TOOL_NAME,
        "email": TOOL_EMAIL,
    }

    try:
        search_resp = requests.get(PUBMED_SEARCH_URL, params=search_params,
                                   timeout=REQUEST_TIMEOUT)
        search_resp.raise_for_status()
    except requests.exceptions.Timeout:
        raise Exception("PubMed search timed out.")
    except requests.exceptions.ConnectionError:
        raise Exception("Cannot connect to PubMed.")

    search_data = search_resp.json()
    ids = search_data.get("esearchresult", {}).get("idlist", [])

    if not ids:
        return []

    # ── Step 2: Fetch paper details ───────────────────────────
    fetch_params = {
        "db": "pubmed",
        "id": ",".join(ids),   # Comma-separated IDs
        "retmode": "xml",      # PubMed detail returns XML
        "rettype": "abstract",
        "tool": TOOL_NAME,
        "email": TOOL_EMAIL,
    }

    try:
        fetch_resp = requests.get(PUBMED_FETCH_URL, params=fetch_params,
                                  timeout=REQUEST_TIMEOUT)
        fetch_resp.raise_for_status()
    except Exception as e:
        raise Exception(f"PubMed fetch error: {e}")

    return _parse_xml(fetch_resp.text)


def _parse_xml(xml_text: str) -> List[Paper]:
    """Parse PubMed XML response into Paper objects."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []

    papers = []
    for article in root.findall(".//PubmedArticle"):
        paper = _parse_article(article)
        if paper and paper.title:
            papers.append(paper)
    return papers


def _parse_article(article: ET.Element) -> Paper:
    """Convert one PubMed XML article to a Paper object."""

    def find_text(path: str) -> str:
        el = article.find(path)
        return el.text.strip() if el is not None and el.text else ""

    # Title
    title = find_text(".//ArticleTitle")

    # Authors
    authors = []
    for author in article.findall(".//Author"):
        last  = find_text(".//LastName") if author.find("LastName") is not None else ""
        first = find_text(".//ForeName") if author.find("ForeName") is not None else ""
        last_el  = author.find("LastName")
        first_el = author.find("ForeName")
        last  = last_el.text.strip()  if last_el  is not None and last_el.text  else ""
        first = first_el.text.strip() if first_el is not None and first_el.text else ""
        if last:
            authors.append(f"{first} {last}".strip())

    # Year
    year = None
    year_el = article.find(".//PubDate/Year")
    if year_el is not None and year_el.text:
        try:
            year = int(year_el.text)
        except ValueError:
            pass

    # Abstract — join multiple sections
    abstract_parts = []
    for ab in article.findall(".//AbstractText"):
        if ab.text:
            label = ab.get("Label", "")
            text = ab.text.strip()
            if label:
                abstract_parts.append(f"{label}: {text}")
            else:
                abstract_parts.append(text)
    abstract = " ".join(abstract_parts) if abstract_parts else None

    # PubMed URL using PMID
    pmid_el = article.find(".//PMID")
    url = None
    if pmid_el is not None and pmid_el.text:
        url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid_el.text.strip()}/"

    ai_summary = None
    if ENABLE_SUMMARIES and abstract:
        print(f"🤖 Summarizing (PubMed): {title[:50]}...")
        ai_summary = get_summary(abstract)

    return Paper(title=title or "Untitled", authors=authors, year=year,
                 abstract=abstract, citation_count=0, url=url,
                 source="pubmed", ai_summary=ai_summary)
