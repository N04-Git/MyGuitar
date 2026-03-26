import re

# Guitar-related function/class

        # 0            2            4           6             8             10
NOTES = ["Do", "Do#", "Ré", "Ré#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si"]
        #       1            3            5            7              9            11

LETTERS = {
    1: "Do",
    2: "Ré",
    3: "Mi",
    4: "Fa",
    5: "Sol",
    6: "La",
    7: "Si",
}

NOTES_ID_BY_NAME = {    # ID (%12) // LETTER NB
    "Dob": (11,1),  #
    "Do": (0,1),    #   I
    "Do#": (1,1),   #

    "Réb": (1,2),   #
    "Ré": (2,2),    #  II
    "Ré#": (3,2),   #

    "Mib": (3,3),   #
    "Mi": (4,3),    # III
    "Mi#" : (5,3),  #

    "Fab": (4,4),   #
    "Fa": (5,4),    #  IV
    "Fa#": (6,4),   #

    "Solb": (6,5),  #
    "Sol": (7,5),   #   V
    "Sol#": (8,5),  #

    "Lab": (8,6),   #
    "La": (9,6),    #  VI
    "La#": (10,6),  #

    "Sib": (10,7),  #
    "Si": (11,7),   # VII
    "Si#": (0,7)    #
}

COLORS = {
    "RED" : "\033[91m",
    "GREEN" : "\033[92m",
    "RESET" : "\033[0m"
}

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

class Note:
    def __init__(self, note_index:int=-1, note_name:str="") -> None:
        if note_index > -1:
            self.index = note_index
            self._name = NOTES[note_index % len(NOTES)]
        if note_name:
            self._name = note_name
            self.index = NOTES_ID_BY_NAME.get(note_name, [-100, -100])[0]

        self.highlight = False
        self.highlight_color = "#A653D6"

    @property
    def name(self):
        if self.highlight:
            return COLORS.get("GREEN", "") + self._name + COLORS.get("RESET", "")
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def getLetterNumber(self) -> int:
        return NOTES_ID_BY_NAME.get(self._name.removesuffix('#').removesuffix('b'), [0, 0])[1]

    def adjustName(self, target_note_index:int):
        # Update name
        target_note_index %= 12
    
        # Compute shortest circular distance
        diff = (target_note_index - self.index) % 12
        if diff > 6:
            diff -= 12

        if diff > 0:
            # Add '#'
            self._name += "#" * diff

        elif diff < 0:
            # Add 'b'
            self._name += "b" * abs(diff)

        # Update index
        self.index = target_note_index

class NotePosition:
    def __init__(self, chord_id:int, note_id:int) -> None:
        self.chord_id = chord_id    # 0 : High E note
        self.note_id = note_id      # 0 : Open string note

class Key:
    def __init__(self, baseNote:Note) -> None:
        self.baseNote = baseNote
        self.name = "DO NOT USE THIS CLASS"
        self.architecture = []
        self.sound = "DO NOT USE THIS CLASS"

    def get_notes(self) -> list[Note]:
        n = [self.baseNote]

        # print(f"ACTUAL : {self.baseNote.index} ({self.baseNote.name})")

        for i in range(len(self.architecture)-1):
            # I, II, III, IV, V, VI, ... = i+1
            # num : note index + architecture (e.g: 3 + 0.5)

            # Current
            current_note = n[-1]
            current_index = current_note.index
            current_letter = current_note.getLetterNumber()

            # Target
            target_letter = current_letter + 1
            if target_letter == 8:
                target_letter = 1

            target_index = (current_index + self.architecture[i])

            if target_index > 12:
                target_index %= 12

            next_note = Note(note_name=LETTERS.get(target_letter, ""))

            # Adjust
            # print(f"ACTUAL : {next_note.index} ({next_note.name}) >> TARGET : {target_index} ({NOTES[target_index%12]}) ({target_index} - {next_note.index} = {target_index - next_note.index})")

            next_note.adjustName(target_index) # Adjust letter to target note index

            n.append(next_note)

        return n

class IonanKey(Key):
    def __init__(self, baseNote) -> None:
        super().__init__(baseNote)
        self.name = "Ionan"
        self.altName = "Major"
        self.architecture = [2, 2, 1, 2, 2, 2, 1]
        self.sound = "Happy, Bright, Stable"

class AeolianKey(Key):
    def __init__(self, baseNote) -> None:
        super().__init__(baseNote)
        self.name = "Aeolian Key"
        self.altName = "Natural Minor"
        self.architecture = [2, 1, 2, 2, 1, 2, 2]

class HarmonicMinorKey(Key):
    def __init__(self, baseNote) -> None:
        super().__init__(baseNote)
        self.name = "Harmonic Minor"
        self.altName = ""
        self.architecture = [2, 1, 2, 2, 1, 3, 1]

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
        initial_note = FRETBOARD[n_chord][0].index
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

def show_fretboard(fretboard:list[list[Note]], left_handed=False):
    display = ""
    note_width = 6
    fret_width = len(fretboard[0])

    # Index
    for i in range(fret_width):
        if left_handed:
            display = f"{i}".ljust(note_width) + display
        else:
            display += f"{i}".ljust(note_width)
    display += '\n'

    # Notes
    for i in range(len(fretboard)):
        chord = fretboard[i]

        # Left-handed
        if left_handed:
            chord.reverse()

        for note in chord:
            display += fill_text(note.name, note_width)

        # Reverse back
        if left_handed:
            chord.reverse()

        display += "\n"

    print(display)

def visible_length(text):
    return len(ansi_escape.sub('', text))

def fill_text(text, width):
    space_to_add = width - visible_length(text)
    return text + " " * space_to_add

# # # # # # # # # # # # # # # # # #

# Pattern
pattern1 = [
    (0, 4),
    (1, 4),
    (2, 4),
    (3, 4),
    (5, 4),
]

apply_pattern(pattern1)

show_fretboard(FRETBOARD, True)

show_fretboard(FRETBOARD, True)