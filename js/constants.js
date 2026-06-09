const CO2_FACTORS = {
  car: { petrol: 0.21, diesel: 0.27, hybrid: 0.12, electric: 0.05, none: 0 },
  transport: { petrol: 0.21, diesel: 0.27, hybrid: 0.12, electric: 0.05, none: 0 },
  publicTransportPerHour: 0.089,
  flightPerYear: 255,
  electricityPerDollar: 0.92,
  gasPerDollar: 2.1,
  renewable: { none: 1, partial: 0.7, mostly: 0.3, full: 0.05, renewable: 0.05 },
  heating: { gas: 1, electric: 0.8, oil: 1.3, heatpump: 0.3, wood: 0.6 },
  diet: {
    'heavy-meat': 250,
    heavy: 150,
    'medium-meat': 180,
    medium: 100,
    'low-meat': 130,
    low: 60,
    pescatarian: 50,
    vegetarian: 40,
    vegan: 25
  },
  foodWaste: { high: 20, medium: 12, low: 6, none: 2 },
  waste: { high: 20, medium: 12, low: 6, none: 2 },
  energy: { none: 1.0, partial: 0.6, mostly: 0.3, full: 0.05 },
  recycling: { none: 1.2, some: 1, most: 0.8, all: 0.6 },
  water: { high: 1.3, average: 1, conscious: 0.7, minimal: 0.5 }
};

const GLOBAL_AVG_KG_YEAR = 4000;
const MAX_CALC_KM = 5000;
const MAX_ELECTRICITY_BILL = 1000;

const STORAGE_KEYS = {
  history: 'ecotrack_history'
};

const MONTH_LABELS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

const EXPORTS = { CO2_FACTORS, GLOBAL_AVG_KG_YEAR, MAX_CALC_KM, MAX_ELECTRICITY_BILL, STORAGE_KEYS, MONTH_LABELS };

if (typeof module !== 'undefined' && module.exports) {
  module.exports = EXPORTS;
}

if (typeof window !== 'undefined') {
  window.EcoTrackConstants = EXPORTS;
}
