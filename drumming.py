import dataclasses
import itertools as it
import random
from typing import Generator, Iterator, Optional, Union


NoteLength = int
NoteString = str
PatternLength = int
PatternString = str
NoteMapping = dict[NoteLength, NoteString]
LengthPattern = list[NoteLength]
NotePattern = list[NoteString]


SYMBOLS: NoteMapping = {
    1: "·",
    2: "–",
}


@dataclasses.dataclass()
class NoteProperties:
    note_number: int
    velocity: int


DEFAULT_NOTE_NUMBER = 60
DEFAULT_NOTE_ACCENT = 127
DEFAULT_NOTE_NORMAL = 100
DEFAULT_NOTE_SOFT = 50


PROPERTIES = {
    SYMBOLS[1]: [NoteProperties(note_number=60, velocity=100)],
    SYMBOLS[2]: [NoteProperties(note_number=60, velocity=100), NoteProperties(note_number=60, velocity=50)],
}


class Synthesizer:
    pass


class Note:
    symbols: NoteMapping = {
        1: "·",
        2: "–",
    }

    def __init__(self, length, number=DEFAULT_NOTE_NUMBER):
        self.length = length
        self.number = number
        self.symbol = self.symbols[length]

    def __repr__(self):
        return f"Note({self.length}, {self.number})"

    def __str__(self):
        return self.symbol


class Pattern:
    def __init__(self, notes: Iterator[Note], *, separator: str = " ", synthesizer: Synthesizer=None):
        self.notes: list[Note] = list(notes)
        self.separator: str = separator
        self.synthesizer: Synthesizer = synthesizer

    def __repr__(self):
        return f"Pattern({self.notes})"

    def __str__(self):
        return self.separator.join(str(note) for note in self.notes)


class PatternGenerator:
    def __init__(self, pattern_length):
        self.pattern_length = pattern_length

    def __len__(self):
        return self.n_combos(self.pattern_length)

    @staticmethod
    def _fib(n: int) -> int:
        """Return the nth Fibonacci number."""
        phi = (5**0.5 + 1)/2
        return int((phi**n - (-phi)**(-n)) / 5**0.5)

    def n_combos(self, pattern_length: int) -> int:
        """Return the number of note combinations with a total length of `length`."""
        return self._fib(pattern_length + 1)

    def _note_counts(self) -> Generator[tuple[NoteLength, NoteLength], None, None]:
        """Yield the count combination of single and double notes with a total length of `length`."""
        yield from ((n_singles, n_doubles) for n_doubles, n_singles in enumerate(range(self.pattern_length, -1, -2)))

    @staticmethod
    def _expand_counts(counts: tuple[NoteLength, NoteLength]) -> Generator[Pattern, None, None]:
        """Yield the combinations for a given number of note types."""
        singles, doubles = counts
        n_notes = singles + doubles
        for positions in it.combinations(range(n_notes), doubles):
            notes = [Note(1)] * n_notes
            for position in positions:
                notes[position] = Note(2)
            yield Pattern(notes)

    def all_combos(self) -> Generator[Pattern, None, None]:
        """Yield all combinations for a total length."""
        yield from it.chain.from_iterable(self._expand_counts(counts) for counts in self._note_counts())

    @staticmethod
    def as_string(patterns: Iterator[Pattern]) -> Generator[PatternString, None, None]:
        yield from (str(pattern) for pattern in patterns)

    def __iter__(self) -> Generator[PatternString, None, None]:
        yield from self.as_string(self.all_combos())

    def __getitem__(self, start: Union[slice, int], stop: Optional[int] = None, step: int = 1):
        if stop is not None:
            return next(it.islice(self, start, stop, step))
        if isinstance(start, slice):
            yield from it.islice(self, start.start, start.stop, start.step)
        else:
            return next(it.islice(self, start, start+1, step))

    def head(self, n: int = 5) -> list[Pattern]:
        return list(self[:n])

    def choose(self, n_choices: int = 1) -> list[Pattern]:
        """
        Choose a list of random notes.

        Notes
        -----
        This exhausts the generator. It has to generate every single combination first.

        """
        return random.choices(list(self), k=n_choices)


if __name__ == "__main__":
    print(PatternGenerator(10).choose(5))
