const KEY = 'ecotrack_data';

export function saveResult(transport, energy, food, lifestyle, total) {
  const history = getHistory();
  history.push({ transport, energy, food, lifestyle, total, date: Date.now() });
  localStorage.setItem(KEY, JSON.stringify(history));
}

export function getHistory() {
  try { return JSON.parse(localStorage.getItem(KEY)) || []; }
  catch { return []; }
}

export function getLatest() {
  const h = getHistory();
  return h.length ? h[h.length - 1] : null;
}
