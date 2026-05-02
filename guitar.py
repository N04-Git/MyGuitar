        # Guitar stuff #

# Modules
import re
import os
import copy
from typing import Tuple
import pathlib
import zipfile
import xml.etree.ElementTree as ET

#### Constants

#Semitones:F    2m     2M    3m     3M    4j    5-     5j     6m      6M    7m     7M

        # 0            2            4           6             8             10
NOTES = ["Do", "Do#", "Ré", "Ré#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si"]
        #       1            3            5            7              9            11

EXISTING_NOTES = [
    "Do", "Do#", "Dob",
    "Ré", "Ré#", "Réb",
    "Mi", "Mi#", "Mib",
    "Fa", "Fa#", "Fab",
    "Sol", "Sol#", "Solb",
    "La", "La#", "Lab",
    "Si", "Si#", "Sib",
]

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

class Exercise:

    exercises = []

    def __init__(self, name:str, category:str, tablature:str) -> None:
        self.name = name
        self.category = category
        self.tablaturePath = 'exercises\\' + tablature
        Exercise.exercises.append(self)

    def to_dict(self) -> dict:
        d = {
            'name': self.name,
            'category': self.category,
            'tabPath': self.tablaturePath,
        }
        return d

class Note:
    def __init__(self, note:int|str) -> None:

        self._name = ''
        self.index = -1 # Can change over adjustements
        self.interval = None # Can change over adjustements
        self.highlight = 0 # No highlight by default
        self.initial_interval = -1 # Unset by default

        if type(note) == str:
            self._name = note
            self.index = NOTES_ID_BY_NAME.get(note, [])[0]

        elif type(note) == int:
            self.index = note
            self._name = NOTES[note % len(NOTES)]
            self.interval = list(INTERVALS.keys())[list(INTERVALS.values()).index(note % 12)]

        else:
            print('Note definition error !', note)

    @property
    def name(self):
        if self.highlight:
            return COLORS.get("GREEN", "") + self._name + COLORS.get("RESET", "")
        return self._name

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

    def to_dict(self):
        return {
            'name': self._name,
            'highlight': self.highlight,
            'index': self.index,
            'interval': self.interval,
            'initial_interval': self.initial_interval
        }

class NotePosition:
    def __init__(self, string:int, fret:int) -> None:
        self.chord = string
        self.fret = fret
        self.initialFret = fret

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

        # Apply pattern to a new fretboard
        F = duplicate_fretboard(FRETBOARD)

        # Check kind
        if self.kind == NotePosition: # POSITION (chord,note)
            # For each note to place
            for n in self.notes:
                counter = 0
                if isinstance(n, NotePosition):
                    # For each note in row
                    for note in F[n.chord]:
                        # If note's index matches, update its highlight status + set initial interval
                        if n.fret == note.index:
                            if counter < row_notes_limit:
                                note.highlight = n.fret
                                note.initial_interval = n.initialFret
                                counter += 1

        elif self.kind == Note: # Note
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

    def to_dict(self, row_notes_limit=1):
        f = self.apply(row_notes_limit)
        return fretboard_to_dict(f)

# Chords
class Chord:

    _existing_chords = []
    _id_counter = 0
    _instances_by_id = {}

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        Chord._existing_chords.append(cls)

    def __init__(self, root_note:Note) -> None:
        self.rootNote = root_note
        self.name = f"{root_note._name} "
        self.structure = [] # Refers to Major Scale // Semitones
        self.sound = ""
        self.patterns: Tuple[Pattern, ...] = () # Chord chart
        self.kind = 'UNSET' # Maj / Min / Dim / 7th / 6th

        # ID
        s = self.find_similar()
        if s:
            self.id = s.id
        else:
            self.id = self._id_counter
            Chord._id_counter += 1
            self._instances_by_id[self.id] = self

    def get_composing_notes(self) -> list[str]:
        n = []
        c = self.rootNote.index
        for interval in self.structure:
            next_note = Note(c + interval)
            n.append(next_note._name)

        return n

    def find_similar(self) -> "Chord | None":
        for chord in Chord._instances_by_id.values():
            if (chord.__class__ is self.__class__ and
                chord.rootNote._name == self.rootNote._name
            ):
                return chord
        return None

    def to_dict(self):
        d = {
            'name': self.name,
            'root': self.rootNote.to_dict(),
            'structure': self.structure,
            'kind': self.kind,
            'sound': self.sound,
            'id': self.id,
            'composing_notes': self.get_composing_notes(),
        }
        return d

    def get_chart(self, min_strings:int=6, min_frets:int=5) -> list[list[list]]:
        charts = []

        for p in self.patterns:
            f = fretboard_to_array(p.apply())

            # Exand frets by 3
            for row in f:
                for _ in range(3):
                    row.append((0, -1))

            rows = len(f)
            cols = len(f[0])

            # Find bounding box of highlighted notes
            min_row, max_row = rows, -1
            min_col, max_col = cols, -1
            for r in range(rows):
                for c in range(cols):
                    if f[r][c][0] != 0:
                        if r < min_row: min_row = r
                        if r > max_row: max_row = r
                        if c < min_col: min_col = c
                        if c > max_col: max_col = c

            if max_row == -1:  # no notes
                return []

            # Initialize slice indices
            start_row, end_row = min_row, max_row
            start_col, end_col = min_col, max_col

            # Pad columns to reach min_frets
            counter = 0
            while (end_col - start_col + 1) < min_frets:
                # Alternate left/right
                if (end_col - start_col + 1) % 2 == 0:
                    # Try Left
                    if start_col > 0:
                        start_col -= 1
                    else:
                        end_col += 1
                else:
                    # Try Right
                    if end_col < cols - 1:
                        end_col += 1
                    else:
                        start_col -= 1

                counter += 1
                if counter > 100:
                    raise ValueError('Error: chart cannot be created (1)')

            # Pad rows to reach min_strings
            counter = 0
            while (end_row - start_row + 1) < min_strings:
                # Alternate top/bottom
                if (end_row - start_row + 1) % 2 == 0:
                    if start_row > 0:
                        start_row -= 1
                    else:
                        end_row += 1
                else:
                    if end_row < rows - 1:
                        end_row += 1
                    else:
                        start_row -= 1

                counter += 1
                if counter > 100:
                    raise ValueError('Error: chart cannot be created (2)')

            # Slice the array
            charts.append([row[start_col:end_col+1] for row in f[start_row:end_row+1]])

        return charts

class Chord_Major(Chord):
    def __init__(self, root_note:Note) -> None:
        super().__init__(root_note)
        self.name += "M"
        self.structure = [0, 4, 7]
        self.sound = "Happy"
        self.kind = "Majeur"
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
        self.name += "m"
        self.structure = [0, 3, 7]
        self.sound = "Sad"
        self.kind = "Mineur"
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
        self.name += "Maj7"
        self.structure = [0, 4, 7, 11]
        self.kind = "7th"
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
        self.name += "Min7"
        self.kind = "7th"
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
        super().__init__(root_note)
        self.name += "Sus2"
        self.kind = "Sus"
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
        self.kind = "Sus"
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
        super().__init__(root_note)
        self.name += "Maj6"
        self.kind = "6th"
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
        super().__init__(root_note)
        self.name += "Min6"
        self.kind = "6th"
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
        super().__init__(root_note)
        self.name += "9e"
        self.kind = '9th'
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
        super().__init__(root_note)
        self.name += "Maj9"
        self.kind = "9th"
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
        self.name += "Min9"
        self.kind = "9th"
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
        self.name += "Dim"
        self.kind = "Dim"
        self.structure = [0, 3, 6]
        self.sound = "Tense / Dark"
        self.patterns = (
            # Pattern 1
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(1, INTERVALS['3m']),
                NotePosition(2, INTERVALS['FD']),
                NotePosition(3, INTERVALS['5-']),
                NotePosition(4, INTERVALS['FD']),
            ])),
        )

class Chord_Pow(Chord):
    def __init__(self, root_note: Note) -> None:
        super().__init__(root_note)
        self.name += "5"
        self.kind = "Pow"
        self.structure = [0, 7]
        self.sound = "Intense, Neutre"
        self.patterns = (
            # Pattern 1
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(3, INTERVALS['FD']),
                NotePosition(4, INTERVALS['5J']),
                NotePosition(5, INTERVALS['FD']),
            ])),
        )

class Chord_Triad_Maj(Chord):
    def __init__(self, root_note: Note) -> None:
        super().__init__(root_note)
        self.name += "M (tri)"
        self.kind = "Triad"
        self.structure = [0, 4, 7]
        self.sound = ""
        self.patterns = (
                    ### PATTERN F35 ###
            # Pattern F35 sur cordes 5/4/3
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(3, INTERVALS['5J']),
                NotePosition(4, INTERVALS['3M']),
                NotePosition(5, INTERVALS['FD']),
            ])),
            # Pattern F35 sur cordes 4/3/2
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(2, INTERVALS['5J']),
                NotePosition(3, INTERVALS['3M']),
                NotePosition(4, INTERVALS['FD']),
            ])),
            # Pattern F35 sur cordes 3/2/1
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(1, INTERVALS['5J']),
                NotePosition(2, INTERVALS['3M']),
                NotePosition(3, INTERVALS['FD']),
            ])),
            # Pattern F35 sur cordes 2/1/0
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(0, INTERVALS['5J']),
                NotePosition(1, INTERVALS['3M']),
                NotePosition(2, INTERVALS['FD']),
            ])),

                    ### PATTERN 35F ###
            # Pattern F35 sur cordes 5/4/3
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(3, INTERVALS['FD']),
                NotePosition(4, INTERVALS['5J']),
                NotePosition(5, INTERVALS['3M']),
            ])),
            # Pattern F35 sur cordes 4/3/2
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(2, INTERVALS['FD']),
                NotePosition(3, INTERVALS['5J']),
                NotePosition(4, INTERVALS['3M']),
            ])),
            # Pattern F35 sur cordes 3/2/1
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(1, INTERVALS['FD']),
                NotePosition(2, INTERVALS['5J']),
                NotePosition(3, INTERVALS['3M']),
            ])),
            # Pattern F35 sur cordes 2/1/0
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(0, INTERVALS['FD']),
                NotePosition(1, INTERVALS['5J']),
                NotePosition(2, INTERVALS['3M']),
            ])),

                    ### PATTERN 5F3 ###
            # Pattern F35 sur cordes 5/4/3
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(3, INTERVALS['3M']),
                NotePosition(4, INTERVALS['FD']),
                NotePosition(5, INTERVALS['5J']),
            ])),
            # Pattern F35 sur cordes 4/3/2
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(2, INTERVALS['3M']),
                NotePosition(3, INTERVALS['FD']),
                NotePosition(4, INTERVALS['5J']),
            ])),
            # Pattern F35 sur cordes 3/2/1
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(1, INTERVALS['3M']),
                NotePosition(2, INTERVALS['FD']),
                NotePosition(3, INTERVALS['5J']),
            ])),
            # Pattern F35 sur cordes 2/1/0
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(0, INTERVALS['3M']),
                NotePosition(1, INTERVALS['FD']),
                NotePosition(2, INTERVALS['5J']),
            ])),
        )

class Chord_Triad_Min(Chord):
    def __init__(self, root_note: Note) -> None:
        super().__init__(root_note)
        self.name += "m (tri)"
        self.kind = "Triad"
        self.structure = [0, 3, 7]
        self.sound = ""
        self.patterns = (
                    ### PATTERN F35 ###
            # Pattern F35 sur cordes 5/4/3
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(3, INTERVALS['5J']),
                NotePosition(4, INTERVALS['3m']),
                NotePosition(5, INTERVALS['FD']),
            ])),
            # Pattern F35 sur cordes 4/3/2
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(2, INTERVALS['5J']),
                NotePosition(3, INTERVALS['3m']),
                NotePosition(4, INTERVALS['FD']),
            ])),
            # Pattern F35 sur cordes 3/2/1
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(1, INTERVALS['5J']),
                NotePosition(2, INTERVALS['3m']),
                NotePosition(3, INTERVALS['FD']),
            ])),
            # Pattern F35 sur cordes 2/1/0
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(0, INTERVALS['5J']),
                NotePosition(1, INTERVALS['3m']),
                NotePosition(2, INTERVALS['FD']),
            ])),

                    ### PATTERN 35F ###
            # Pattern F35 sur cordes 5/4/3
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(3, INTERVALS['FD']),
                NotePosition(4, INTERVALS['5J']),
                NotePosition(5, INTERVALS['3m']),
            ])),
            # Pattern F35 sur cordes 4/3/2
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(2, INTERVALS['FD']),
                NotePosition(3, INTERVALS['5J']),
                NotePosition(4, INTERVALS['3m']),
            ])),
            # Pattern F35 sur cordes 3/2/1
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(1, INTERVALS['FD']),
                NotePosition(2, INTERVALS['5J']),
                NotePosition(3, INTERVALS['3m']),
            ])),
            # Pattern F35 sur cordes 2/1/0
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(0, INTERVALS['FD']),
                NotePosition(1, INTERVALS['5J']),
                NotePosition(2, INTERVALS['3m']),
            ])),

                    ### PATTERN 5F3 ###
            # Pattern F35 sur cordes 5/4/3
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(3, INTERVALS['3m']),
                NotePosition(4, INTERVALS['FD']),
                NotePosition(5, INTERVALS['5J']),
            ])),
            # Pattern F35 sur cordes 4/3/2
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(2, INTERVALS['3m']),
                NotePosition(3, INTERVALS['FD']),
                NotePosition(4, INTERVALS['5J']),
            ])),
            # Pattern F35 sur cordes 3/2/1
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(1, INTERVALS['3m']),
                NotePosition(2, INTERVALS['FD']),
                NotePosition(4, INTERVALS['5J']),
            ])),
            # Pattern F35 sur cordes 2/1/0
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(0, INTERVALS['3m']),
                NotePosition(1, INTERVALS['FD']),
                NotePosition(2, INTERVALS['5J']),
            ])),
        )

"""
        >> Chord Template <<

class Chord_MinorSus2(Chord):
    def __init__(self, root_note: Note) -> None:
        super().__init__(root_note)
        self.name += ""
        self.kind = ""
        self.structure = []
        self.sound = ""
        self.patterns = (
            Pattern(ChordPosition(self.rootNote, [
                NotePosition(1, INTERVALS['']),
                NotePosition(2, INTERVALS['']),
                NotePosition(3, INTERVALS['']),
                NotePosition(4, INTERVALS['']),
            ])),
        )
"""

# Keys
class Key:
    def __init__(self, baseNote:Note) -> None:

        if not isinstance(baseNote, Note):
            raise ValueError('Cannot instanciate from this value : ', baseNote)

        self.baseNote = baseNote
        self.name = "DEFAULT NAME VALUE"
        self.architecture = []
        self.sound = "DEFAULT SOUND VALUE"
        self.relative = (0, "DEFAULT VALUE")

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

    def get_degrees_quality(self) -> list[tuple[Chord]]:
        scale_notes = self.get_notes()
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
                quality = []

            instances = tuple(c(scale_notes[i]) for c in quality)
            degrees.append(instances)

        return degrees

    def build_chord(self, degree:int) -> tuple[Chord]:
        if not (1 <= degree <= 7):
            raise ValueError("Degree out of range (1-7) :", degree)

        list_of_chords = self.get_degrees_quality()

        return list_of_chords[degree-1]

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

    def get_fretboard(self, length=15) -> list[list[Note]]:

        # New fretboard, key notes
        F = duplicate_fretboard(FRETBOARD)
        N = self.get_notes()

        # Fretboard length
        index = len(F[0]) - length
        if LEFT_HANDED:
            F = [row[:length] for row in F]
        else:
            F = [row[index:] for row in F]

        # Highlight all fretboard's notes in common
        for row in F:
            for noteObj in row:
                n_id = noteObj.index % 12
                for keyNote in N:
                    if keyNote.index % 12 == n_id:
                        noteObj.highlight = 999

        return F

    def to_dict(self) -> dict:

        notes = [n._name for n in self.get_notes()]
        degrees = [[chord.to_dict() for chord in degree] for degree in self.get_degrees_quality()]

        d = {
            'baseNote': self.baseNote._name,
            'name': self.name,
            'architecture': self.architecture,
            'sound': self.sound,
            'notes': notes,
            'degrees_quality': degrees,
            'fretboard_key': fretboard_to_dict(self.get_fretboard()),
            'relative': self.relative
        }
        return d

class IonanKey(Key):
    def __init__(self, baseNote) -> None:
        super().__init__(baseNote)
        self.name = "Ionan"
        self.altName = "Major"
        self.architecture = [2, 2, 1, 2, 2, 2, 1]
        self.sound = "Happy, Bright, Stable"
        self.relative = (5, 'aeolien')

class AeolianKey(Key):
    def __init__(self, baseNote) -> None:
        super().__init__(baseNote)
        self.name = "Aeolian Key"
        self.altName = "Natural Minor"
        self.architecture = [2, 1, 2, 2, 1, 2, 2]
        self.sound = "Sad"
        self.relative = (2, 'ionien')

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

# CHORDS
MAJOR_CHORDS = (
    Chord_Major,
    Chord_Major6,
    Chord_Major7,
    Chord_Major9,
    Chord_Sus2,
    Chord_Sus4,
    Chord_Pow,
    Chord_Triad_Maj,
)

MINOR_CHORDS = (
    Chord_Minor,
    Chord_Minor6,
    Chord_Minor7,
    Chord_Minor9,
    Chord_Sus2,
    Chord_Sus4,
    Chord_Pow,
    Chord_Triad_Min,
)

DIMINISHED_CHORDS = (
    Chord_Diminished,
)

# KEYS
KEYS_BY_NAME = {
    'ionien':   IonanKey,
    'aeolien':  AeolianKey,
}

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

def fretboard_to_dict(fretboard: list[list[Note]]) -> list[dict]:
    # Returns a dict containing
    result = []

    fret_width = len(fretboard[0])

    # Header (fret indices)
    frets = list(range(fret_width))
    if LEFT_HANDED:
        frets = frets[::-1]

    result.append({
        "type": "header",
        "frets": frets
    })

    # Notes
    for row in fretboard:
        row_data = []

        # Handle left-handed
        notes = list(row[::-1] if LEFT_HANDED else row)

        for note in notes:
            row_data.append(note.to_dict())

        result.append({
            "type": "row",
            "notes": row_data
        })

    return result

def visible_length(text):
    return len(ansi_escape.sub('', text))

def fill_text(text, width):
    space_to_add = width - visible_length(text)
    return text + " " * space_to_add

def get_key(mode:str, key:str) -> Key|None:
    m = KEYS_BY_NAME.get(mode, '')
    if m:
        # Check note
        if key in EXISTING_NOTES:
            return m(Note(key)).to_dict()

    return None

def get_chart(chord_id: int) -> list:

    # Find chord instance
    chord = Chord._instances_by_id.get(chord_id, None)
    if isinstance(chord, Chord):
        # Get charts of chord
        return chord.get_chart()

    return []

def get_chord_fretboard(chord_id:int):

    # Find chord instance
    chord = Chord._instances_by_id.get(chord_id, None)
    if isinstance(chord, Chord):
        return [fretboard_to_dict(f.apply()) for f in chord.patterns]
    print('Unknown chord id', chord, 'within list :', Chord._instances_by_id)
    return []

def get_exercies(category:str, sorting:str, prefix:str) -> list:
    # Get all exercises
    exercises = [e.to_dict() for e in Exercise.exercises]
    filtered = []
    # Sort
    for e in exercises:
        # Check category
        if category != 'all':
            if category != e['category']:
                continue

        # Check prefix
        if prefix.strip() != '':
            if not (prefix.lower().strip()) in str(e['name']).lower().strip():
                continue

        filtered.append(e)

    return filtered

def fretboard_to_array(fretboard: list[list[Note]]) -> list[list[tuple[int, int]]]:
    ## DEPRECATED (USED ONLY BY CHORD PATTERN...) >> USE 'fretboard_to_dict' instead

    # Returns an array containing note's highlight and note's interval
    if LEFT_HANDED:
        array = [[(int(note.highlight), (note.initial_interval)) for note in reversed(row)] for row in fretboard]
    else:
        array = [[(int(note.highlight), (note.initial_interval)) for note in row] for row in fretboard]
    return array

def get_chords(prefix:str, kind:str) -> list:
    # Get all chords

    results = []

    for note in EXISTING_NOTES:
        root = Note(note)

        for c in Chord._existing_chords:
            chord = c(root)

            if prefix and prefix.lower() not in chord.name.lower():
                continue

            if kind and chord.kind != kind:
                continue

            results.append(chord.to_dict())

    return results

def parse_gpfile(gpfile_path:pathlib.Path) -> dict:
    try:
        with zipfile.ZipFile(gpfile_path, 'r') as z:
            with z.open('Content/score.gpif') as f:
                tree = ET.parse(f)
                root = tree.getroot()

                score = root.find('Score')
                if score is None:
                    return {}

                def get(tag):
                    el = score.find(tag)
                    return el.text.strip() if el is not None and el.text else None

                return {
                    "title": get("Title"),
                    "subtitle": get("SubTitle"),
                    "artist": get("Artist"),
                    "album": get("Album"),
                    "words": get("Words"),
                    "music": get("Music"),
                    "words_and_music": get("WordsAndMusic"),
                    "tabber": get("Tabber"),
                    "copyright": get("Copyright"),
                    "filepath": str('/gpfile/tabs/'+gpfile_path.name),
                }

    except Exception as e:
        print(f"Error parsing {gpfile_path}: {e}")
        return {}

def get_tabs(prefix:str, sort:str) -> list:
    results = []

    tabsPath = pathlib.Path("./gpfile/tabs")

    if not tabsPath.exists():
        print('Error: tabs path does not exist !')
        return []

    files = [x for x in tabsPath.glob('**/*') if x.is_file()]

    for f in files:
        s = parse_gpfile(f)

        p = prefix.strip().lower()
        haystack = f"{s.get('title') or ''} {s.get('artist') or ''}".lower()

        if not p or p in haystack:
            results.append(s)

    return results

def merge_fretboards(f1:list[dict], f2:list[dict]) -> list:
    # Copy all highlighted notes from f1 (=pattern) to f2 (=base)

    for i in range(len(f1)):
        f1_value = f1[i]
        f2_value = f2[i]

        if f1_value['type'] == 'row' and f2_value['type'] == 'row':
            # Check highlighted notes in f1
            f1_notes = f1_value['notes']
            f2_notes = f2_value['notes']

            if LEFT_HANDED:
                minimum = min(len(f1_notes), len(f2_notes))

                for j in range(minimum):
                    f1_note = f1_notes[-minimum+j]
                    f2_note = f2_notes[-minimum+j]
                    if f1_note['highlight']:
                        f2_note['highlight'] = f1_note['highlight']

    return f2

def get_chord_key_fretboard(chord_id: int, key:str, mode:str) -> list:
    # Get fretboard with key notes highlight + chord notes highlight

    # Key fretboard
    try:
        f1 = fretboard_to_dict(KEYS_BY_NAME[mode](Note(key)).get_fretboard())
    except (KeyError, ValueError):
        print('Incorrect key/mode :', key, mode)
        return []

    # Chord fretboard
    f2 = get_chord_fretboard(chord_id)

    # Merge f1 & f2
    if f1 and f2:
        merged = [merge_fretboards(copy.deepcopy(f2_i), copy.deepcopy(f1)) for f2_i in f2]
        return merged

    print('Error: f1 or f2 undefined !')
    return []

# # # # # # # # # # # # # # # # # #

# Build all chords
CHORD_CACHE = {}
def build_all_chords():
    if CHORD_CACHE:
        return CHORD_CACHE

    for note in EXISTING_NOTES:
        for cls in Chord._existing_chords:
            c = cls(Note(note))
            CHORD_CACHE[c.id] = c

    return CHORD_CACHE
build_all_chords()

if __name__ == '__main__':
    pass