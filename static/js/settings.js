// Web-saved settings

// Init
const settingsTemplate = {
    'gamme': {
        'last_key': ['ionien', 'Do'],
    }
}

// Create if not already
let CURRENT_SETTINGS = null;
try {
    CURRENT_SETTINGS = localStorage.getItem('settings');
    CURRENT_SETTINGS = JSON.parse(CURRENT_SETTINGS);
    if (CURRENT_SETTINGS === null) {
        throw new Error();
    }
    console.log('Restored Settings')
} catch {
    localStorage.setItem('settings', settingsTemplate);
    CURRENT_SETTINGS = settingsTemplate;
    console.log('Default Settings');
}

// Functions
function saveSettings(page, settingsData) {
    CURRENT_SETTINGS[page] = settingsData;
    localStorage.setItem('settings', JSON.stringify(CURRENT_SETTINGS));
    console.log('Saved Settings');
}

function getSettings(page) {
    return CURRENT_SETTINGS[page];
}