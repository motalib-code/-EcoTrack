const fs = require('fs');
const path = require('path');

describe('recommendations section', () => {
    test('contains at least six recommendation cards and key titles', () => {
        const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
        const recCards = html.match(/class="rec-card"/g) || [];

        expect(html).toContain('id="recommendations"');
        expect(recCards.length).toBeGreaterThanOrEqual(6);
        expect(html).toContain('Bike to Work');
        expect(html).toContain('Meatless Mondays');
        expect(html).toContain('Smart Thermostat');
    });
});
