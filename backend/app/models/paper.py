"""
app/models/paper.py
--------------------
Data models for research papers.

DAY 3 ADDITION:
  - ai_summary field added to Paper model
  - SummaryRequest model for the summarize endpoint
"""

from pydantic import BaseModel
from typing import List, Optional


class Paper(BaseModel):
    """
    Represents one research paper.

    DAY 3: Added ai_summary field.
    This field is Optional because:
      - Summaries are only generated when ENABLE_SUMMARIES=true
      - Papers with no abstract cannot be summarized
      - If HuggingFace API fails, we still return the paper (without summary)
    """

    title: str
    authors: List[str]
    year: Optional[int] = None
    abstract: Optional[str] = None
    citation_count: Optional[int] = 0
    url: Optional[str] = None
    source: str = "unknown"

    # NEW in Day 3 ↓
    ai_summary: Optional[str] = None
    # AI-generated short summary of the abstract.
    # None means: summary was not generated (disabled or failed).
    # Example value: "This paper proposes a deep learning approach for
    #                 medical image analysis, achieving 94% accuracy on
    #                 benchmark datasets."


class SearchResponse(BaseModel):
    """Full API response sent to the frontend."""

    query: str
    total: int
    papers: List[Paper]
    source_used: str = "unknown"
    summaries_enabled: bool = False  # NEW: tells frontend if summaries are included


class ErrorResponse(BaseModel):
    """Standard error response shape."""
    error: str
    message: str
    suggestion: str


class SummaryRequest(BaseModel):
    """
    NEW in Day 3: Request body for the /summarize endpoint.

    This is used when the frontend wants to summarize a SINGLE abstract
    on demand (e.g., when user clicks "Summarize" button).
    """
    abstract: str   # The abstract text to summarize
