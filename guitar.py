        # Guitar stuff #

# Modules
import re
import os
import copy
import time

#### Constants

#Semitones:F    2m     2M    3m     3M    4j    5-     5j     6m      6M    7m     7M

        # 0            2            4           6             8             10
NOTES = ["Do", "Do#", "Ré", "Ré#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si"]
        #       1            3            5            7              9            11

INTERVALS = {
    'FD':   0,
    '2m':   1,
    '2M':   2,
    '3m':   3,
    '3M':   4,
    '4J':   5,
    '5-':   6,
    '5J':   7,
    '6m':   8,
    '6M':   9,
    '7m':   10,
    '7M':   11,
}

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

LEFT_HANDED = True

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

#### Classes

class Note:
    def __init__(self, note:int|str) -> None:
        if type(note) == str:
            self._name = note
            self.index = NOTES_ID_BY_NAME.get(note, [])[0]
        elif type(note) == int:
            self.index = note
            self._name = NOTES[note % len(NOTES)]
        else:
            print('Not definition error !', note)

        self.highlight = False

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
    def __init__(self, string:int, fret:int) -> None:
        self.chord = string
        self.fret = fret

class Pattern:
    def __init__(self, notes:list[NotePosition] | list[Note]) -> None:
        self.notes = notes
        self.kind = type(notes[0])

    def apply(self, row_notes_limit=1) -> list[list[Note]]:

        if row_notes_limit == 0:
            row_notes_limit = len(FRETBOARD[0])

        # Apply pattern to a new returned fretboard
        F = duplicate_fretboard(FRETBOARD)

        # Check kind
        if self.kind == NotePosition:
            for n in self.notes:
                if isinstance(n, NotePosition):
                    F[n.chord][n.fret].highlight = True

        elif self.kind == Note:
            # For each row
            for row in F:
                counter = 0
                # For each note in row
                for note in row:
                    # For each note in pattern's note
                    for n in self.notes:
                        # Compare
                        if isinstance(n, Note) and n.index == (note.index % 12):
                            if counter < row_notes_limit:
                                note.highlight = True
                                counter += 1

        return F

class Key:
    def __init__(self, baseNote:Note) -> None:
        self.baseNote = baseNote
        self.name = "DEFAULT NAME VALUE"
        self.architecture = []
        self.sound = "DEFAULT SOUND VALUE"

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

            next_note = Note(LETTERS.get(target_letter, ""))

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
        self.sound = "Sad"

class HarmonicMinorKey(Key):
    def __init__(self, baseNote) -> None:
        super().__init__(baseNote)
        self.name = "Harmonic Minor"
        self.altName = ""
        self.architecture = [2, 1, 2, 2, 1, 3, 1]

class Exercise:
    def __init__(self, patterns:list[Pattern]) -> None:
        self.patterns = patterns

    def addPattern(self, pattern:Pattern):
        self.patterns.append(pattern)

    def play(self):
        for pattern in self.patterns:
            os.system('cls')
            show_fretboard(pattern.apply())
            time.sleep(1.0)

class Chord:
    def __init__(self, root_note:Note, string_offset=4) -> None:
        self.rootNote = root_note
        self.string_offest = string_offset
        self.rootNote_index = adjust_root_for_ostring(self.rootNote.index, string_offset=self.string_offest)
        self.name = "DEFAULT CHORD NAME"
        self.structure = [] # Refers to Major Scale // Semitones
        self.sound = ""
        self.patterns = [] # Chord chart

class Chord_Major(Chord):
    def __init__(self, root_note:Note) -> None:
        super().__init__(root_note)
        self.name = "Majeur"
        self.structure = [0, 4, 7]
        self.sound = "Happy"
        self.patterns = (
            # Pattern 1
            Pattern([
                NotePosition(0, self.rootNote_index+0),   # F
                NotePosition(1, self.rootNote_index+0),   # 5
                NotePosition(2, self.rootNote_index+1),   # 3
                NotePosition(3, self.rootNote_index+2),   # F
                NotePosition(4, self.rootNote_index+2),   # 5
                NotePosition(5, self.rootNote_index+0)    # F
            ]),
            # Pattern 2
            Pattern([
                NotePosition(0, self.rootNote_index+0),   # 5
                NotePosition(1, self.rootNote_index+2),   # 3
                NotePosition(2, self.rootNote_index+2),   # F
                NotePosition(3, self.rootNote_index+2),   # 5
                NotePosition(4, self.rootNote_index+0),   # F
            ])
        )

class Chord_Minor(Chord):
    def __init__(self, root_note:Note) -> None:
        super().__init__(root_note)
        self.name = "Mineur"
        self.structure = [0, 3, 7]
        self.sound = "Sad"
        self.patterns = (
            # Pattern 1
            Pattern([
                NotePosition(0, self.rootNote_index + 0),
                NotePosition(1, self.rootNote_index + 0),
                NotePosition(2, self.rootNote_index + 0),
                NotePosition(3, self.rootNote_index + 2),
                NotePosition(4, self.rootNote_index + 2),
                NotePosition(5, self.rootNote_index + 0)
            ]),
            # Pattern 2
            Pattern([
                NotePosition(0, self.rootNote_index + 0),
                NotePosition(1, self.rootNote_index + 1),
                NotePosition(2, self.rootNote_index + 2),
                NotePosition(3, self.rootNote_index + 2),
                NotePosition(4, self.rootNote_index + 0)
            ]),
        )

class Chord_Major7(Chord):
    def __init__(self, root_note:Note) -> None:
        super().__init__(root_note)
        self.name = "7e Majeur"
        self.structure = [0, 4, 7, 11]
        self.sound = "Smooth / Jazzy"
        self.patterns = (
            Pattern([
                NotePosition(0, self.rootNote_index + 0),
                NotePosition(1, self.rootNote_index + 0),
                NotePosition(2, self.rootNote_index + 1),
                NotePosition(3, self.rootNote_index + 1),
                NotePosition(4, self.rootNote_index + 2),
                NotePosition(5, self.rootNote_index + 0)
            ]),
            Pattern([
                NotePosition(0, self.rootNote_index + 0),
                NotePosition(1, self.rootNote_index + 2),
                NotePosition(2, self.rootNote_index + 1),
                NotePosition(3, self.rootNote_index + 2),
                NotePosition(4, self.rootNote_index + 0),
            ]),
        )

class Chord_Minor7(Chord):
    def __init__(self, root_note:Note) -> None:
        super().__init__(root_note)
        self.name = "7e Mineur"
        self.structure = [0, 3, 7, 10]
        self.sound = "Soft / Bluesy"
        self.patterns = (
            Pattern([
                NotePosition(0, self.rootNote_index + 0),
                NotePosition(1, self.rootNote_index + 0),
                NotePosition(2, self.rootNote_index + 0),
                NotePosition(3, self.rootNote_index + 0),
                NotePosition(4, self.rootNote_index + 2),
                NotePosition(5, self.rootNote_index + 0)
            ]),
            Pattern([
                NotePosition(0, self.rootNote_index + 0),
                NotePosition(1, self.rootNote_index + 1),
                NotePosition(2, self.rootNote_index + 0),
                NotePosition(3, self.rootNote_index + 2),
                NotePosition(4, self.rootNote_index + 0),
            ]),
        )

class Chord_Sus2(Chord):
    def __init__(self, root_note:Note) -> None:
        super().__init__(root_note, 5)
        self.name = "Sus2"
        self.structure = [0, 2, 7]
        self.sound = "Open / Floating"
        self.patterns = (
            Pattern([
                NotePosition(0, self.rootNote_index + 1),
                NotePosition(1, self.rootNote_index + 1),
                NotePosition(2, self.rootNote_index + 0),
                NotePosition(3, self.rootNote_index + 3),
                NotePosition(4, self.rootNote_index + 3),
                NotePosition(5, self.rootNote_index + 1)
            ]),
            Pattern([
                NotePosition(0, self.rootNote_index + 1),
                NotePosition(1, self.rootNote_index + 1),
                NotePosition(2, self.rootNote_index + 3),
                NotePosition(3, self.rootNote_index + 3),
                NotePosition(4, self.rootNote_index + 1),
            ]),
        )

class Chord_Sus4(Chord):
    def __init__(self, root_note:Note) -> None:
        super().__init__(root_note)
        self.name = "Sus4"
        self.structure = [0, 5, 7]
        self.sound = "Tension / Suspended"
        self.patterns = (
            Pattern([
                NotePosition(0, self.rootNote_index + 0),
                NotePosition(1, self.rootNote_index + 0),
                NotePosition(2, self.rootNote_index + 2),
                NotePosition(3, self.rootNote_index + 2),
                NotePosition(4, self.rootNote_index + 2),
                NotePosition(5, self.rootNote_index + 0)
            ]),
            Pattern([
                NotePosition(0, self.rootNote_index + 0),
                NotePosition(1, self.rootNote_index + 3),
                NotePosition(2, self.rootNote_index + 2),
                NotePosition(3, self.rootNote_index + 2),
                NotePosition(4, self.rootNote_index + 0),
            ]),
        )

class Chord_Major6(Chord):
    def __init__(self, root_note:Note) -> None:
        super().__init__(root_note, 5)
        self.name = "6e Majeur"
        self.structure = [0, 4, 7, 9]
        self.sound = "Warm / Stable"
        self.patterns = (
            Pattern([
                NotePosition(2, self.rootNote_index + 2),
                NotePosition(3, self.rootNote_index + 0),
                NotePosition(5, self.rootNote_index + 1),
            ]),
        )

class Chord_Minor6(Chord):
    def __init__(self, root_note:Note) -> None:
        super().__init__(root_note, 6)
        self.name = "6e Mineur"
        self.structure = [0, 3, 7, 9]
        self.sound = "Melancholic / Jazz"
        self.patterns = (
            Pattern([
                NotePosition(2, self.rootNote_index + 2),
                NotePosition(3, self.rootNote_index + 0),
                NotePosition(5, self.rootNote_index + 2),
            ]),
            Pattern([
                NotePosition(2, self.rootNote_index + 2),
                NotePosition(3, self.rootNote_index + 4),
                NotePosition(4, self.rootNote_index + 5),
                NotePosition(5, self.rootNote_index + 2),
            ]),
        )

class Chord_9(Chord):
    def __init__(self, root_note:Note) -> None:
        super().__init__(root_note, 5)
        self.name = "9e"
        self.structure = [0, 4, 7, 10, 14]
        self.sound = "Rich / Funky"
        self.patterns = (
            Pattern([
                NotePosition(1, self.rootNote_index + 1),
                NotePosition(2, self.rootNote_index + 1),
                NotePosition(3, self.rootNote_index + 0),
                NotePosition(4, self.rootNote_index + 1),
            ]),
        )

class Chord_Major9(Chord):
    def __init__(self, root_note:Note) -> None:
        super().__init__(root_note, 5)
        self.name = "9e Majeur"
        self.structure = [0, 4, 7, 11, 14]
        self.sound = "Lush / Dreamy"
        self.patterns = (
            Pattern([
                NotePosition(1, self.rootNote_index + 1),
                NotePosition(2, self.rootNote_index + 2),
                NotePosition(3, self.rootNote_index + 0),
                NotePosition(4, self.rootNote_index + 1),
            ]),
            Pattern([
                NotePosition(2, self.rootNote_index + 0),
                NotePosition(3, self.rootNote_index + 2),
                NotePosition(4, self.rootNote_index + 0),
                NotePosition(5, self.rootNote_index + 1),
            ]),
        )

class Chord_Minor9(Chord):
    def __init__(self, root_note:Note) -> None:
        super().__init__(root_note, 6)
        self.name = "9e Mineur"
        self.structure = [0, 3, 7, 10, 14]
        self.sound = "Deep / Smooth"
        self.patterns = (
            Pattern([
                NotePosition(1, self.rootNote_index + 2),
                NotePosition(2, self.rootNote_index + 2),
                NotePosition(3, self.rootNote_index + 0),
                NotePosition(4, self.rootNote_index + 2),
            ]),
            Pattern([
                NotePosition(2, self.rootNote_index + 1),
                NotePosition(3, self.rootNote_index + 2),
                NotePosition(4, self.rootNote_index + 0),
                NotePosition(5, self.rootNote_index + 2),
            ]),
        )

# FRETBOARD

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

def duplicate_fretboard(fretboard:list[list]) -> list[list]:
    return copy.deepcopy(fretboard)

def show_fretboard(fretboard:list[list[Note]]):
    display = ""
    note_width = 6
    fret_width = len(fretboard[0])

    # Index
    for i in range(fret_width):
        if LEFT_HANDED:
            display = f"{i}".ljust(note_width) + display
        else:
            display += f"{i}".ljust(note_width)
    display += '\n'

    # Notes
    for i in range(len(fretboard)):
        chord = fretboard[i]

        # Left-handed
        if LEFT_HANDED:
            chord.reverse()

        for note in chord:
            display += fill_text(note.name, note_width)

        # Reverse back
        if LEFT_HANDED:
            chord.reverse()

        display += "\n"

    print(display)

def visible_length(text):
    return len(ansi_escape.sub('', text))

def fill_text(text, width):
    space_to_add = width - visible_length(text)
    return text + " " * space_to_add

def adjust_root_for_ostring(root_index: int, string_offset: int = 4) -> int:
    """
    Adjust root note index relative to the low E string (or any string offset),
    wrapping around modulo 12.
    """
    return (root_index - string_offset) % 12

# # # # # # # # # # # # # # # # # #

# Highlight key's notes

show_fretboard(Chord_Sus2(Note('Fa')).patterns[1].apply())
