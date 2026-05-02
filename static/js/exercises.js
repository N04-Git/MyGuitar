// Exercises Page Handling
const exercises_container = document.querySelector('.exercises');
const search_name = document.querySelector('.search #name input');
const search_category = document.querySelector('.search #category select');
const search_sort = document.querySelector('.search #sort select');

const view = document.querySelector('#view');
const view_back_btn = view.querySelector(".back-btn");
const tab_viewport = view.querySelector('.tab-viewport')
const tab_main = view.querySelector('.tab-main');
const tab_restart = view.querySelector('#restart');
const tab_mute = view.querySelector('#mute');
const tab_speed = view.querySelector('#playback-speed');
const tab_speed_txt = view.querySelector('#playback-speed-txt');

// Globals
let isMuted = true;
let isPlaying = false;
const PAGE_SETTINGS = {
    'search': {
        'name':'',
        'category': 'all',
        'sort': 'latest',
    }
}

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

        // Clear tabs
        isMuted = true;
        isPlaying = false;
        tab_main.innerHTML = '';

        // Show tabs
        const settings = {
            file: 'api/gpfile/'+exercise.tabPath,
            core: {
                engine: 'svg'
            },
            player: {
                enableCursor: true,
                enablePlayer: true,
                soundFont: 'https://cdn.jsdelivr.net/npm/@coderline/alphatab@latest/dist/soundfont/sonivox.sf2',
                scrollElement: tab_viewport,
            },
            display: {
                resources: {
                    mainGlyphColor: '#fff',       // numbers, symbols
                    secondaryGlyphColor: '#ccc',  // less important symbols
                    staffLineColor: '#666',
                    barSeparatorColor: '#999',
                    selectionColor: '#ff000067',
                }
            },
            cursor: {
                enable: true,
                followCursor: true,
                smoothScrolling: true,
                color: '#00ff00',
                alpha: 0.8
            }
        };

        const api = new alphaTab.AlphaTabApi(tab_main, settings);
        api.masterVolume = 0;

        // Update commands
        api.scoreLoaded.on( () => {
            updateCommands(api);
        })

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
            add_exercise(exo);
        });
    })
}

function updateCommands(api) {
    // Play
    document.addEventListener('keydown', () => {
        if (isPlaying) {
            api.pause();
        } else {
            api.play();
        }
        isPlaying = !isPlaying;
    })

    tab_restart.onclick = () => {
        api.stop();
        isPlaying = false;
        // Remove focus
        tab_restart.blur();
    }

    tab_mute.onclick = () => {
        if (isMuted) {
            api.masterVolume = 1;
            tab_mute.textContent = 'Mute';
        } else {
            api.masterVolume = 0;
            tab_mute.textContent = 'Unmute';
        }
        isMuted = !isMuted;
        // Remove focus
        tab_mute.blur();
    }

    tab_speed.addEventListener('input', () => {
        api.playbackSpeed = tab_speed.value;
        tab_speed_txt.innerText = tab_speed.value;
    })

}

// Events
search_name.addEventListener('input', () => {
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