    // Common Musical Functions & Constants

// Values
const INTERVALS = {
    0: 'F',
    1: '2m',
    2: '2M',
    3: '3m',
    4: '3M',
    5: '4J',
    6: '5-',
    7: '5J',
    8: '6m',
    9: '6M',
    10:'7m',
    11:'7M',
    12:'F',
    13:'9m',
    14:'9M',
    17:'11J',
    18:'11#',
    20:'13m',
    21:'13M',
}

const DEGREES = ["I", "II", "III", "IV", "V", "VI", "VII"]

// Functions
function render_fretboard(fretboard_data, fretboard_container) {
    const fretboard_length = fretboard_data[0].frets.length

    // Reset
    fretboard_container.innerHTML = '';

    // Create table
    const t = document.createElement('table');
    const t_head = document.createElement('thead');
    const t_body = document.createElement('tbody');
    t.append(t_head, t_body);
    fretboard_container.append(t);

    // Create each column
    const t_rows = [];
    for (let i=0; i<fretboard_length; i++) {
        const tr = document.createElement('tr')
        if (i===0) {
            t_head.append(tr);
        } else {
            t_body.append(tr);
        }
        t_rows.push(tr);
    }

    // Fill each column
    for (let i=0; i<fretboard_length; i++) {

        fretboard_data.forEach( (row, j) => {
            const row_type = row.type;
            const cell = document.createElement('td');
            if (row_type === 'header') {
                // Header
                cell.classList.add('header');
                cell.textContent = row.frets[i];
            } else if (row_type === 'row') {
                // String
                cell.classList.add('string');
                cell.textContent = row.notes[i].name;

                if (row.notes[i].highlight) {
                    if (row.notes[i].highlight === 999) {
                        cell.classList.add('highlight', 'a');
                    } else {
                        cell.classList.add('highlight', 'b');
                    }
                }
            }

            t_rows[j].appendChild(cell);

        })
    }
}