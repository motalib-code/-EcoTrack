const { loadApp } = require('./helpers/loadApp');

function createInsightCard() {
    const description = { textContent: '' };
    return {
        description,
        querySelector: jest.fn(() => description)
    };
}

describe('updateInsightDescriptions', () => {
    test('updates each insight card description based on score bands', () => {
        const cards = {
            transport: createInsightCard(),
            energy: createInsightCard(),
            food: createInsightCard(),
            lifestyle: createInsightCard()
        };

        const { updateInsightDescriptions } = loadApp({
            documentOverrides: {
                getElementById: jest.fn((id) => {
                    if (id === 'insight-transport') return cards.transport;
                    if (id === 'insight-energy') return cards.energy;
                    if (id === 'insight-food') return cards.food;
                    if (id === 'insight-lifestyle') return cards.lifestyle;
                    return null;
                })
            }
        });

        updateInsightDescriptions(
            { transport: 0, energy: 0, food: 0, lifestyle: 0 },
            { transport: 80, energy: 50, food: 20, lifestyle: 75 }
        );

        expect(cards.transport.description.textContent).toContain('Great job');
        expect(cards.energy.description.textContent).toContain('above average');
        expect(cards.food.description.textContent).toContain('significant carbon impact');
        expect(cards.lifestyle.description.textContent).toContain('Great recycling habits');
    });
});
