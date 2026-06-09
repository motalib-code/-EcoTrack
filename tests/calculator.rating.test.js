const { loadApp } = require('./helpers/loadApp');

describe('getRating', () => {
    const { getRating } = loadApp();

    test.each([
        [149, '🌟 Excellent', 'excellent'],
        [150, '✅ Good', 'good'],
        [249, '✅ Good', 'good'],
        [250, '⚡ Average', 'average'],
        [399, '⚡ Average', 'average'],
        [400, '⚠️ High', 'high'],
        [599, '⚠️ High', 'high'],
        [600, '🔴 Very High', 'very-high']
    ])('returns expected rating for total %i', (total, label, className) => {
        expect(getRating(total)).toEqual({ label, class: className });
    });
});
