// Web-saved settings

// Init
const settingsTemplate = {
    'gamme': {
        'last_key': ['ionien', 'Do'],
    },
    'exercises': {
        'search': {
            'name':'',
            'category': 'all',
            'sort': 'latest',
        }
    },
    'accords': {},
}

// Get global settings
let SETTINGS = null;
try {
    SETTINGS = JSON.parse(localStorage.getItem('settings'));
} catch {
    resetSettings();
}

if (!SETTINGS) {
    resetSettings();
}

// Functions
function getSettings(page) {
    return SETTINGS[page];
}

function saveSettings(page_settings, page) {
    SETTINGS[page] = page_settings;
    localStorage.setItem('settings', JSON.stringify(SETTINGS));
}

function resetSettings() {
    localStorage.setItem('settings', JSON.stringify(settingsTemplate));
    SETTINGS = settingsTemplate;
}