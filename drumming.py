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


class NoteGenerator:
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
    def _expand_counts(counts: tuple[NoteLength, NoteLength]) -> Generator[LengthPattern, None, None]:
        """Yield the combinations for a given number of note types."""
        singles, doubles = counts
        n_notes = singles + doubles
        for positions in it.combinations(range(n_notes), doubles):
            notes = [1] * n_notes
            for position in positions:
                notes[position] = 2
            yield notes

    def all_combos(self) -> Generator[LengthPattern, None, None]:
        """Yield all combinations for a total length."""
        yield from it.chain.from_iterable(self._expand_counts(counts) for counts in self._note_counts())

    @staticmethod
    def _item_to_string(combo: LengthPattern, separator: str, mapping: NoteMapping) -> PatternString:
        """Change a combination to a string. Default mapping is `SYMBOLS`."""
        return separator.join(mapping[note] for note in combo)

    def as_string(
            self,
            combos: Iterator[LengthPattern],
            separator: str = " ",
            mapping: Optional[NoteMapping] = None,
    ) -> Generator[PatternString, None, None]:
        """Change a sequence of note lengths to a string."""
        if mapping is None:
            mapping = SYMBOLS
        yield from (self._item_to_string(combo, separator, mapping) for combo in combos)

    def __iter__(self) -> Generator[PatternString, None, None]:
        yield from self.as_string(self.all_combos())

    def __getitem__(self, start: Union[slice, int], stop: Optional[int] = None, step: int = 1):
        if stop is not None:
            return next(it.islice(self, start, stop, step))
        if isinstance(start, slice):
            yield from it.islice(self, start.start, start.stop, start.step)
        else:
            return next(it.islice(self, start, start+1, step))

    def head(self, n: int = 5) -> list[PatternString]:
        return list(self[:n])

    def choice(self, n_choices: int = 1) -> list[PatternString]:
        """
        Choose a list of random notes.

        Notes
        -----
        This exhausts the generator. It has to generate every single combination first.

        """
        return random.choices(list(self), k=n_choices)


if __name__ == "__main__":
    ...
