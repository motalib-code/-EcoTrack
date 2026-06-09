/**
 * Derive top focus categories from emission results.
 */
function getRecommendationFocus(results) {
  const categories = [
    { key: 'transport', value: Number(results?.transport || 0) },
    { key: 'energy', value: Number(results?.energy || 0) },
    { key: 'food', value: Number(results?.food || 0) },
    { key: 'lifestyle', value: Number(results?.lifestyle || 0) }
  ];

  return categories.sort((a, b) => b.value - a.value).slice(0, 2).map((item) => item.key);
}

const EXPORTS = { getRecommendationFocus };

if (typeof module !== 'undefined' && module.exports) {
  module.exports = EXPORTS;
}

if (typeof window !== 'undefined') {
  window.EcoTrackRecommendations = EXPORTS;
}
