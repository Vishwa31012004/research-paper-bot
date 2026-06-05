/*
  src/App.js — Day 7
  -------------------
  NEW FEATURES:
    1. Export to CSV button
    2. 4 sources + "all" in dropdown
    3. searchQuery passed to PaperCard for highlighting
*/

import React, { useState, useEffect } from 'react';
import PaperCard from './components/PaperCard';
import { searchPapers, checkHealth } from './services/api';
import './App.css';

/* ── Skeleton card ─────────────────────────────────────────── */
function SkeletonCard() {
  return (
    <div className="skeleton-card">
      <div className="skeleton-line sk-title"></div>
      <div className="skeleton-line sk-meta"></div>
      <div className="skeleton-line sk-body"></div>
      <div className="skeleton-line sk-body"></div>
      <div className="skeleton-line sk-body"></div>
    </div>
  );
}

/* ── exportToCSV() ─────────────────────────────────────────── */
/*
  Converts the papers array to a CSV file and triggers download.

  HOW IT WORKS:
    1. Build a 2D array of rows (header + one row per paper)
    2. Escape any commas/quotes in cell values
    3. Join rows with newlines → CSV string
    4. Create a Blob (Binary Large Object) — like a file in memory
    5. Create a temporary <a> tag pointing to the Blob
    6. Programmatically click it → browser downloads the file
    7. Clean up the temporary URL

  WHY Blob?
    Browsers can't write files directly.
    Blob + URL.createObjectURL() = create a downloadable URL
    from in-memory data without a server.
*/
function exportToCSV(papers, query) {
  if (!papers || papers.length === 0) return;

  // CSV header row
  const headers = ['Title', 'Authors', 'Year', 'Citations', 'Source', 'URL', 'Abstract'];

  // Build rows — one per paper
  const rows = papers.map(p => [
    p.title || '',
    (p.authors || []).join('; '),   // Multiple authors separated by semicolon
    p.year || '',
    p.citation_count || 0,
    p.source || '',
    p.url || '',
    (p.abstract || '').replace(/\n/g, ' '), // Remove newlines from abstract
  ]);

  // Escape a CSV cell value
  // If value contains comma, quote, or newline → wrap in quotes
  // Double up any existing quotes (CSV standard)
  const escapeCell = (val) => {
    const str = String(val);
    if (str.includes(',') || str.includes('"') || str.includes('\n')) {
      return `"${str.replace(/"/g, '""')}"`;
    }
    return str;
  };

  // Build full CSV string
  const csvContent = [
    headers.map(escapeCell).join(','),       // Header row
    ...rows.map(row => row.map(escapeCell).join(','))  // Data rows
  ].join('\n');

  // Create Blob and download
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url  = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href     = url;
  link.download = `research-papers-${query.replace(/\s+/g, '-')}.csv`;
  // .download attribute sets the filename

  document.body.appendChild(link);
  link.click();                    // Trigger download
  document.body.removeChild(link); // Clean up
  URL.revokeObjectURL(url);        // Free memory
}


/* ── App ───────────────────────────────────────────────────── */
function App() {

  const [query,         setQuery]         = useState('');
  const [source,        setSource]        = useState('auto');
  const [summarize,     setSummarize]     = useState(true);
  const [papers,        setPapers]        = useState([]);
  const [loading,       setLoading]       = useState(false);
  const [error,         setError]         = useState(null);
  const [lastQuery,     setLastQuery]     = useState('');
  const [sourceUsed,    setSourceUsed]    = useState('');
  const [summariesOn,   setSummariesOn]   = useState(false);
  const [total,         setTotal]         = useState(0);
  const [hasSearched,   setHasSearched]   = useState(false);
  const [backendStatus, setBackendStatus] = useState(null);

  useEffect(() => {
    checkHealth()
      .then(h => setBackendStatus(h))
      .catch(() => setBackendStatus({ status: 'offline' }));
  }, []);

  const handleSearch = async (q, src, sum) => {
    const trimmed = (q || query).trim();
    if (trimmed.length < 2) return;

    setLoading(true);
    setError(null);
    setHasSearched(true);

    try {
      const data = await searchPapers(trimmed, 10, src || source, sum ?? summarize);
      setPapers(data.papers || []);
      setTotal(data.total || 0);
      setSourceUsed(data.source_used || src || source);
      setSummariesOn(data.summaries_enabled || false);
      setLastQuery(trimmed);
    } catch (err) {
      console.error('Search failed:', err);
      if (!err.response) {
        setError({ title: 'Cannot connect to backend',
                   detail: 'Run: uvicorn app.main:app --reload' });
      } else {
        setError({ title: 'Search failed',
                   detail: err.response?.data?.detail || err.message });
      }
      setPapers([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleSearch(query, source, summarize);
  };

  return (
    <div className="app">

      <div className="bg-ambient" aria-hidden="true">
        <div className="ambient-blob blob-gold-tr"></div>
        <div className="ambient-blob blob-teal-bl"></div>
        <div className="ambient-blob blob-gold-tc"></div>
      </div>

      {/* ── Header ── */}
      <header className="app-header">
        <div className="header-inner">
          <div className="brand">
            <div className="brand-mark" aria-hidden="true">⚗</div>
            <div>
              <div className="brand-name">Research Finder</div>
              <div className="brand-tagline">AI-powered paper discovery</div>
            </div>
          </div>
          {backendStatus && (
            <div className={`status-pill ${backendStatus.status === 'ok' ? 'online' : 'offline'}`}>
              <span className="status-dot"></span>
              {backendStatus.status === 'ok' ? 'Backend online' : 'Backend offline'}
            </div>
          )}
        </div>
      </header>

      {/* ── Main ── */}
      <main className="app-main">

        {/* Hero */}
        {!hasSearched && (
          <section className="hero">
            <div className="hero-eyebrow">
              <span className="eyebrow-dot"></span>
              4 Sources · AI Summaries · CSV Export
            </div>
            <h1 className="hero-heading">
              Find the papers<br />
              that <em>matter most</em>
            </h1>
            <p className="hero-sub">
              Search 500M+ academic papers across arXiv, Semantic Scholar,
              OpenAlex and PubMed. Get AI summaries and export to CSV.
            </p>
            <div className="chip-row">
              <span className="chip-label">Try:</span>
              {['medical image segmentation', 'large language models',
                'quantum computing', 'cancer detection'].map(ex => (
                <button key={ex} className="chip"
                        onClick={() => { setQuery(ex); handleSearch(ex, source, summarize); }}>
                  {ex}
                </button>
              ))}
            </div>
          </section>
        )}

        {/* ── Search form ── */}
        <section className="search-section">
          <form onSubmit={handleSubmit}>
            <div className="search-box">
              <span className="search-icon">🔍</span>
              <input type="text" className="search-input"
                     placeholder="e.g. transformer neural networks..."
                     value={query}
                     onChange={e => setQuery(e.target.value)}
                     disabled={loading} />
              <button type="submit" className="search-btn"
                      disabled={loading || query.trim().length < 2}>
                {loading ? <span className="btn-spinner"></span> : '🔍 Search'}
              </button>
            </div>

            <div className="search-options">
              <div className="opt-group">
                <label className="opt-label">Source</label>
                <select className="opt-select" value={source}
                        onChange={e => setSource(e.target.value)} disabled={loading}>
                  <option value="auto">Auto (smart fallback)</option>
                  <option value="all">All Sources (4 at once)</option>
                  <option value="semantic_scholar">Semantic Scholar</option>
                  <option value="arxiv">arXiv</option>
                  <option value="openalex">OpenAlex (250M+)</option>
                  <option value="pubmed">PubMed (medical)</option>
                </select>
              </div>

              <div className="opt-group toggle-wrap">
                <span className="opt-label">AI Summaries</span>
                <label className="toggle">
                  <input type="checkbox" checked={summarize}
                         onChange={e => setSummarize(e.target.checked)}
                         disabled={loading} />
                  <span className="toggle-track"></span>
                  <span className="toggle-thumb"></span>
                </label>
              </div>
            </div>
          </form>
        </section>

        {/* Error */}
        {error && (
          <div className="error-bar" role="alert">
            <span className="error-icon">⚠️</span>
            <div className="error-body">
              <div className="error-title">{error.title}</div>
              <div className="error-detail">{error.detail}</div>
            </div>
            <button className="error-close" onClick={() => setError(null)}>✕</button>
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="loading-view">
            <div className="loader-ring"></div>
            <p className="loader-text">Searching papers…</p>
            <p className="loader-sub">Fetching from {source === 'all' ? 'all 4 sources' : source}</p>
            <div className="skeleton-list" style={{ marginTop: 32 }}>
              {[0,1,2].map(i => <SkeletonCard key={i} />)}
            </div>
          </div>
        )}

        {/* Results */}
        {!loading && hasSearched && (
          <section className="results-section">
            {papers.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">🔎</div>
                <h2 className="empty-title">No papers found for "{lastQuery}"</h2>
                <p className="empty-sub">Try different keywords or switch to "All Sources".</p>
              </div>
            ) : (
              <>
                {/* Results bar with CSV export button */}
                <div className="results-bar">
                  <p className="results-count">
                    <strong>{total}</strong> papers for{' '}
                    <span className="results-query">"{lastQuery}"</span>
                  </p>
                  <div className="results-right">
                    <div className="results-tags">
                      <span className="tag tag-source">📡 {sourceUsed}</span>
                      {summariesOn && <span className="tag tag-summary">🤖 AI on</span>}
                    </div>

                    {/*
                      Export to CSV button.
                      Calls exportToCSV() with current papers and query.
                      Triggers an instant file download — no server needed!
                    */}
                    <button
                      className="btn-export"
                      onClick={() => exportToCSV(papers, lastQuery)}
                      title="Download results as CSV spreadsheet"
                    >
                      ⬇ Export CSV
                    </button>
                  </div>
                </div>

                {/* Paper cards — pass searchQuery for highlighting */}
                <div className="papers-list">
                  {papers.map((paper, i) => (
                    <PaperCard
                      key={`${paper.title}-${i}`}
                      paper={paper}
                      index={i}
                      searchQuery={lastQuery}
                      /*
                        searchQuery is passed so PaperCard can highlight
                        matching words in titles and abstracts.
                      */
                    />
                  ))}
                </div>
              </>
            )}
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <div className="footer-inner">
          <p className="footer-copy">© 2026 Research Finder · Built for learning</p>
          <div className="footer-stack">
            {['React', 'FastAPI', 'OpenAlex', 'PubMed', 'arXiv', 'BART'].map(t => (
              <span key={t} className="stack-pill">{t}</span>
            ))}
          </div>
        </div>
      </footer>

    </div>
  );
}

export default App;
