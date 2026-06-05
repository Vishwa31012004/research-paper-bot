"""
app/routers/papers.py — Day 7
Now supports: semantic_scholar, arxiv, openalex, pubmed, auto, all
"""
from fastapi import APIRouter, HTTPException, Query
from app.models.paper import SearchResponse, SummaryRequest
from app.services import semantic_scholar, arxiv_service, openalex, pubmed
from app.services.summarizer import get_summary
from app.config import DEFAULT_RESULT_LIMIT, MAX_RESULT_LIMIT, ENABLE_SUMMARIES
from concurrent.futures import ThreadPoolExecutor

router = APIRouter()

def _run_source(fn, query, limit):
    try:
        return fn(query, limit)
    except Exception as e:
        print(f"⚠️  {fn.__module__} failed: {e}")
        return []

@router.get("/search", response_model=SearchResponse)
def search_papers(
    query: str = Query(..., min_length=2, max_length=200),
    limit: int = Query(default=DEFAULT_RESULT_LIMIT, ge=1, le=MAX_RESULT_LIMIT),
    source: str = Query(default="auto",
        description="semantic_scholar | arxiv | openalex | pubmed | auto | all"),
    summarize: bool = Query(default=True),
):
    import app.config as cfg
    original = cfg.ENABLE_SUMMARIES
    cfg.ENABLE_SUMMARIES = ENABLE_SUMMARIES and summarize
    papers = []
    source_used = source

    try:
        source_map = {
            "semantic_scholar": semantic_scholar.search_papers,
            "arxiv":            arxiv_service.search_papers,
            "openalex":         openalex.search_papers,
            "pubmed":           pubmed.search_papers,
        }

        if source in source_map:
            try:
                papers = source_map[source](query, limit)
                source_used = source
            except Exception as e:
                raise HTTPException(status_code=503, detail=str(e))

        elif source == "auto":
            for name, fn in source_map.items():
                try:
                    papers = fn(query, limit)
                    source_used = name
                    if papers:
                        break
                except Exception as e:
                    print(f"⚠️  {name} failed: {e}")
                    continue
            if not papers:
                raise HTTPException(status_code=503, detail="All sources failed.")

        elif source == "all":
            per_source = max(3, limit // 2)
            with ThreadPoolExecutor(max_workers=4) as ex:
                futures = {name: ex.submit(_run_source, fn, query, per_source)
                           for name, fn in source_map.items()}
                for result in [f.result() for f in futures.values()]:
                    papers.extend(result)

            # Deduplicate by title
            seen, unique = set(), []
            for p in papers:
                key = p.title.lower()[:60].strip()
                if key not in seen:
                    seen.add(key)
                    unique.append(p)
            papers = unique
            source_used = "all sources"

        else:
            raise HTTPException(status_code=400,
                detail=f"Invalid source. Options: {list(source_map.keys())} + auto + all")

    finally:
        cfg.ENABLE_SUMMARIES = original

    papers.sort(key=lambda p: p.citation_count or 0, reverse=True)
    return SearchResponse(query=query, total=len(papers), papers=papers,
                         source_used=source_used,
                         summaries_enabled=cfg.ENABLE_SUMMARIES and summarize)


@router.post("/summarize")
def summarize_paper(request: SummaryRequest):
    if not request.abstract or len(request.abstract.strip()) < 50:
        raise HTTPException(status_code=400, detail="Abstract too short.")
    summary = get_summary(request.abstract)
    if not summary:
        raise HTTPException(status_code=503, detail="Could not generate summary.")
    return {"summary": summary, "model_used": "facebook/bart-large-cnn"}


@router.get("/health")
def health_check():
    from app.config import SEMANTIC_SCHOLAR_API_KEY, HUGGINGFACE_API_TOKEN
    return {
        "status": "ok",
        "sources_available": ["semantic_scholar", "arxiv", "openalex", "pubmed"],
        "services": {
            "semantic_scholar_key": bool(SEMANTIC_SCHOLAR_API_KEY),
            "huggingface_token": bool(HUGGINGFACE_API_TOKEN),
            "summaries_enabled": ENABLE_SUMMARIES,
        }
    }
