import dataclasses
import functools as ft
import itertools as it
import operator as op
import random
from typing import Generator, Iterator, Union


NoteLength = int
NoteString = str
NoteMapping = dict[NoteLength, NoteString]


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

    def __init__(self, length):
        self.length = length
        self.symbol = self.symbols[length]

    def __repr__(self) -> str:
        return f"Note({self.length})"

    def __str__(self) -> NoteString:
        return self.symbol


class Pattern:
    def __init__(self, notes: Iterator[Note], *, separator: str = ""):
        self.notes: Iterator[Note] = notes
        self.separator: str = separator

    def __iter__(self) -> Generator[Note, None, None]:
        yield from self.notes

    def __repr__(self) -> str:
        return f"Pattern({str(self)})"

    def __str__(self) -> str:
        return self.separator.join(str(note) for note in self.notes)

    def __add__(self, other) -> "Pattern":
        if isinstance(other, Note):
            return Pattern(it.chain(self.notes, other))
        elif isinstance(other, Pattern):
            return Pattern(it.chain(self.notes, other.notes))


class Patterns:
    def __init__(self, patterns: Iterator[Pattern], *, separator: str = ", "):
        self.patterns: Iterator[Pattern] = patterns
        self.separator = separator

    def __repr__(self) -> str:
        return f"Patterns([{str(self)}])"

    def __str__(self) -> str:
        return self.separator.join(str(pattern) for pattern in self)

    def __iter__(self) -> Generator[Pattern, None, None]:
        yield from self.patterns
    
    def __add__(self, other) -> "Patterns":
        if isinstance(other, Pattern):
            return Patterns(it.chain(self.patterns, other))
        elif isinstance(other, Patterns):
            return Patterns(it.chain(self.patterns, other.patterns))

    def join(self) -> Pattern:
        return ft.reduce(op.add, self)


class PatternGenerator:
    def __init__(self, pattern_length):
        self.pattern_length = pattern_length
        self.patterns = self._all_patterns()

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
    def _generate_pattern(counts: tuple[NoteLength, NoteLength]) -> Generator[Pattern, None, None]:
        """Yield the combinations for a given number of note types."""
        singles, doubles = counts
        n_notes = singles + doubles
        for positions in it.combinations(range(n_notes), doubles):
            notes = [Note(1)] * n_notes
            for position in positions:
                notes[position] = Note(2)
            yield Pattern(notes)

    def _all_patterns(self) -> Patterns:
        return Patterns(it.chain.from_iterable(self._generate_pattern(counts) for counts in self._note_counts()))

    def __iter__(self) -> Generator[Pattern, None, None]:
        yield from self.patterns

    def __getitem__(self, index: Union[slice, int]) -> Union[Patterns, Pattern]:
        try:
            return next(it.islice(self.patterns, index, index + 1))
        except TypeError:
            return Patterns(it.islice(self, index.start, index.stop, index.step))

    def head(self, n: int = 5) -> Patterns:
        return Patterns(self[:n])

    def choose(self, n_choices: int = 1) -> Patterns:
        """
        Choose a list of random notes.

        Notes
        -----
        This exhausts the generator. It has to generate every single combination first.

        """
        return Patterns(random.choices(list(self), k=n_choices))

    def reset(self) -> None:
        self.patterns = self._all_patterns()


if __name__ == "__main__":
    print(f"Patterns repr: {PatternGenerator(5).head()!r}")
    print(" Patterns str:          ", PatternGenerator(5).head())
    print(f" Pattern repr: {PatternGenerator(5)[3]!r}")
    print("  Pattern str:        ", PatternGenerator(5)[3])
    print("Choice:", PatternGenerator(5).choose(5))
    print("Head: ", PatternGenerator(5).head())
    print(f"Join: {PatternGenerator(5).head().join()!r}")
