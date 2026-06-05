/*
  src/components/ResultsList.jsx
  --------------------------------
  Renders the list of paper cards.

  WHAT IS .map()?
  ───────────────
  .map() is a JavaScript array method that transforms
  every item in an array into something new.

  Like Python's list comprehension:
    Python: [transform(item) for item in items]
    JS:     items.map(item => transform(item))

  In React, we use .map() to turn data into JSX:

    papers.map((paper, index) => (
      <PaperCard key={paper.title} paper={paper} index={index} />
    ))

  This creates one <PaperCard> for EVERY paper in the array.
  React renders all of them in order.

  WHAT IS key={}?
  ───────────────
  React needs a unique "key" for each item in a list.
  This helps React know WHICH item changed when re-rendering.
  Without keys, React might re-render the wrong items.
  Think of it like a database primary key.

  PROPS RECEIVED:
    papers       — array of paper objects from the API
    query        — the search query (shown in results header)
    total        — total count from API
    sourceUsed   — which API was used
    summariesOn  — whether summaries are enabled
*/

import React from 'react';
import PaperCard from './PaperCard';

function ResultsList({ papers, query, total, sourceUsed, summariesOn }) {

  // If no papers array, render nothing
  if (!papers) return null;

  // Empty results
  if (papers.length === 0) {
    return (
      <div className="empty-results">
        <div className="empty-icon">🔍</div>
        <h3>No papers found for "{query}"</h3>
        <p>Try a different search term or switch to a different source.</p>
      </div>
    );
  }

  return (
    <div className="results-container">

      {/* Results summary bar */}
      <div className="results-header">
        <div className="results-count">
          <strong>{total}</strong> papers found for
          <span className="query-highlight"> "{query}"</span>
        </div>
        <div className="results-meta">
          <span className="source-tag">📡 {sourceUsed}</span>
          {summariesOn && <span className="summary-tag">🤖 AI summaries on</span>}
        </div>
      </div>

      {/*
        .map() renders one PaperCard for each paper.

        (paper, index) → index is the position (0, 1, 2...)
          used in PaperCard for staggered animation delay

        key={paper.title + paper.year} → unique identifier for React
          We combine title + year in case two papers have the same title
      */}
      <div className="papers-grid">
        {papers.map((paper, index) => (
          <PaperCard
            key={`${paper.title}-${paper.year}-${index}`}
            paper={paper}
            index={index}
          />
        ))}
      </div>

    </div>
  );
}

export default ResultsList;
