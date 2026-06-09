const constants = typeof window !== 'undefined' && window.EcoTrackConstants
  ? window.EcoTrackConstants
  : require('./constants');

const { STORAGE_KEYS } = constants;

function sanitizeNumber(value) {
  const parsed = parseFloat(String(value ?? ''));
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : 0;
}

function sanitizeResult(entry) {
  if (!entry || typeof entry !== 'object') return null;

  return {
    transport: sanitizeNumber(entry.transport),
    energy: sanitizeNumber(entry.energy),
    food: sanitizeNumber(entry.food),
    lifestyle: sanitizeNumber(entry.lifestyle),
    total: sanitizeNumber(entry.total),
    date: typeof entry.date === 'string' ? entry.date : new Date().toISOString()
  };
}

function safeStorage() {
  if (typeof localStorage === 'undefined') {
    return null;
  }
  return localStorage;
}

/**
 * Get sanitized saved history.
 */
function getHistory() {
  const storage = safeStorage();
  if (!storage) return [];

  try {
    const raw = storage.getItem(STORAGE_KEYS.history) || '[]';
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];

    return parsed
      .map(sanitizeResult)
      .filter(Boolean);
  } catch {
    return [];
  }
}

/**
 * Save a snapshot to localStorage history.
 */
function saveResult(data) {
  const storage = safeStorage();
  if (!storage) return;

  const history = getHistory();
  const sanitized = sanitizeResult({
    ...data,
    date: data?.date || new Date().toISOString()
  });

  if (!sanitized) return;

  history.push(sanitized);
  storage.setItem(STORAGE_KEYS.history, JSON.stringify(history));
}

/**
 * Get latest saved snapshot.
 */
function getLatest() {
  const history = getHistory();
  return history.length ? history[history.length - 1] : null;
}

/**
 * Get recent snapshots with oldest->newest ordering.
 */
function getRecentHistory(limit = 6) {
  const history = getHistory();
  if (!history.length) return [];
  return history.slice(Math.max(0, history.length - limit));
}

const EXPORTS = { sanitizeNumber, saveResult, getHistory, getLatest, getRecentHistory };

if (typeof module !== 'undefined' && module.exports) {
  module.exports = EXPORTS;
}

if (typeof window !== 'undefined') {
  window.EcoTrackStorage = EXPORTS;
}
