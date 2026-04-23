        // Accords - JS

// Constants / Variables
let current_chart_index = 0;
let current_fretboard_data = [];

// Elements
const search_input = document.querySelector('.param #search');
const search_kind = document.querySelector('.param #kind');
const result_container = document.querySelector('.search-frame .output');

const view_element = document.querySelector('div.view-frame');
const chord_name = view_element.querySelector('#name');
const chord_kind = view_element.querySelector('#kind');
const chord_comp = view_element.querySelector('#compo');
const chord_feel = view_element.querySelector('#feeling');
const chart_container = view_element.querySelector('.general .chart .container');
const chart_left = view_element.querySelector('.general .chart .left');
const chart_right = view_element.querySelector('.general .chart .right');
const fretboard_container = view_element.querySelector('#fretboard');

// Functions
function clicked_chord_item(chord) {
    p = {'chord_id': chord.id}

    // General
    chord_name.innerText = chord.name;
    chord_kind.innerText = 'Type : ' + chord.kind;
    chord_feel.innerText = 'Feeling : ' + chord.sound;
    chord_comp.innerHTML = 'Notes : ' + chord.structure.map((val, i) => `${INTERVALS[val]} (${chord.composing_notes[i]}) `).join('&nbsp&nbsp&nbsp&nbsp')

    // Chart
    render_chart();

    // Fretboard
    call_api('/fretboard', p)
    .then(fretboard => {
        current_fretboard_data = fretboard;
        render_fretboard(current_fretboard_data[current_chart_index], fretboard_container);
    })
}

function render_chart () {
    call_api('/chart', p)
    .then(chart => {

        const arr = chart[current_chart_index];

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
        chart_container.innerHTML = '';
        chart_container.appendChild(table);

        // Chart controls (prev/next pattern)
        if (current_chart_index > 0) { chart_left.classList.add('visible') } else { chart_left.classList.remove('visible'); }
        if (current_chart_index < chart.length-1) { chart_right.classList.add('visible') } else { chart_right.classList.remove('visible'); }
    })

}

function render_chord_item(chord) {
    const item = document.createElement('div');
    item.classList.add('item');

    const title = document.createElement('h4');
    title.innerText = chord.name;
    item.appendChild(title);

    result_container.appendChild(item);

    // On clikc
    item.addEventListener('click', () => {
        clicked_chord_item(chord);
    })

}

function search_chords() {
    call_api('/chords', {'prefix':search_input.value, 'kind':search_kind.value})
    .then(response => {
        // Clear output
        result_container.innerHTML = '';

        // Render items
        response.forEach(element => {
            render_chord_item(element)
        });

        // Check if only 1 element
        if (response.length === 1) {
            // Auto click element
            result_container.lastChild.click();
        }
    })
}

// Events
search_input.addEventListener('input', () => {
    search_chords();
})

search_kind.addEventListener('change', () => {
    search_chords();
})

chart_left.onclick = () => { current_chart_index--; render_fretboard(current_fretboard_data[current_chart_index], fretboard_container);; render_chart(); }
chart_right.onclick = () => { current_chart_index++; render_fretboard(current_fretboard_data[current_chart_index], fretboard_container);; render_chart(); }

// Init
search_chords();
