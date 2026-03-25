# Guitar-related function/class

        # 0            2            4           6             8             10
NOTES = ["Do", "Do#", "Ré", "Ré#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si"]
        #       1            3            5            7              9            11

class Note:
    def __init__(self, note_index:int) -> None:
        self.note_index = note_index
        self.note_name = NOTES[note_index % len(NOTES)]
        self.highlight = False
        self.highlight_color = "#A653D6"

class NotePosition:
    def __init__(self, chord_id:int, note_id:int) -> None:
        self.chord_id = chord_id    # 0 : High E note
        self.note_id = note_id      # 0 : Open string note

FRETBOARD_LENGTH = 20
FRETBOARD = [
    [Note(4)],
    [Note(11)],
    [Note(7)],
    [Note(2)],
    [Note(9)],
    [Note(4)]
]

# Generate full fretboard
for n_chord in range(len(FRETBOARD)):
    for i in range(1, FRETBOARD_LENGTH):
        initial_note = FRETBOARD[n_chord][0].note_index
        next_note = Note(initial_note + i)
        FRETBOARD[n_chord].append(next_note)

# Functions
def apply_pattern(pattern:list[tuple[int, int]]) -> list[list[Note]]:
    F = FRETBOARD.copy()

    for p in pattern:
        p_row = p[0]
        p_col = p[1]
        FRETBOARD[p_row][p_col].highlight = True

    return F

# Pattern
pattern1 = [
    (0, 4),
    (1, 4),
    (2, 4),
    (3, 4),
    (5, 4),
]
