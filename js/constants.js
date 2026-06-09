/**
 * Shared constants for EcoTrack calculations.
 */
const CO2_FACTORS = {
  car: { petrol: 0.21, diesel: 0.27, hybrid: 0.12, electric: 0.05, none: 0 },
  publicTransportPerHour: 0.089,
  flightPerYear: 255,
  electricityPerDollar: 0.92,
  gasPerDollar: 2.1,
  renewable: { none: 1, partial: 0.7, mostly: 0.3, full: 0.05, renewable: 0.05 },
  heating: { gas: 1, electric: 0.8, oil: 1.3, heatpump: 0.3, wood: 0.6 },
  diet: {
    'heavy-meat': 250,
    heavy: 250,
    'medium-meat': 180,
    'low-meat': 130,
    pescatarian: 110,
    vegetarian: 85,
    vegan: 60
  },
  foodWaste: { high: 1.3, medium: 1.1, low: 1, none: 0.9 },
  recycling: { none: 1.2, some: 1, most: 0.8, all: 0.6 },
  water: { high: 1.3, average: 1, conscious: 0.7, minimal: 0.5 }
};

const STORAGE_KEYS = {
  history: 'ecotrack_history'
};

const MONTH_LABELS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

const EXPORTS = { CO2_FACTORS, STORAGE_KEYS, MONTH_LABELS };

if (typeof module !== 'undefined' && module.exports) {
  module.exports = EXPORTS;
}

if (typeof window !== 'undefined') {
  window.EcoTrackConstants = EXPORTS;
}
