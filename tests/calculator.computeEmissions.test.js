const { loadApp } = require('./helpers/loadApp');

function createValueMap(values) {
    return {
        getElementById: jest.fn((id) => ({ value: values[id] }))
    };
}

describe('computeEmissions', () => {
    test('calculates expected monthly emissions from input values', () => {
        const values = {
            'car-km': '100',
            'car-type': 'petrol',
            'public-transport': '10',
            flights: '2',
            electricity: '200',
            'gas-bill': '50',
            renewable: 'partial',
            heating: 'gas',
            diet: 'vegetarian',
            'food-waste': 'medium',
            'local-food': '50',
            shopping: '100',
            recycling: 'most',
            streaming: '20',
            'water-usage': 'conscious'
        };

        const { computeEmissions } = loadApp({
            documentOverrides: createValueMap(values)
        });

        expect(computeEmissions()).toEqual({
            transport: 137,
            energy: 202,
            food: 79,
            lifestyle: 76,
            total: 495
        });
    });

    test('falls back safely for unknown categories and empty numeric values', () => {
        const values = {
            'car-km': '',
            'car-type': 'unknown',
            'public-transport': '',
            flights: '',
            electricity: '',
            'gas-bill': '',
            renewable: 'unknown',
            heating: 'unknown',
            diet: 'unknown',
            'food-waste': 'unknown',
            'local-food': '',
            shopping: '',
            recycling: 'unknown',
            streaming: '',
            'water-usage': 'unknown'
        };

        const { computeEmissions } = loadApp({
            documentOverrides: createValueMap(values)
        });

        expect(computeEmissions()).toEqual({
            transport: 0,
            energy: 0,
            food: 180,
            lifestyle: 20,
            total: 200
        });
    });
});
