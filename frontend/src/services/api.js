/*
  src/services/api.js
  --------------------
  All communication between React and FastAPI.
  Unchanged from Day 4 — the backend API hasn't changed.
*/

import axios from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 60000,
});

export const searchPapers = async (query, limit = 10, source = 'arxiv', summarize = true) => {
  const response = await api.get('/api/papers/search', {
    params: { query, limit, source, summarize },
  });
  return response.data;
};

export const summarizePaper = async (abstract) => {
  const response = await api.post('/api/papers/summarize', { abstract });
  return response.data;
};

export const checkHealth = async () => {
  const response = await api.get('/api/papers/health');
  return response.data;
};

export default api;
