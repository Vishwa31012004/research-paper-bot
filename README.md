# ⚗️ Research Finder — AI-Powered Academic Paper Discovery

![Version](https://img.shields.io/badge/version-1.0.0-gold)
![Backend](https://img.shields.io/badge/backend-FastAPI-009688)
![Frontend](https://img.shields.io/badge/frontend-React-61DAFB)
![License](https://img.shields.io/badge/license-MIT-blue)

> Search millions of academic papers from arXiv and Semantic Scholar.  
> Get AI-generated summaries powered by HuggingFace BART — completely free.

---

## 🖥️ Live Demo

| Service | URL |
|---------|-----|
| Frontend | `https://research-finder.vercel.app` *(after deployment)* |
| Backend API | `https://research-finder-api.onrender.com` *(after deployment)* |
| API Docs | `https://research-finder-api.onrender.com/docs` |

---

## ✨ Features

- 🔍 **Smart Search** — searches arXiv and Semantic Scholar simultaneously
- 🤖 **AI Summaries** — BART model generates concise paper summaries
- ⭐ **Citation Counts** — see how influential each paper is
- 📄 **Full Abstracts** — expandable abstract view per paper
- 🔄 **Auto Fallback** — if one API fails, switches to the other automatically
- 📱 **Responsive** — works on desktop, tablet, and mobile
- ⚡ **Fast** — results in under 3 seconds

---

## 🧱 Tech Stack

### Backend
| Technology | Purpose |
|-----------|---------|
| Python 3.11 | Programming language |
| FastAPI | Web framework — handles HTTP requests |
| Uvicorn | ASGI server — runs FastAPI |
| Requests | HTTP client — calls external APIs |
| Pydantic | Data validation |
| Python-dotenv | Environment variable management |

### Frontend
| Technology | Purpose |
|-----------|---------|
| React 18 | UI framework |
| Axios | HTTP client — calls our FastAPI |
| CSS3 | Styling — custom design system |
| Fraunces + Outfit | Typography |

### External APIs (all free)
| API | Purpose | Cost |
|----|---------|------|
| Semantic Scholar | 10M+ papers with citation counts | Free with API key |
| arXiv | Pre-print papers, no key needed | Always free |
| HuggingFace Inference | BART summarization model | Free tier |

---

## 📁 Project Structure

```
research-paper-bot/
│
├── backend/                          # FastAPI Python backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # App entry point, CORS, routes
│   │   ├── config.py                 # All settings from .env
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── paper.py              # Pydantic data models
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── semantic_scholar.py   # Semantic Scholar API logic
│   │   │   ├── arxiv_service.py      # arXiv API logic
│   │   │   └── summarizer.py        # HuggingFace BART summaries
│   │   └── routers/
│   │       ├── __init__.py
│   │       └── papers.py             # API endpoints
│   ├── .env                          # Secret keys (never commit this!)
│   ├── .env.example                  # Template for others to copy
│   └── requirements.txt              # Python dependencies
│
├── frontend/                         # React frontend
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js                    # Root component + state
│   │   ├── App.css                   # All styles
│   │   ├── index.js                  # React entry point
│   │   ├── components/
│   │   │   └── PaperCard.jsx         # Individual paper card
│   │   └── services/
│   │       └── api.js                # Axios API calls
│   └── package.json
│
├── .gitignore                        # Files to exclude from Git
└── README.md                         # This file
```

---

## 🚀 Local Development Setup

### Prerequisites
- Python 3.9+ → https://www.python.org/downloads/
- Node.js 18+ → https://nodejs.org/
- Git → https://git-scm.com/

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/research-paper-bot.git
cd research-paper-bot
```

### 2. Backend setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
copy .env.example .env     # Windows
cp .env.example .env       # Mac/Linux

# Add your API keys to .env (see API Keys section below)
```

### 3. Frontend setup
```bash
cd ../frontend
npm install
```

### 4. Run both servers

**Terminal 1 — Backend:**
```bash
cd backend
venv\Scripts\activate          # Windows
uvicorn app.main:app --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm start
```

Open http://localhost:3000 ✅

---

## 🔑 API Keys

All keys are **free** — no credit card required.

### Semantic Scholar API Key
1. Visit https://www.semanticscholar.org/product/api
2. Click "Get API Key" and fill out the form
3. Key arrives by email (usually within hours)
4. Add to `.env`: `SEMANTIC_SCHOLAR_API_KEY=your_key_here`

### HuggingFace API Token
1. Visit https://huggingface.co → Sign up free
2. Profile → Settings → Access Tokens
3. Click "New token" → name: `research-bot` → role: `read`
4. Add to `.env`: `HUGGINGFACE_API_TOKEN=hf_your_token_here`

---

## 🌐 Deployment Guide

### Deploy Backend → Render (Free)

Render gives you a free Python web service. Cold starts may take 30-60s.

**Step 1: Create `render.yaml` in your backend folder:**
```yaml
services:
  - type: web
    name: research-paper-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: SEMANTIC_SCHOLAR_API_KEY
        sync: false
      - key: HUGGINGFACE_API_TOKEN
        sync: false
      - key: ENABLE_SUMMARIES
        value: "true"
      - key: APP_ENV
        value: production
```

**Step 2: Push to GitHub (see GitHub section below)**

**Step 3: Deploy on Render**
1. Go to https://render.com → Sign up free with GitHub
2. Click "New +" → "Web Service"
3. Connect your GitHub repo
4. Set Root Directory to `backend`
5. Add environment variables (your API keys)
6. Click "Create Web Service"
7. Wait ~3 minutes for first deploy
8. Your API URL: `https://your-app-name.onrender.com`

**Step 4: Test your deployed API:**
```
https://your-app-name.onrender.com/docs
```

---

### Deploy Frontend → Vercel (Free)

Vercel is the best free host for React apps. Instant global CDN.

**Step 1: Create `.env.production` in your frontend folder:**
```
REACT_APP_API_URL=https://your-app-name.onrender.com
```

**Step 2: Deploy on Vercel**
1. Go to https://vercel.com → Sign up free with GitHub
2. Click "New Project"
3. Import your GitHub repository
4. Set Root Directory to `frontend`
5. Add environment variable:
   - Key: `REACT_APP_API_URL`
   - Value: `https://your-app-name.onrender.com`
6. Click "Deploy"
7. Your app URL: `https://your-app.vercel.app`

---

## 🔧 Production Configuration

### Update CORS in `backend/app/main.py`

When deploying, add your Vercel URL to the allowed origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",          # Local development
        "https://your-app.vercel.app",    # Your Vercel URL
        "https://research-finder.vercel.app",  # Custom if renamed
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Environment Variables Reference

| Variable | Required | Description |
|---------|---------|-------------|
| `SEMANTIC_SCHOLAR_API_KEY` | Recommended | Unlocks higher rate limits |
| `HUGGINGFACE_API_TOKEN` | Optional | Enables real AI summaries |
| `ENABLE_SUMMARIES` | Optional | `true`/`false` (default: true) |
| `DEFAULT_RESULT_LIMIT` | Optional | Papers per search (default: 10) |
| `APP_ENV` | Optional | `development`/`production` |

---

## 📤 GitHub Setup

### First time upload

```bash
# 1. Initialize Git in your project root
cd D:\research-paper-bot
git init

# 2. Add all files
git add .

# 3. First commit
git commit -m "Initial commit — Research Paper Bot v1.0"

# 4. Create repo on GitHub:
#    Go to github.com → New repository
#    Name: research-paper-bot
#    Public (for portfolio visibility)
#    DO NOT initialize with README (we have one)

# 5. Connect and push
git remote add origin https://github.com/YOUR_USERNAME/research-paper-bot.git
git branch -M main
git push -u origin main
```

### ⚠️ IMPORTANT: What NOT to push to GitHub

Your `.gitignore` file handles this automatically. Never commit:
- `.env` files (contain secret API keys)
- `venv/` folder (large, others recreate it with pip install)
- `node_modules/` folder (large, others recreate with npm install)

---

## 🐛 Common Errors & Fixes

### Backend Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `429 Too Many Requests` | Rate limited | Add API key to `.env` |
| `503 Service Unavailable` | API is down | Switch source to arXiv |
| `ModuleNotFoundError` | venv not activated | Run `venv\Scripts\activate` |
| `Port already in use` | Another server running | Use `--port 8001` |

### Frontend Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Cannot connect to backend` | FastAPI not running | Run `uvicorn app.main:app --reload` |
| `CORS error` | Origin not in allowed list | Add URL to CORS origins in `main.py` |
| `Module not found: axios` | npm install not run | Run `npm install` |
| `Blank page` | JS error | Open browser console (F12) for details |

### Deployment Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Build failed on Render` | Missing dependency | Check `requirements.txt` |
| `Cold start timeout` | Free tier sleeps | Wait 30-60s, then retry |
| `CORS error on Vercel` | Wrong origin in FastAPI | Add Vercel URL to `allow_origins` |
| `Env vars not found` | Not set on Render/Vercel | Add in platform dashboard |

---

## 📊 API Documentation

### `GET /api/papers/search`

Search for research papers.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | required | Search topic |
| `limit` | integer | 10 | Results count (1-20) |
| `source` | string | "auto" | `arxiv`, `semantic_scholar`, or `auto` |
| `summarize` | boolean | true | Include AI summaries |

**Example request:**
```
GET /api/papers/search?query=deep+learning&limit=5&source=arxiv
```

**Example response:**
```json
{
  "query": "deep learning",
  "total": 5,
  "source_used": "arxiv",
  "summaries_enabled": true,
  "papers": [
    {
      "title": "Deep Learning for Medical Imaging",
      "authors": ["Alice Smith", "Bob Jones"],
      "year": 2023,
      "abstract": "We propose a novel...",
      "citation_count": 142,
      "url": "https://arxiv.org/abs/2305.12345",
      "ai_summary": "This paper proposes a deep learning approach...",
      "source": "arxiv"
    }
  ]
}
```

### `POST /api/papers/summarize`

Summarize a single abstract on demand.

**Request body:**
```json
{ "abstract": "The full abstract text here..." }
```

**Response:**
```json
{
  "summary": "AI-generated summary...",
  "model_used": "facebook/bart-large-cnn",
  "input_length": 500,
  "summary_length": 120
}
```

### `GET /api/papers/health`

Check API health and configuration status.

---

## 🎯 How This Project Works — Architecture

```
User types query
       ↓
React (localhost:3000)
       ↓ axios GET /api/papers/search?query=...
FastAPI (localhost:8000)
       ↓
   Router (papers.py)
       ↓
   Service Layer
   ┌──────────────────────────┐
   │  semantic_scholar.py     │  → GET api.semanticscholar.org
   │  arxiv_service.py        │  → GET export.arxiv.org
   │  summarizer.py           │  → POST api-inference.huggingface.co
   └──────────────────────────┘
       ↓
   Pydantic validates data
       ↓
   JSON response
       ↓
React renders paper cards
```

---

## 💼 Resume Description

Use this in your resume under Projects:

> **Research Finder — AI Academic Paper Discovery Tool** | React · FastAPI · Python  
> Built a full-stack web application that searches 200M+ academic papers using Semantic Scholar and arXiv APIs. Integrated HuggingFace BART transformer model to generate AI summaries of paper abstracts. Implemented async FastAPI backend with smart fallback logic, modular service architecture, and production CORS configuration. Deployed frontend on Vercel and backend on Render with environment-based configuration.

---

## 🎤 Interview Talking Points

**"Tell me about this project"**
> "I built a full-stack research paper finder. The React frontend lets users search academic papers by topic. The FastAPI backend calls Semantic Scholar and arXiv APIs to fetch papers, and uses the HuggingFace BART model to generate AI summaries of abstracts. The system has a smart fallback — if Semantic Scholar rate-limits us, it automatically switches to arXiv."

**"What was the hardest part?"**
> "Handling API rate limiting gracefully. Semantic Scholar has strict rate limits, so I built an automatic fallback system that tries Semantic Scholar first and silently switches to arXiv if it fails — the user never sees an error."

**"What would you add next?"**
> "User authentication to save favourite papers, filtering by year/citation count, and a recommendation engine that suggests related papers based on reading history."

**"Why FastAPI over Flask or Django?"**
> "FastAPI gives you automatic API documentation, built-in data validation with Pydantic, and async support. For this use case it was perfect — less boilerplate than Django and better performance than Flask."

---

## 🗓️ Project Timeline (Built in 5 Days)

| Day | What Was Built |
|-----|---------------|
| Day 1 | FastAPI project structure, virtual environment, first endpoints |
| Day 2 | Semantic Scholar + arXiv API integration, requests library |
| Day 3 | HuggingFace BART summarization, .env configuration |
| Day 4 | React frontend, Axios, component architecture |
| Day 5 | Professional UI redesign, skeleton loading, animations |
| Day 6 | Deployment, GitHub, documentation |

---

## 📝 License

MIT License — free to use, modify, and distribute.

---

## 🙏 Acknowledgements

- [Semantic Scholar](https://www.semanticscholar.org/) — academic paper API
- [arXiv](https://arxiv.org/) — open access pre-prints
- [HuggingFace](https://huggingface.co/) — BART summarization model
- [Render](https://render.com/) — free backend hosting
- [Vercel](https://vercel.com/) — free frontend hosting
