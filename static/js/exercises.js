// Exercises Page Handling
const exercises_container = document.querySelector('.exercises');
const search_name = document.querySelector('.search #name input');
const search_category = document.querySelector('.search #category select');
const search_sort = document.querySelector('.search #sort select');

// Globals
PAGE_SETTINGS = getSettings('exercises');

// Functions
function refresh_exercises() {
    // Get current settings
    param = PAGE_SETTINGS.search;
    

    // APi
    call_api('/exercises', param)

    // Save settings
    saveSettings(PAGE_SETTINGS, 'exercises')

}

// Events
search_name.addEventListener('change', () => {
    const v = search_name.value;
    PAGE_SETTINGS.search['name'] = v;
    refresh_exercises();
})
search_category.addEventListener('change', () => {
    const v = search_category.value;
    PAGE_SETTINGS.search['category'] = v;
    refresh_exercises();
})
search_sort.addEventListener('change', () => {
    const v = search_sort.value;
    PAGE_SETTINGS.search['sort'] = v;
    refresh_exercises();
})

refresh_exercises();