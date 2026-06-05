/*
  src/components/PaperCard.jsx — Day 7
  --------------------------------------
  NEW FEATURES:
    1. Keyword highlighting — search term glows in abstract
    2. Copy citation button — formats APA citation to clipboard
    3. Reading time estimate — "~3 min read"
    4. Source badge colors for all 4 sources
*/

import React, { useState } from 'react';
import { summarizePaper } from '../services/api';

/*
  highlightText()
  ───────────────
  Splits text around the search query and wraps matches in <mark> tags.

  How it works:
    Input:  "Deep learning is great", query="learning"
    Output: ["Deep ", <mark>learning</mark>, " is great"]

  We use RegExp to find all matches (case-insensitive):
    new RegExp(`(${query})`, 'gi')
    g = global (find ALL matches, not just first)
    i = case-insensitive

  .split() with a capturing group keeps the matched text in the array.
  Example: "hello world".split(/(world)/) = ["hello ", "world", ""]

  We then .map() over the parts:
    - If part matches query → wrap in <mark>
    - Otherwise → plain text
*/
function highlightText(text, query) {
  if (!text || !query || query.trim().length < 2) return text;

  try {
    // Escape special regex characters in query
    // (prevents errors if user types "c++" or "a.b")
    const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(${escaped})`, 'gi');
    const parts = text.split(regex);

    return parts.map((part, i) =>
      regex.test(part)
        ? <mark key={i} className="highlight">{part}</mark>
        : part
    );
  } catch {
    return text; // If regex fails, return plain text
  }
}


/*
  formatAPA()
  ───────────
  Generates an APA-format citation string from a Paper object.

  APA format:
    Author, A., & Author, B. (Year). Title. Source. URL

  Examples:
    He, K., Zhang, X., Ren, S., & Sun, J. (2016).
    Deep Residual Learning for Image Recognition.
    Semantic Scholar. https://doi.org/10.1109/cvpr.2016.90
*/
function formatAPA(paper) {
  // Format authors: "Last, F., & Last, F."
  const formatAuthor = (name) => {
    const parts = name.trim().split(' ');
    if (parts.length === 1) return parts[0];
    const last  = parts[parts.length - 1];
    const first = parts.slice(0, -1).map(p => p[0] + '.').join(' ');
    return `${last}, ${first}`;
  };

  let authors = '';
  if (paper.authors && paper.authors.length > 0) {
    const formatted = paper.authors.slice(0, 6).map(formatAuthor);
    if (paper.authors.length > 6) {
      formatted.push('et al.');
    }
    if (formatted.length === 1) {
      authors = formatted[0];
    } else {
      authors = formatted.slice(0, -1).join(', ') + ', & ' + formatted[formatted.length - 1];
    }
  }

  const year   = paper.year ? `(${paper.year})` : '(n.d.)';
  const title  = paper.title || 'Untitled';
  const source = paper.source
    ? paper.source.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())
    : 'Unknown Source';
  const url    = paper.url ? ` ${paper.url}` : '';

  return `${authors} ${year}. ${title}. ${source}.${url}`;
}


/*
  estimateReadingTime()
  ─────────────────────
  Estimates how long it takes to read the abstract.
  Average reading speed = 200 words per minute.
*/
function estimateReadingTime(text) {
  if (!text) return null;
  const words = text.trim().split(/\s+/).length;
  const minutes = Math.ceil(words / 200);
  return minutes <= 1 ? '~1 min read' : `~${minutes} min read`;
}


/*
  SOURCE BADGE CONFIG
  Maps source name to display label and CSS class.
*/
const SOURCE_CONFIG = {
  semantic_scholar: { label: 'Semantic Scholar', cls: 'badge-ss' },
  arxiv:            { label: 'arXiv',            cls: 'badge-arxiv' },
  openalex:         { label: 'OpenAlex',         cls: 'badge-openalex' },
  pubmed:           { label: 'PubMed',           cls: 'badge-pubmed' },
};


function PaperCard({ paper, index, searchQuery }) {
  /*
    Props:
      paper       — paper object from API
      index       — position (0,1,2...) for animation delay + card number
      searchQuery — current search term for keyword highlighting
  */

  const [expanded,        setExpanded]        = useState(false);
  const [summaryLoading,  setSummaryLoading]  = useState(false);
  const [onDemandSummary, setOnDemandSummary] = useState(null);
  const [copied,          setCopied]          = useState(false);
  // copied: true for 2 seconds after clicking copy citation

  const handleSummarize = async () => {
    if (!paper.abstract) return;
    setSummaryLoading(true);
    try {
      const result = await summarizePaper(paper.abstract);
      setOnDemandSummary(result.summary);
    } catch {
      setOnDemandSummary('Could not generate summary.');
    } finally {
      setSummaryLoading(false);
    }
  };

  /*
    handleCopyCitation()
    ─────────────────────
    Formats APA citation and copies it to the clipboard.

    navigator.clipboard.writeText() is the modern clipboard API.
    It returns a Promise — we await it.

    After copying, we show "Copied!" for 2 seconds then reset.
    setTimeout(() => setCopied(false), 2000) runs after 2000ms.
  */
  const handleCopyCitation = async () => {
    const citation = formatAPA(paper);
    try {
      await navigator.clipboard.writeText(citation);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for browsers that block clipboard
      prompt('Copy this citation:', citation);
    }
  };

  const displaySummary = onDemandSummary || paper.ai_summary;
  const readingTime    = estimateReadingTime(paper.abstract);
  const sourceConfig   = SOURCE_CONFIG[paper.source] || { label: paper.source, cls: 'badge-arxiv' };

  const formatAuthors = (authors) => {
    if (!authors?.length) return 'Unknown authors';
    if (authors.length <= 3) return authors.join(', ');
    return `${authors.slice(0, 3).join(', ')} +${authors.length - 3} more`;
  };

  // For abstract display: highlight query terms
  const abstractToShow = expanded ? paper.abstract : (
    paper.abstract
      ? paper.abstract.slice(0, 240) + (paper.abstract.length > 240 ? '…' : '')
      : null
  );

  return (
    <div
      className="paper-card"
      style={{ animationDelay: `${index * 0.055}s` }}
    >
      {/* Decorative card number */}
      <span className="card-number" aria-hidden="true">
        {String(index + 1).padStart(2, '0')}
      </span>

      {/* ── Top ── */}
      <div className="card-top">
        <div className="card-badges">

          {/* Source badge */}
          <span className={`badge ${sourceConfig.cls}`}>
            {sourceConfig.label}
          </span>

          {paper.year && (
            <span className="badge badge-year">{paper.year}</span>
          )}

          {paper.citation_count > 0 && (
            <span className="badge badge-cite">
              ⭐ {paper.citation_count.toLocaleString()}
            </span>
          )}

          {/* Reading time estimate */}
          {readingTime && (
            <span className="badge badge-time">
              🕐 {readingTime}
            </span>
          )}

        </div>

        {/* Title with keyword highlight */}
        {paper.url ? (
          <a href={paper.url} target="_blank" rel="noopener noreferrer"
             className="card-title">
            {highlightText(paper.title, searchQuery)}
          </a>
        ) : (
          <span className="card-title">
            {highlightText(paper.title, searchQuery)}
          </span>
        )}

        <p className="card-authors">
          👤 {formatAuthors(paper.authors)}
        </p>
      </div>

      {/* ── AI Summary ── */}
      {displaySummary && (
        <div className="summary-block">
          <div className="summary-header">
            <span className="summary-label">🤖 AI Summary</span>
            {displaySummary.startsWith('[Extracted]') && (
              <span className="summary-tag-extracted">extracted</span>
            )}
          </div>
          <p className="summary-text">
            {displaySummary.replace('[Extracted] ', '')}
          </p>
        </div>
      )}

      {/* ── Abstract with keyword highlighting ── */}
      {paper.abstract && (
        <div className="abstract-block">
          <div className="abstract-label">Abstract</div>
          <p className="abstract-text">
            {/*
              highlightText wraps matching words in <mark> tags.
              React renders the array of strings + <mark> elements correctly.
            */}
            {highlightText(abstractToShow, searchQuery)}
          </p>
          {paper.abstract.length > 240 && (
            <button className="abstract-toggle"
                    onClick={() => setExpanded(!expanded)}>
              {expanded ? '▲ Show less' : '▼ Read more'}
            </button>
          )}
        </div>
      )}

      {/* ── Footer ── */}
      <div className="card-footer">

        {!displaySummary && paper.abstract && (
          <button className="btn-summarize" onClick={handleSummarize}
                  disabled={summaryLoading}>
            {summaryLoading
              ? <><span className="btn-mini-spin"></span> Generating…</>
              : '✨ Summarize'
            }
          </button>
        )}

        {/*
          Copy Citation button.
          Shows "✓ Copied!" for 2 seconds after clicking.
          This visual feedback confirms the action worked.
        */}
        <button
          className={`btn-cite ${copied ? 'btn-cite-success' : ''}`}
          onClick={handleCopyCitation}
          title="Copy APA citation to clipboard"
        >
          {copied ? '✓ Copied!' : '📋 Cite'}
        </button>

        {paper.url && (
          <a href={paper.url} target="_blank" rel="noopener noreferrer"
             className="btn-read">
            Read paper →
          </a>
        )}

      </div>
    </div>
  );
}

export default PaperCard;
