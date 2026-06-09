function loadApp({ documentOverrides = {}, windowOverrides = {} } = {}) {
    jest.resetModules();

    const baseDocument = {
        addEventListener: jest.fn(),
        querySelectorAll: jest.fn(() => []),
        getElementById: jest.fn(() => null),
        querySelector: jest.fn(() => null),
        documentElement: {
            setAttribute: jest.fn(),
            removeAttribute: jest.fn(),
            getAttribute: jest.fn(() => null)
        }
    };

    global.document = { ...baseDocument, ...documentOverrides };
    global.window = {
        addEventListener: jest.fn(),
        matchMedia: jest.fn(() => ({ matches: false })),
        ...windowOverrides
    };
    global.localStorage = {
        getItem: jest.fn(() => null),
        setItem: jest.fn()
    };

    return require('../../app.js');
}

module.exports = { loadApp };
