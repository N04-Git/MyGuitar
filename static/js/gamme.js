// Panels handler - Gamme Page

// Input
const gamme_input = document.querySelector('#gamme');
const note_input = document.querySelector('#note');
const architecture_table = document.querySelector('.architecture table')
const chords_frame = document.querySelector('.chords');

// Chart
const chart_number = chords_frame.querySelector('.chart .number');
const chart_container = chords_frame.querySelector('.chart .container');
const chart_name = chords_frame.querySelector('.chart .name')
const chart_kind = chords_frame.querySelector('.chart .kind');
const chart_feeling = chords_frame.querySelector('.chart .feeling');
const chart_structure = chords_frame.querySelector('.chart .structure');
const chart_controller = chords_frame.querySelector('.chart .wrapper')
const chart_left_button = chords_frame.querySelector('#prev-chart');
const chart_right_button = chords_frame.querySelector('#next-chart');
const selected_chords_options = chords_frame.querySelector('.list .options');

// Fretboard
const fretboard_container = document.querySelector('#fretboard')

let MAX_CHART_NUMBER = 0;
let CURRENT_CHART_NUMBER = 0;
let CURRENT_CLICKED_CHORD = null;
let current_key_data = null;
let ACTIVE_CHORDS_SELECTION = {
    'Majeur': true,
    'Mineur': true,
    '6th': false,
    '7th': false,
    '9th': false,
    'Sus': false,
};

const PAGE_SETTINGS = getSettings('gamme');

// Functions
function render_architecture(notes, intervals) {
    // Reset
    architecture_table.innerHTML = '';

    // Rows
    const degrees_row = document.createElement('tr');
    const intervals_row = document.createElement('tr');
    const notes_row = document.createElement('tr');

    // Create each column
    for (let i=0; i<=notes.length; i++) {
        const degree_cell = document.createElement('th');
        const note_cell = document.createElement('td');
        const interval_cell = document.createElement('td');

        degree_cell.textContent = DEGREES[i%notes.length];
        note_cell.textContent = notes[i%notes.length]
            .replace(/b/g, '♭')
            .replace(/#/g, '♯');
        interval_cell.textContent = parseInt(intervals[i]) / 2;
        interval_cell.classList.add('xs')

        degrees_row.append(degree_cell, document.createElement('td'));
        notes_row.append(note_cell, document.createElement('td'));
        intervals_row.append(document.createElement('td'), interval_cell);
    }

    // Delete last cells
    degrees_row.removeChild(degrees_row.lastChild);
    intervals_row.removeChild(intervals_row.lastChild);
    notes_row.removeChild(notes_row.lastChild);

    architecture_table.append(degrees_row, intervals_row, notes_row);

}

function render_chart(chord_id) {
    // Render chart
    chart_number.innerText = CURRENT_CHART_NUMBER+1;

    // Fetch API
    p = {'chord_id': chord_id}
    call_api('/chart', p)
    .then(chart => {

        // Chart Array
        const arr = chart[CURRENT_CHART_NUMBER];
        if (arr == "A") { console.warn('No charts available yet'); return }

        // Controller
        MAX_CHART_NUMBER = chart.length-1;
        if (chart.length <= 1) {
            // Disable arrows
            chart_controller.classList.add('disabled');
        } else {
            chart_controller.classList.remove('disabled');
        }

        // Clear previous
        chart_container.innerHTML = '';

        // Create table
        let isFirst = true;
        const table = document.createElement('table');
        arr.forEach( row => {
            // Rows
            const tr = document.createElement('tr');
            row.forEach((cell) => {
                const cell_highlight = cell[0];
                const cell_interval = INTERVALS[cell[1] % 12];

                // Columns
                const td = document.createElement('td');
                if (isFirst) { td.classList.add('top'); }

                const wrapped = document.createElement('div');
                wrapped.classList.add('cell');

                const subWrapped = document.createElement('p');
                if (cell_highlight) { wrapped.classList.add('highlight'); subWrapped.innerText = cell_interval; }

                wrapped.appendChild(subWrapped);
                td.appendChild(wrapped);
                tr.appendChild(td);
            })
            table.appendChild(tr);
            if (isFirst) { isFirst = false; }
        })

        // Add
        chart_container.appendChild(table);
    })
}

function render_chords(degrees) {
    const chord_container = chords_frame.querySelector('.list .container');
    // Reset
    chord_container.innerHTML = '';

    for (let i=0; i<degrees.length; i++) {
        const chords_degree = degrees[i];

        chords_degree.forEach(chord => {

            if (ACTIVE_CHORDS_SELECTION[chord.kind]) {

                // Create Item
                const item = document.createElement('div');
                const h3 = document.createElement('h3');

                item.classList.add('item')
                item.setAttribute('data-id', chord.id);
                if (i===0) {
                    item.setAttribute('data-sum', 0);
                }
                h3.textContent = chord.name;

                item.appendChild(h3);
                chord_container.appendChild(item);

                // Click
                item.addEventListener('click', () => {
                    // (un)Select chord_clicked
                    if (CURRENT_CLICKED_CHORD) { CURRENT_CLICKED_CHORD.classList.remove('selected'); }
                        CURRENT_CLICKED_CHORD = item;
                        item.classList.add('selected');

                    // Reset
                    CURRENT_CHART_NUMBER = 0;
                    chart_left_button.classList.add('disabled');
                    chart_right_button.classList.remove('disabled');

                    // Render
                    const chord_id = parseInt(CURRENT_CLICKED_CHORD.getAttribute('data-id'));
                    render_chart(chord_id);
                    render_fretboard_key_chord(chord_id);

                    // Update chart name
                    chart_name.textContent = chord.name;
                    chart_kind.innerText = "Type : " + chord.kind;
                    chart_feeling.innerText = "Feeling : " + chord.sound;
                    chart_structure.innerHTML = `
                    <table>
                        <tr>
                        ${chord.structure.map(val => `<td style="padding: 4px 8px;">${INTERVALS[val]}</td>`).join('')}
                        </tr>
                        <tr>
                        ${chord.composing_notes.map(note => `<td style="padding: 4px 8px;">${note}</td>`).join('')}
                        </tr>
                    </table>
                    `;
                })
            }
        })
    }

    // Auto select first chord
    chord_container.firstChild.click();

}

function refresh_output () {

    // API Data
    param = {
        'mode':gamme_input.value,
        'key':  note_input.value,
    }
    call_api('/key', param).then(response => {
        // Update data
        current_key_data = response;

        // Architecture
        render_architecture(current_key_data.notes, current_key_data.architecture);

        // Clickable Chords
        render_chords(current_key_data.degrees_quality);
    })

    // Save settings
    PAGE_SETTINGS['last_key'] = [gamme_input.value, note_input.value];
    saveSettings(PAGE_SETTINGS, 'gamme');
}

function render_fretboard_key_chord(chord_id) {

    // Fetch fretboard
    const p = {
        'mode':gamme_input.value,
        'key':  note_input.value,
        'chord_id': chord_id,
    }
    call_api('/fretboard', p).then(response => {
        const fretboard_data = response[CURRENT_CHART_NUMBER];
        render_fretboard(fretboard_data, fretboard_container);
    })

}

function chart_arrow_clicked(isPrev) {
    if (isPrev && CURRENT_CHART_NUMBER > 0) {
        // Previous
        CURRENT_CHART_NUMBER -= 1;
        if (CURRENT_CHART_NUMBER === 0) {
            // Disable left
            chart_left_button.classList.add('disabled');
            chart_right_button.classList.remove('disabled');
        } else {
            // Enable left
            chart_left_button.classList.remove('disabled');
        }

    } else if (!isPrev && CURRENT_CHART_NUMBER < MAX_CHART_NUMBER) {
        // Next
        CURRENT_CHART_NUMBER += 1;
        if (CURRENT_CHART_NUMBER === MAX_CHART_NUMBER) {
            // Disable right
            chart_right_button.classList.add('disabled');
            chart_left_button.classList.remove('disabled');
        } else {
            // Enable right
            chart_right_button.classList.remove('disabled');
        }
    } else {
        return
    }

    // Render
    const chord_id = parseInt(CURRENT_CLICKED_CHORD.getAttribute('data-id'));
    render_chart(chord_id);
    render_fretboard_key_chord(chord_id);

}

function chord_selector_clicked(item) {
    let c = 0;
    Object.values(ACTIVE_CHORDS_SELECTION).forEach( v => {
        if (v===true) { c++; }
    })

    // Reverse
    const value = item.getAttribute('data-val');
    if (c === 1 && ACTIVE_CHORDS_SELECTION[value]) { return }
    ACTIVE_CHORDS_SELECTION[value] = !ACTIVE_CHORDS_SELECTION[value];

    if (ACTIVE_CHORDS_SELECTION[value]) {
        item.classList.add('selected');
    } else {
        item.classList.remove('selected');
    }

    // Render chords
    render_chords(current_key_data.degrees_quality);
}

// Events
gamme_input.addEventListener('change', refresh_output);
note_input.addEventListener('change', refresh_output);
chart_left_button.addEventListener('click', () => {chart_arrow_clicked(true);})
chart_right_button.addEventListener('click', () => {chart_arrow_clicked(false);})

// Chord Filter Options
Array.from(selected_chords_options.children).forEach( (child) => {
    child.addEventListener('click', function () {
        chord_selector_clicked(child);
    })
})


// Auto refresh on load
refresh_output();