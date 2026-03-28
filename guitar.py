        # Guitar stuff #

# Modules
import re
import os
import copy
import time
from typing import List, Tuple, Type

# TMP
os.system('cls')

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
    '9m':   13 %12,
    '9M':   14 %12,
    '11J':  17 %12,
    '11#':  18 %12,
    '13m':  20 %12,
    '13M':  21 %12,
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

STRINGS_OFFSETS = {
    0:4,
    1:11,
    2:7,
    3:2,
    4:9,
    5:4,
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

    def get_distance(self) -> int:
        min_string = STRINGS_OFFSETS.get(self.chord, 0)
        return self.fret - min_string

class ChordPosition:
    def __init__(self, root_note:Note, notes_position:list[NotePosition]) -> None:
        self.root_note = root_note
        self.notes_position = notes_position

        # Adjust notes position (handle root_note index + margin)
        self.adjustNotesPosition()

    def get_notes(self) -> list[NotePosition]:
        return self.notes_position

    def adjustNotesPosition(self):
        octave_shift = False

        # Apply shifting based on route note
        for note in self.notes_position:

            min_string = STRINGS_OFFSETS.get(note.chord, 0)
            target = (note.fret + self.root_note.index) % 12

            if target < min_string:
                target += 12

            note.fret = target

        # Fix layout
        while self.get_max_space_between_notes() > 6:

            # Shift by an octave lowest note
            for n in self.notes_position:
                d = n.get_distance() % 12
                if d < 6:
                    n.fret+=12

    def get_max_space_between_notes(self) -> int:
        distances = []
        for n in self.notes_position:
            distances.append(n.get_distance())
        return max(distances) - min(distances)


class Pattern:
    def __init__(self, notes:list[NotePosition] | list[Note] | ChordPosition) -> None:
        if isinstance(notes, ChordPosition):
            # Get notes
            self.notes = notes.get_notes()
            self.kind = NotePosition
        else:
            self.notes = notes
            self.kind = type(notes[0])

    def apply(self, row_notes_limit=1) -> list[list[Note]]:

        if row_notes_limit == 0:
            row_notes_limit = len(FRETBOARD[0])

        # Apply pattern to a new returned fretboard
        F = duplicate_fretboard(FRETBOARD)

        # Check kind
        if self.kind == NotePosition:
            # For each note to place
            for n in self.notes:
                counter = 0
                if isinstance(n, NotePosition):
                    # For each note in row
                    for note in F[n.chord]:
                        # If note's index matches
                        if n.fret == note.index:
                            if counter < row_notes_limit:
                                note.highlight = True
                                counter += 1

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

class Chord:
    def __init__(self, root_note:Note, string_offset=4) -> None:
        self.rootNote = root_note
        self.name = f"{root_note._name} "
        self.structure = [] # Refers to Major Scale // Semitones
        self.sound = ""
        self.patterns: Tuple[Pattern, ...] = () # Chord chart

class Key:
    def __init__(self, baseNote:Note) -> None:
        self.baseNote = baseNote
        self.name = "DEFAULT NAME VALUE"
        self.architecture = []
        self.sound = "DEFAULT SOUND VALUE"
        self.degrees_quality = [] # To define for each scale

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

    def get_degrees_quality(self) -> List[Tuple[Type[Chord], ...]]:
        # Calculate each degree's quality based on the scale's architecture
        degrees = []
        for i in range(len(self.architecture)):
            fd = i
            third = (i+2)
            fith = (i+4)
            i3 = get_interval(self.architecture, fd, third)
            i5 = get_interval(self.architecture, third, fith)
            # print(f"{fd} >>{i3}<< {third} >>{i5}<< {fith}")

            if i3 == 2.0 and i5 == 1.5:
                quality = MAJOR_CHORDS
            elif i3 == 1.5 and i5 == 2:
                quality = MINOR_CHORDS
            elif i3 == 1.5 and i5 == 1.5:
                quality = DIMINISHED_CHORDS
            else:
                print('Unknown interval :', i3, i5)

            degrees.append(quality)

        return degrees

    def build_chord(self, degree:int) -> list[Chord]:
        if not (1 <= degree <= 7):
            raise ValueError("Degree out of range (1-7) :", degree)

        l = []

        # Get FD of the degree
        f = self.get_notes()[degree-1]

        list_of_chords = self.get_degrees_quality()[degree-1]
        for chord in list_of_chords:
            l.append(chord(f))

        return l

    def get_all_chords(self) -> list[list[Chord]]:
        """
        Returns : list of 7 degrees, each degree containing all the associated chords
        """
        degrees_chords = []

        for degree_i in range(1, len(self.architecture)+1):
            # Number of notes = number of intervals in the architecture
            degrees_chords.append(
                self.build_chord(degree_i)
            )
            # print('Getting chords of degree : ', degree_i)

        return degrees_chords

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
    def __init__(self, name:str, key:Note, patterns:list[Pattern]=[], tempo=90) -> None:
        self.name = name
        self.key = key
        self.patterns = patterns
        self.tempo = tempo

    def addPattern(self, pattern:Pattern):
        self.patterns.append(pattern)

    def play(self):
        for pattern in self.patterns:
            os.system('cls')
            show_fretboard(pattern.apply())
            time.sleep(1.0)

class Chord_Major(Chord):
    def __init__(self, root_note:Note) -> None:
        super().__init__(root_note)
        self.name += "Majeur"
        self.structure = [0, 4, 7]
        self.sound = "Happy"
        self.patterns = (
            # Pattern 1
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(0, INTERVALS['FD']),
                NotePosition(1, INTERVALS['5J']),
                NotePosition(2, INTERVALS['3M']),
                NotePosition(3, INTERVALS['FD']),
                NotePosition(4, INTERVALS['5J']),
                NotePosition(5, INTERVALS['FD']),
            ])),
            # Pattern 2
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(0, INTERVALS['5J']),
                NotePosition(1, INTERVALS['3M']),
                NotePosition(2, INTERVALS['FD']),
                NotePosition(3, INTERVALS['5J']),
                NotePosition(4, INTERVALS['FD']),
            ])),
        )

class Chord_Minor(Chord):
    def __init__(self, root_note:Note) -> None:
        super().__init__(root_note)
        self.name += "Mineur"
        self.structure = [0, 3, 7]
        self.sound = "Sad"
        self.patterns = (
            # Pattern 1
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(0, INTERVALS['FD']),
                NotePosition(1, INTERVALS['5J']),
                NotePosition(2, INTERVALS['3m']),
                NotePosition(3, INTERVALS['FD']),
                NotePosition(4, INTERVALS['5J']),
                NotePosition(5, INTERVALS['FD']),
            ])),
            # Pattern 2
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(0, INTERVALS['5J']),
                NotePosition(1, INTERVALS['3m']),
                NotePosition(2, INTERVALS['FD']),
                NotePosition(3, INTERVALS['5J']),
                NotePosition(4, INTERVALS['FD']),
            ])),
        )

class Chord_Major7(Chord):
    def __init__(self, root_note:Note) -> None:
        super().__init__(root_note)
        self.name += "7e Majeur"
        self.structure = [0, 4, 7, 11]
        self.sound = "Smooth / Jazzy"
        self.patterns = (
            # Pattern 1
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(0, INTERVALS['FD']),
                NotePosition(1, INTERVALS['5J']),
                NotePosition(2, INTERVALS['3M']),
                NotePosition(3, INTERVALS['7M']),
                NotePosition(4, INTERVALS['5J']),
                NotePosition(5, INTERVALS['FD']),
            ])),
            # Pattern 2
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(0, INTERVALS['5J']),
                NotePosition(1, INTERVALS['3M']),
                NotePosition(2, INTERVALS['7M']),
                NotePosition(3, INTERVALS['5J']),
                NotePosition(4, INTERVALS['FD']),
            ])),
        )

class Chord_Minor7(Chord):
    def __init__(self, root_note:Note) -> None:
        super().__init__(root_note)
        self.name += "7e Mineur"
        self.structure = [0, 3, 7, 10]
        self.sound = "Soft / Bluesy"
        self.patterns = (
            # Pattern 1
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(0, INTERVALS['FD']),
                NotePosition(1, INTERVALS['5J']),
                NotePosition(2, INTERVALS['3m']),
                NotePosition(3, INTERVALS['7m']),
                NotePosition(4, INTERVALS['5J']),
                NotePosition(5, INTERVALS['FD']),
            ])),
            # Pattern 2
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(0, INTERVALS['5J']),
                NotePosition(1, INTERVALS['3m']),
                NotePosition(2, INTERVALS['7m']),
                NotePosition(3, INTERVALS['5J']),
                NotePosition(4, INTERVALS['FD']),
            ])),
        )

class Chord_Sus2(Chord):
    def __init__(self, root_note:Note) -> None:
        super().__init__(root_note, 5)
        self.name += "Sus2"
        self.structure = [0, 2, 7]
        self.sound = "Open / Floating"
        self.patterns = (
            # Pattern 1
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(0, INTERVALS['FD']),
                NotePosition(1, INTERVALS['5J']),
                NotePosition(2, INTERVALS['2M']),
                NotePosition(3, INTERVALS['FD']),
                NotePosition(4, INTERVALS['5J']),
                NotePosition(5, INTERVALS['FD']),
            ])),
            # Pattern 2
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(0, INTERVALS['5J']),
                NotePosition(1, INTERVALS['2M']),
                NotePosition(2, INTERVALS['FD']),
                NotePosition(3, INTERVALS['5J']),
                NotePosition(4, INTERVALS['FD']),
            ])),
        )

class Chord_Sus4(Chord):
    def __init__(self, root_note:Note) -> None:
        super().__init__(root_note)
        self.name += "Sus4"
        self.structure = [0, 5, 7]
        self.sound = "Tension / Suspended"
        self.patterns = (
            # Pattern 1
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(0, INTERVALS['FD']),
                NotePosition(1, INTERVALS['5J']),
                NotePosition(2, INTERVALS['4J']),
                NotePosition(3, INTERVALS['FD']),
                NotePosition(4, INTERVALS['5J']),
                NotePosition(5, INTERVALS['FD']),
            ])),
            # Pattern 2
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(0, INTERVALS['5J']),
                NotePosition(1, INTERVALS['4J']),
                NotePosition(2, INTERVALS['FD']),
                NotePosition(3, INTERVALS['5J']),
                NotePosition(4, INTERVALS['FD']),
            ])),
        )

class Chord_Major6(Chord):
    def __init__(self, root_note:Note) -> None:
        super().__init__(root_note, 5)
        self.name += "6e Majeur"
        self.structure = [0, 4, 7, 9]
        self.sound = "Warm / Stable"
        self.patterns = (
            # Pattern 1
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(2, INTERVALS['3M']),
                NotePosition(3, INTERVALS['6M']),
                NotePosition(5, INTERVALS['FD']),
            ])),
        )

class Chord_Minor6(Chord):
    def __init__(self, root_note:Note) -> None:
        super().__init__(root_note, 6)
        self.name += "6e Mineur"
        self.structure = [0, 3, 7, 9]
        self.sound = "Melancholic / Jazz"
        self.patterns = (
            # Pattern 1
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(2, INTERVALS['3m']),
                NotePosition(3, INTERVALS['6M']),
                NotePosition(5, INTERVALS['FD']),
            ])),
        )

class Chord_9(Chord):
    def __init__(self, root_note:Note) -> None:
        super().__init__(root_note, 5)
        self.name += "9e"
        self.structure = [0, 4, 7, 10, 14]
        self.sound = "Rich / Funky"
        self.patterns = (
            # Pattern 1
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(1, INTERVALS['9M']),
                NotePosition(2, INTERVALS['7m']),
                NotePosition(3, INTERVALS['3M']),
                NotePosition(4, INTERVALS['FD']),
            ])),
        )

class Chord_Major9(Chord):
    def __init__(self, root_note:Note) -> None:
        super().__init__(root_note, 5)
        self.name += "9e Majeur"
        self.structure = [0, 4, 7, 11, 14]
        self.sound = "Lush / Dreamy"
        self.patterns = (
            # Pattern 1
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(1, INTERVALS['9M']),
                NotePosition(2, INTERVALS['7M']),
                NotePosition(3, INTERVALS['3M']),
                NotePosition(4, INTERVALS['FD']),
            ])),
            # Pattern 2
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(2, INTERVALS['9M']),
                NotePosition(3, INTERVALS['7M']),
                NotePosition(4, INTERVALS['3M']),
                NotePosition(5, INTERVALS['FD']),
            ])),
        )

class Chord_Minor9(Chord):
    def __init__(self, root_note:Note) -> None:
        super().__init__(root_note)
        self.name += "9e Mineur"
        self.structure = [0, 3, 7, 10, 14]
        self.sound = "Deep / Smooth"
        self.patterns = (
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(1, INTERVALS['9M']),
                NotePosition(2, INTERVALS['7m']),
                NotePosition(3, INTERVALS['3m']),
                NotePosition(4, INTERVALS['FD']),
            ])),
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(2, INTERVALS['9M']),
                NotePosition(3, INTERVALS['7m']),
                NotePosition(4, INTERVALS['3m']),
                NotePosition(5, INTERVALS['FD']),
            ])),
        )

class Chord_Diminished(Chord):
    def __init__(self, root_note: Note) -> None:
        super().__init__(root_note)
        self.name += " Dim"
        self.structure = [0, 3, 6, 9]
        self.sound = "Tense / Dark"
        self.patterns = (
        )

class Chord_HalfDiminished(Chord):
    def __init__(self, root_note: Note) -> None:
        super().__init__(root_note)
        self.name += "ø7"
        self.structure = [0, 3, 6, 10]
        self.sound = "Mellow / Tense"
        self.patterns = (
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
for n_chord in range(len(FRETBOARD)):
    for i in range(1, FRETBOARD_LENGTH):
        initial_note = FRETBOARD[n_chord][0].index
        next_note = Note(initial_note + i)
        FRETBOARD[n_chord].append(next_note)

# CHORDS LIST
MAJOR_CHORDS = (
    Chord_Major,
    Chord_Major6,
    Chord_Major7,
    Chord_Major9,
    Chord_Sus2,
    Chord_Sus4
)

MINOR_CHORDS = (
    Chord_Minor,
    Chord_Minor6,
    Chord_Minor7,
    Chord_Minor9,
    Chord_Sus2,
    Chord_Sus4,
)

DIMINISHED_CHORDS = (
    Chord_Diminished,
    Chord_HalfDiminished,
)

# Functions
def get_interval(architecture:list[int], n1:int, n2:int):
    s = 0
    begin = n1
    for i in range(n2-n1):
        s += architecture[(begin+i) % 7]

    return s/2

def duplicate_fretboard(fretboard:list[list]) -> list[list[Note]]:
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

# # # # # # # # # # # # # # # # # #

gamme = IonanKey(Note('Do'))
for degree in gamme.get_all_chords():
    for chord in degree:
        print(chord.name)
        pass
    print('---')