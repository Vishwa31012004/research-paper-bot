"""
app/main.py
------------
FastAPI application entry point. Day 3 version.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import papers
from app.config import APP_ENV, ENABLE_SUMMARIES

app = FastAPI(
    title="Research Paper Recommendation API",
    description=(
        "Search for top research papers with AI-generated summaries. "
        "Uses Semantic Scholar, arXiv, and HuggingFace BART model."
    ),
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://research-paper-bot.vercel.app",
    "https://research-paper-bot-git-main-vishwa31012004.vercel.app",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(papers.router, prefix="/api/papers", tags=["Papers"])


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "📚 Research Paper API v3.0 — Now with AI Summaries!",
        "docs": "http://localhost:8000/docs",
        "new_endpoints": {
            "search_with_summaries": "GET /api/papers/search?query=deep+learning&summarize=true",
            "summarize_single":      "POST /api/papers/summarize",
            "health":                "GET /api/papers/health",
        }
    }


@app.on_event("startup")
def startup():
    from app.config import SEMANTIC_SCHOLAR_API_KEY, HUGGINGFACE_API_TOKEN
    print("\n" + "="*55)
    print("🚀  Research Paper API v3.0 started!")
    print("📖  Docs: http://localhost:8000/docs")
    print(f"🔑  Semantic Scholar key : {'✅ set' if SEMANTIC_SCHOLAR_API_KEY else '❌ not set'}")
    print(f"🤗  HuggingFace token    : {'✅ set' if HUGGINGFACE_API_TOKEN else '❌ not set (extractive fallback active)'}")
    print(f"🤖  AI summaries         : {'✅ enabled' if ENABLE_SUMMARIES else '⏭️  disabled'}")
    print("="*55 + "\n")
