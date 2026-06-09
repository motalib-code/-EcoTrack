const constants = typeof window !== 'undefined' && window.EcoTrackConstants
  ? window.EcoTrackConstants
  : require('./constants');

const { MONTH_LABELS } = constants;

/**
 * Build chart labels/data from history snapshots.
 */
function buildTrendData(history, limit = 6) {
  const recent = (Array.isArray(history) ? history : []).slice(Math.max(0, (history || []).length - limit));
  return {
    labels: recent.map((entry) => {
      const d = new Date(entry.date);
      return MONTH_LABELS[d.getMonth()] || 'N/A';
    }),
    totals: recent.map((entry) => Math.round(entry.total || 0))
  };
}

/**
 * Calculate month-over-month percent change from history.
 */
function calculateProgress(history) {
  if (!Array.isArray(history) || history.length < 2) return 0;
  const latest = history[history.length - 1].total || 0;
  const previous = history[history.length - 2].total || 0;
  if (!previous) return 0;
  return Math.round(((latest - previous) / previous) * 100);
}

const EXPORTS = { buildTrendData, calculateProgress };

if (typeof module !== 'undefined' && module.exports) {
  module.exports = EXPORTS;
}

if (typeof window !== 'undefined') {
  window.EcoTrackDashboard = EXPORTS;
}
