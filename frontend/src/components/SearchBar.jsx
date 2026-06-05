/*
  src/components/SearchBar.jsx
  -----------------------------
  The search input + button at the top of the page.

  WHAT IS A COMPONENT?
    A component is a reusable piece of UI.
    Like a Python function that returns HTML.
    
    function SearchBar(props) {
      return <div>some HTML</div>
    }

  WHAT ARE PROPS?
    Props = properties passed INTO a component from its parent.
    Like function parameters.
    
    Parent passes:  <SearchBar onSearch={handleSearch} loading={true} />
    Child receives: function SearchBar({ onSearch, loading }) { ... }

  WHAT IS JSX?
    JSX = JavaScript + HTML mixed together.
    Looks like HTML but it's actually JavaScript.
    React converts it to real DOM elements.
*/

import React, { useState } from 'react';

/*
  useState explained:
  ──────────────────
  useState is a React "Hook" — a special function that adds
  state (memory) to a component.

  const [value, setValue] = useState(initialValue)
    value    → the current state value (read it)
    setValue → function to UPDATE the value
    
  When setValue() is called, React re-renders the component
  with the new value. Like a reactive variable.

  Example:
    const [query, setQuery] = useState('')
    query     = '' initially
    setQuery('deep learning') → query becomes 'deep learning'
                              → component re-renders automatically
*/

function SearchBar({ onSearch, loading }) {
  /*
    Props destructured:
      onSearch — function called when user submits search
                 passed from App.js
      loading  — boolean, true while fetching results
                 used to disable the button and show spinner
  */

  // Local state — the text currently typed in the input box
  const [query, setQuery] = useState('');

  // Which source the user selected
  const [source, setSource] = useState('arxiv');

  // Whether to include AI summaries
  const [summarize, setSummarize] = useState(true);

  /*
    handleSubmit()
    ──────────────
    Called when user clicks Search or presses Enter.
    
    e.preventDefault() stops the browser from refreshing the page.
    Without it, HTML forms reload the page on submit — we don't want that.
  */
  const handleSubmit = (e) => {
    e.preventDefault(); // Stop page reload
    const trimmed = query.trim(); // Remove leading/trailing spaces
    if (trimmed.length < 2) return; // Don't search empty or 1-char queries
    onSearch(trimmed, source, summarize); // Call parent's handler
  };

  return (
    // <form onSubmit> triggers handleSubmit when Enter is pressed OR button clicked
    <form className="search-form" onSubmit={handleSubmit}>

      <div className="search-input-row">
        {/*
          Controlled input:
          value={query}         → React controls what's displayed
          onChange={e => ...}   → called every keystroke
          e.target.value        → the new text after the keystroke

          This is a "controlled component" — React owns the value,
          not the browser. They stay in sync via state.
        */}
        <input
          type="text"
          className="search-input"
          placeholder="e.g. medical image analysis, transformer neural networks..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={loading}
          // disabled while loading — prevents double-submit
        />

        {/*
          Button is disabled when:
          1. loading is true (request in progress)
          2. query is empty (nothing to search)
        */}
        <button
          type="submit"
          className="search-button"
          disabled={loading || query.trim().length < 2}
        >
          {loading ? (
            // Show spinner while loading
            <span className="btn-loading">
              <span className="spinner"></span> Searching...
            </span>
          ) : (
            '🔍 Search'
          )}
        </button>
      </div>

      {/* Options row — source selector and summarize toggle */}
      <div className="search-options">

        <div className="option-group">
          <label className="option-label">Source</label>
          {/*
            select = dropdown menu
            value={source} → controlled by React state
            onChange → updates state when user picks different option
          */}
          <select
            className="option-select"
            value={source}
            onChange={(e) => setSource(e.target.value)}
            disabled={loading}
          >
            <option value="arxiv">arXiv (free, always works)</option>
            <option value="semantic_scholar">Semantic Scholar (needs API key)</option>
            <option value="auto">Auto (tries both)</option>
          </select>
        </div>

        <div className="option-group">
          <label className="option-label">AI Summaries</label>
          <label className="toggle">
            {/*
              Checkbox for toggling summarize on/off
              checked={summarize} → controlled by state
              onChange → flips the boolean
            */}
            <input
              type="checkbox"
              checked={summarize}
              onChange={(e) => setSummarize(e.target.checked)}
              disabled={loading}
            />
            <span className="toggle-slider"></span>
          </label>
        </div>

      </div>
    </form>
  );
}

export default SearchBar;
