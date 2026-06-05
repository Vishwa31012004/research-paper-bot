"""
app/services/summarizer.py
---------------------------
Generates AI summaries of research paper abstracts.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HOW THIS WORKS (Big Picture)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Option A — Local model (NOT what we use):
  Your Computer → loads 400MB model → generates summary
  Problem: slow, uses lots of RAM, bad for beginners

Option B — HuggingFace Inference API (what we USE):
  Your Computer → HTTP request → HuggingFace servers → summary back
  Benefit: fast, no download, free tier available

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT IS HUGGINGFACE?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HuggingFace is like GitHub but for AI models.
  - Thousands of free, pre-trained AI models
  - Inference API = run models via HTTP without downloading them
  - Free tier: ~30,000 characters/month

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT IS BART (THE AI MODEL)?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BART = Bidirectional and Auto-Regressive Transformers
  - Created by Facebook AI Research in 2019
  - Trained on millions of news articles
  - Learned to compress long text into short summaries
  - Works by encoding the full text, then GENERATING a new
    shorter version — not just copying sentences

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT ARE TRANSFORMERS?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Transformers are the architecture behind modern AI (GPT, BERT, BART).
Key idea: "Attention" — the model learns which words are most
important relative to each other.

Example:
  "The cat sat on the mat because it was tired"
  The model learns: "it" refers to "cat" (not "mat")
  This understanding of context makes summaries accurate.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT ARE max_length AND min_length?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

These control the summary OUTPUT length in TOKENS.
A token ≈ 1 word (roughly).

  max_length=130 → summary will be AT MOST 130 words long
  min_length=30  → summary will be AT LEAST 30 words long

Why not just use characters?
  AI models work with tokens internally, not characters.
  Token = word piece. "unhappiness" = ["un", "happiness"] = 2 tokens.

Research papers need:
  max_length=150 → enough for a full summary sentence
  min_length=40  → prevents one-word summaries
"""

import requests   # For making HTTP calls to HuggingFace
import time       # For sleep() when we need to wait and retry
from typing import Optional

from app.config import (
    HUGGINGFACE_API_TOKEN,
    SUMMARIZATION_MODEL,
    SUMMARIZATION_MODEL_FAST,
    SUMMARY_TIMEOUT,
    SUMMARY_MAX_INPUT_LENGTH,
    get_huggingface_headers,
)


# ─────────────────────────────────────────────────────────────
# HuggingFace Inference API URL
# ─────────────────────────────────────────────────────────────
# URL format: https://api-inference.huggingface.co/models/<model_name>
# We just swap the model name to use a different model.
HF_API_URL = f"https://api-inference.huggingface.co/models/{SUMMARIZATION_MODEL}"
HF_API_URL_FAST = f"https://api-inference.huggingface.co/models/{SUMMARIZATION_MODEL_FAST}"


def summarize_abstract(abstract: str) -> Optional[str]:
    """
    Generates an AI summary of a research paper abstract.

    Parameters:
        abstract (str): The full abstract text of the paper

    Returns:
        Optional[str]: A short summary string, or None if summarization failed

    Why return None instead of raising an exception?
      Because a failed summary should NOT crash the whole paper search.
      We want: "Here are 10 papers, 8 with summaries, 2 without"
      Not:     "Error: summary failed" (shows nothing to user)

    Flow:
      1. Validate input (too short? skip)
      2. Truncate if too long
      3. Call HuggingFace API
      4. Handle "model loading" response (retry)
      5. Parse and return summary
    """

    # ── Step 1: Validate input ─────────────────────────────────────────────

    if not abstract:
        # No abstract = nothing to summarize
        return None

    if len(abstract) < 100:
        # Abstract too short — the AI summary would be the same length
        # Not worth calling the API
        return None

    # ── Step 2: Truncate long abstracts ────────────────────────────────────

    # SUMMARY_MAX_INPUT_LENGTH is set in config.py (default: 1000 characters)
    # Why truncate?
    #   - API has input limits
    #   - Longer input = slower response
    #   - First 1000 chars usually contain the key information
    input_text = abstract[:SUMMARY_MAX_INPUT_LENGTH]

    # ── Step 3: Build the API request ─────────────────────────────────────

    # What we send to HuggingFace (as JSON):
    # {
    #   "inputs": "The abstract text here...",
    #   "parameters": {
    #     "max_length": 150,    ← max output tokens
    #     "min_length": 40,     ← min output tokens
    #     "do_sample": false    ← deterministic output (same input = same output)
    #   }
    # }
    payload = {
        "inputs": input_text,
        "parameters": {
            "max_length": 150,
            # Maximum length of the generated summary in tokens.
            # 150 tokens ≈ 2-3 sentences. Good for paper summaries.

            "min_length": 40,
            # Minimum length. Prevents the model from being lazy
            # and returning a 5-word summary.

            "do_sample": False,
            # False = deterministic (greedy decoding)
            # Same abstract always gives same summary.
            # True = adds randomness (different each time, sometimes creative)

            "truncation": True,
            # If input is still too long after our truncation, truncate again.
            # Safety net.
        },
        "options": {
            "wait_for_model": True,
            # If the model isn't loaded yet on HuggingFace servers,
            # wait for it to load instead of returning an error.
            # First request after a long idle period may take 20-30 seconds.
        }
    }

    # ── Step 4: Call the HuggingFace Inference API ────────────────────────

    headers = get_huggingface_headers()
    # headers contains:
    #   "Content-Type": "application/json"
    #   "Authorization": "Bearer hf_your_token_here"  (if token is set)

    try:
        response = requests.post(
            HF_API_URL,
            # We use POST (not GET) because we're SENDING data (the abstract text)
            # GET requests have URL length limits — can't send long text in URL
            # POST puts data in the request BODY — no length limit

            headers=headers,
            json=payload,
            # json=payload automatically:
            #   1. Converts the Python dict to a JSON string
            #   2. Sets Content-Type header to application/json
            # Same as: data=json.dumps(payload)

            timeout=SUMMARY_TIMEOUT,
            # 60 seconds — HuggingFace sometimes needs time to load the model
        )

    except requests.exceptions.Timeout:
        print("⏱️  HuggingFace API timed out")
        return None

    except requests.exceptions.ConnectionError:
        print("🔌  Cannot connect to HuggingFace API")
        return None

    # ── Step 5: Handle the response ───────────────────────────────────────

    # HuggingFace response status codes:
    #   200 → success, summary is in the response body
    #   503 → model is loading, wait and retry
    #   401 → unauthorized (wrong or missing token)
    #   429 → rate limited (too many requests)

    if response.status_code == 503:
        # Model is still loading on HuggingFace servers.
        # This happens on the first request after the model has been idle.
        # Response body looks like: {"error": "Model ... is currently loading"}
        print("⏳  HuggingFace model is loading, retrying in 20 seconds...")
        time.sleep(20)  # Wait 20 seconds

        # Retry the request once
        try:
            response = requests.post(
                HF_API_URL,
                headers=headers,
                json=payload,
                timeout=SUMMARY_TIMEOUT,
            )
        except Exception:
            return None  # If retry also fails, give up gracefully

    if response.status_code == 401:
        print("🔑  HuggingFace API: Invalid or missing token")
        print("    Add HUGGINGFACE_API_TOKEN to your .env file")
        return None

    if response.status_code == 429:
        print("🚦  HuggingFace API: Rate limited")
        return None

    if not response.ok:
        print(f"❌  HuggingFace API error: {response.status_code} - {response.text[:200]}")
        return None

    # ── Step 6: Parse the JSON response ───────────────────────────────────

    # Successful HuggingFace response looks like:
    # [
    #   {
    #     "summary_text": "This paper proposes a novel deep learning approach..."
    #   }
    # ]
    #
    # It's a LIST with one dict inside.
    # Why a list? Because HuggingFace supports batch processing (multiple inputs).
    # We always send one input, so we get a list of one result.

    try:
        result = response.json()
        # result is now a Python list: [{"summary_text": "..."}]

        if isinstance(result, list) and len(result) > 0:
            # Get the first (and only) result
            summary = result[0].get("summary_text", "")

            if summary and len(summary) > 20:
                # Clean up the summary:
                # Sometimes the model adds extra spaces or newlines
                summary = summary.strip()
                return summary

    except Exception as e:
        print(f"⚠️  Failed to parse HuggingFace response: {e}")

    return None


def summarize_without_api(abstract: str) -> Optional[str]:
    """
    Fallback summarizer that works WITHOUT any API or AI model.

    This is used when:
      - No HuggingFace token is set
      - HuggingFace API is down
      - User wants instant results without waiting

    How it works:
      Extractive summarization — picks the FIRST 2 sentences of the abstract.
      Not AI-generated, but still useful as a quick preview.

    AI summarization (BART) = ABSTRACTIVE
      → generates NEW sentences that weren't in the original text
      → better quality, requires API

    Extractive summarization = picks EXISTING sentences from the text
      → lower quality but instant, no API needed
    """

    if not abstract or len(abstract) < 50:
        return None

    # Split the abstract into sentences
    # We split on ". " (period + space) to find sentence boundaries
    sentences = abstract.split(". ")

    if len(sentences) == 0:
        return None

    # Take the first 2 sentences as a summary
    # Research abstracts usually start with the most important information
    first_two = ". ".join(sentences[:2])

    # Add period back if it was stripped
    if not first_two.endswith("."):
        first_two += "."

    # Only return if it's meaningfully shorter than the full abstract
    if len(first_two) < len(abstract) * 0.7:
        return f"[Extracted] {first_two}"

    # If abstract is already short, return it as-is
    return abstract[:300] + "..." if len(abstract) > 300 else abstract


def get_summary(abstract: str, use_api: bool = True) -> Optional[str]:
    """
    Main function called by other services to get a summary.

    This is the ONLY function other files should import and call.
    It decides automatically:
      - Use HuggingFace API if token exists and use_api=True
      - Fall back to extractive summarizer if API fails or no token

    Parameters:
        abstract (str): The paper abstract
        use_api (bool): Whether to try the HuggingFace API

    Returns:
        Optional[str]: Summary string or None
    """

    if not abstract:
        return None

    # Try AI summarization if:
    #   1. use_api is True (caller wants AI)
    #   2. HuggingFace token is configured
    if use_api and HUGGINGFACE_API_TOKEN:
        ai_summary = summarize_abstract(abstract)
        if ai_summary:
            return ai_summary
        # If AI fails, fall through to extractive

    # Fallback: extractive summarizer (no API needed)
    return summarize_without_api(abstract)
