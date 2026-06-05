"""
app/config.py
--------------
Central configuration for the entire app.
All settings come from the .env file.

DAY 3 ADDITIONS:
  - HUGGINGFACE_API_TOKEN
  - ENABLE_SUMMARIES
  - SUMMARY_MAX_INPUT_LENGTH
  - HuggingFace model name
"""

import os
from dotenv import load_dotenv

load_dotenv()  # Read the .env file into environment variables

# ── Semantic Scholar ───────────────────────────────────────
SEMANTIC_SCHOLAR_API_KEY: str = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
SEMANTIC_SCHOLAR_BASE_URL: str = "https://api.semanticscholar.org/graph/v1"

# ── arXiv ──────────────────────────────────────────────────
ARXIV_BASE_URL: str = "https://export.arxiv.org/api/query"

# ── HuggingFace (NEW in Day 3) ─────────────────────────────
HUGGINGFACE_API_TOKEN: str = os.getenv("HUGGINGFACE_API_TOKEN", "")

# The summarization model we use on HuggingFace
# facebook/bart-large-cnn:
#   - BART = Bidirectional and Auto-Regressive Transformer
#   - Trained by Facebook AI on CNN/DailyMail news articles
#   - Excellent at summarizing long text into short paragraphs
#   - Free to use via HuggingFace Inference API
SUMMARIZATION_MODEL: str = "facebook/bart-large-cnn"

# Fallback model (smaller, faster, less accurate)
# Use this if bart-large-cnn is too slow
SUMMARIZATION_MODEL_FAST: str = "sshleifer/distilbart-cnn-12-6"

# ── Summarization Settings ─────────────────────────────────
# Convert string "true"/"false" from .env to Python bool
ENABLE_SUMMARIES: bool = os.getenv("ENABLE_SUMMARIES", "true").lower() == "true"

# How many characters of abstract to send for summarization
# More = better summary, but slower and uses more API quota
SUMMARY_MAX_INPUT_LENGTH: int = int(os.getenv("SUMMARY_MAX_INPUT_LENGTH", "1000"))

# ── HTTP Settings ──────────────────────────────────────────
REQUEST_TIMEOUT: int = 30   # seconds for Semantic Scholar / arXiv
SUMMARY_TIMEOUT: int = 60   # seconds for HuggingFace (model may need to load)

# ── App Settings ───────────────────────────────────────────
DEFAULT_RESULT_LIMIT: int = int(os.getenv("DEFAULT_RESULT_LIMIT", "10"))
MAX_RESULT_LIMIT: int = 20
APP_ENV: str = os.getenv("APP_ENV", "development")


def get_semantic_scholar_headers() -> dict:
    """HTTP headers for Semantic Scholar API requests."""
    headers = {
        "Accept": "application/json",
        "User-Agent": "ResearchPaperBot/3.0 (educational project)",
    }
    if SEMANTIC_SCHOLAR_API_KEY:
        headers["x-api-key"] = SEMANTIC_SCHOLAR_API_KEY
    return headers


def get_huggingface_headers() -> dict:
    """
    HTTP headers for HuggingFace Inference API requests.

    Authorization header format: "Bearer <token>"
    This is the standard way to send API tokens in HTTP headers.
    "Bearer" means "the holder of this token is authorized."
    """
    headers = {"Content-Type": "application/json"}
    if HUGGINGFACE_API_TOKEN:
        headers["Authorization"] = f"Bearer {HUGGINGFACE_API_TOKEN}"
    return headers
