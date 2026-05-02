// Web-saved settings

// Init
const settingsTemplate = {
    'gamme': {
        'last_key': ['ionien', 'Do'],
    }
}

let CURRENT_SETTINGS = JSON.parse(localStorage.getItem('settings'));

// Create if not already
if (!CURRENT_SETTINGS) {
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