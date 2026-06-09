const { loadApp } = require('./helpers/loadApp');

function createElement() {
    return {
        textContent: '0',
        style: {
            setProperty: jest.fn()
        }
    };
}

describe('updateInsightsFromResults', () => {
    test('sets overall score/progress and low-score description', () => {
        let frameTime = 0;
        global.requestAnimationFrame = (cb) => {
            frameTime += 500;
            cb(frameTime);
        };

        const scoreTransport = createElement();
        const scoreEnergy = createElement();
        const scoreFood = createElement();
        const scoreLifestyle = createElement();
        const overallScore = createElement();
        const overallProgress = createElement();
        const overallDesc = createElement();

        const progressFill = { style: { setProperty: jest.fn() } };
        const card = { querySelector: jest.fn(() => progressFill) };

        const { updateInsightsFromResults } = loadApp({
            documentOverrides: {
                getElementById: jest.fn((id) => {
                    const map = {
                        'score-transport': scoreTransport,
                        'score-energy': scoreEnergy,
                        'score-food': scoreFood,
                        'score-lifestyle': scoreLifestyle,
                        'insight-transport': card,
                        'insight-energy': card,
                        'insight-food': card,
                        'insight-lifestyle': card,
                        'overall-score': overallScore,
                        'overall-progress': overallProgress,
                        'overall-desc': overallDesc
                    };
                    return map[id] || null;
                })
            }
        });

        updateInsightsFromResults({
            transport: 450,
            energy: 350,
            food: 280,
            lifestyle: 290
        });

        expect(overallProgress.style.setProperty).toHaveBeenCalledWith('--progress', expect.stringMatching(/deg$/));
        expect(overallDesc.textContent).toContain('Time to take action');
        expect(Number(overallScore.textContent)).toBeGreaterThanOrEqual(0);
    });
});
