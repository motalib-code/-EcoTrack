const constants = typeof window !== 'undefined' && window.EcoTrackConstants
  ? window.EcoTrackConstants
  : require('./constants');

const { CO2_FACTORS } = constants;

/**
 * Parse and validate non-negative numeric input.
 * @param {unknown} value
 * @returns {number}
 */
function toNonNegativeNumber(value) {
  const parsed = typeof value === 'number' ? value : parseFloat(String(value ?? '').trim());
  if (!Number.isFinite(parsed) || parsed < 0) return 0;
  return parsed;
}

/**
 * Calculate monthly transport emissions.
 */
function calculateTransport(carKm, carType, publicTransportHours, flightsPerYear = 0) {
  const km = toNonNegativeNumber(carKm);
  const pt = toNonNegativeNumber(publicTransportHours);
  const flights = toNonNegativeNumber(flightsPerYear);
  const carFactor = CO2_FACTORS.car[carType] ?? 0;

  return (km * 4.33 * carFactor) +
    (pt * 4.33 * CO2_FACTORS.publicTransportPerHour) +
    (flights * CO2_FACTORS.flightPerYear / 12);
}

/**
 * Calculate monthly home energy emissions.
 */
function calculateEnergy(electricityBill, gasBill, renewable, heating = 'gas') {
  const electricity = toNonNegativeNumber(electricityBill);
  const gas = toNonNegativeNumber(gasBill);
  const renewableFactor = CO2_FACTORS.renewable[renewable] ?? 1;
  const heatingFactor = CO2_FACTORS.heating[heating] ?? 1;

  return ((electricity * CO2_FACTORS.electricityPerDollar) + (gas * CO2_FACTORS.gasPerDollar)) * renewableFactor * heatingFactor;
}

/**
 * Calculate monthly food emissions.
 */
function calculateFood(diet, foodWaste, localFood = 0) {
  const dietBase = CO2_FACTORS.diet[diet] ?? CO2_FACTORS.diet['medium-meat'];
  const wasteFactor = CO2_FACTORS.foodWaste[foodWaste] ?? 1;
  const local = Math.min(100, toNonNegativeNumber(localFood));
  const localFactor = 1 - (local / 100) * 0.3;

  return dietBase * wasteFactor * localFactor;
}

/**
 * Calculate monthly lifestyle emissions.
 */
function calculateLifestyle(shopping, recycling, streaming, waterUsage) {
  const shoppingVal = toNonNegativeNumber(shopping);
  const stream = toNonNegativeNumber(streaming);
  const recyclingFactor = CO2_FACTORS.recycling[recycling] ?? 1;
  const waterFactor = CO2_FACTORS.water[waterUsage] ?? 1;

  return (shoppingVal * 0.5 * recyclingFactor) +
    (stream * 30 * 0.036) +
    (waterFactor * 20);
}

/**
 * Calculate overall eco score from category scores.
 */
function calculateEcoScore(transportScore, energyScore, foodScore, lifestyleScore) {
  const values = [transportScore, energyScore, foodScore, lifestyleScore]
    .map(toNonNegativeNumber)
    .map((v) => Math.min(v, 100));

  return Math.round(values.reduce((sum, value) => sum + value, 0) / values.length);
}

/**
 * Read form inputs from a document-like object.
 */
function readInputValues(doc = document) {
  const readValue = (id) => {
    const element = doc.getElementById(id);
    return element ? element.value : '';
  };

  return {
    carKm: readValue('car-km'),
    carType: readValue('car-type'),
    publicTransport: readValue('public-transport'),
    flights: readValue('flights'),
    electricity: readValue('electricity'),
    gasBill: readValue('gas-bill'),
    renewable: readValue('renewable'),
    heating: readValue('heating'),
    diet: readValue('diet'),
    foodWaste: readValue('food-waste'),
    localFood: readValue('local-food'),
    shopping: readValue('shopping'),
    recycling: readValue('recycling'),
    streaming: readValue('streaming'),
    waterUsage: readValue('water-usage')
  };
}

/**
 * Compute full monthly emissions from normalized values.
 */
function computeEmissionsFromValues(values) {
  const transportEmissions = calculateTransport(values.carKm, values.carType, values.publicTransport, values.flights);
  const energyEmissions = calculateEnergy(values.electricity, values.gasBill, values.renewable, values.heating);
  const foodEmissions = calculateFood(values.diet, values.foodWaste, values.localFood);
  const lifestyleEmissions = calculateLifestyle(values.shopping, values.recycling, values.streaming, values.waterUsage);
  const total = transportEmissions + energyEmissions + foodEmissions + lifestyleEmissions;

  return {
    transport: Math.round(transportEmissions),
    energy: Math.round(energyEmissions),
    food: Math.round(foodEmissions),
    lifestyle: Math.round(lifestyleEmissions),
    total: Math.round(total)
  };
}

const EXPORTS = {
  toNonNegativeNumber,
  calculateTransport,
  calculateEnergy,
  calculateFood,
  calculateLifestyle,
  calculateEcoScore,
  readInputValues,
  computeEmissionsFromValues
};

if (typeof module !== 'undefined' && module.exports) {
  module.exports = EXPORTS;
}

if (typeof window !== 'undefined') {
  window.EcoTrackCalculator = EXPORTS;
}
