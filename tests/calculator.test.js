const { calculateTransport, computeEmissionsFromValues } = require('../js/calculator.js');

function calculateTotal(carKm, electricityBill, meatConsumption, carType, dietType, renewable) {
    const values = {
        carKm, carType, publicTransport: 0, flights: 0,
        electricity: electricityBill, gasBill: 0, renewable, heating: 'gas',
        diet: dietType, foodWaste: 'none', localFood: 0,
        shopping: 0, recycling: 'none', streaming: 0, waterUsage: 'average'
    };
    return computeEmissionsFromValues(values).total;
}

// Edge cases
test('zero input = zero CO2', () => {
  expect(calculateTransport(0, 'petrol', 0)).toBe(0);
});
test('negative input handled safely', () => {
  expect(calculateTransport(-100, 'petrol', 0)).toBeGreaterThanOrEqual(0);
});
test('all vegan + electric + renewable = lowest total', () => {
  const low = calculateTotal(0, 0, 0, 'electric', 'vegan', 'full');
  const high = calculateTotal(500, 200, 100, 'petrol', 'heavy', 'none');
  expect(low).toBeLessThan(high);
});
