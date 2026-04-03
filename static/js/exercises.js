// Exercises Page Handling
const exercises_container = document.querySelector('.exercises');
const search_name = document.querySelector('.search #name input');
const search_category = document.querySelector('.search #category select');
const search_sort = document.querySelector('.search #sort select');

const view = document.querySelector('#view');
const view_back_btn = view.querySelector(".back-btn");

// Globals
PAGE_SETTINGS = getSettings('exercises');

// Functions

function add_exercise(exercise) {
    const item = document.createElement('div');
    item.classList.add('item');

    const name = document.createElement('h3');
    name.innerText = exercise.name;
    item.appendChild(name);

    const category = document.createElement('h4');
    category.innerText = exercise.category;
    item.appendChild(category);

    // Event
    item.addEventListener('click', () => {
        // Visible view
        view.classList.add('visible');

        // Set title


    })

    // Add
    exercises_container.appendChild(item);
}

function refresh_exercises() {
    // Get current settings
    const param = PAGE_SETTINGS.search;

    // API
    call_api('/exercises', param)
    .then(exercises => {
        // Reset
        exercises_container.innerHTML = '';
        exercises.forEach(exo => {
            add_exercise(exo)
        });
    })

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

view_back_btn.addEventListener('click', () => {
    view.classList.remove('visible');
})

refresh_exercises();