const STORAGE_KEY = 'ecotrack_data';

export function saveCalculation(result) {
  const history = loadHistory();
  history.push({ ...result, date: new Date().toISOString() });
  localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
}

export function loadHistory() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
  } catch { return []; }
}

export function getLatestResult() {
  const h = loadHistory();
  return h.length ? h[h.length - 1] : null;
}
