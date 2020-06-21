import itertools as it
import random
from typing import Generator, Union

from helpers import NoteLength, PatternLength
from representation import Note, Pattern, Patterns


class PatternGenerator:
    def __init__(self, pattern_length: PatternLength):
        self.pattern_length: PatternLength = pattern_length
        self.patterns: Patterns = self._all_patterns()

    def __len__(self) -> PatternLength:
        return self.n_combos(self.pattern_length)

    @staticmethod
    def _fib(n: int) -> int:
        """Return the nth Fibonacci number."""
        phi = (5**0.5 + 1)/2
        return int((phi**n - (-phi)**(-n)) / 5**0.5)

    def n_combos(self, pattern_length: PatternLength) -> int:
        """Return the number of note combinations with a total length of `length`."""
        return self._fib(pattern_length + 1)

    def _note_counts(self) -> Generator[tuple[NoteLength, NoteLength], None, None]:
        """Yield the count combination of single and double notes with a total length of `length`."""
        for n_doubles, n_singles in enumerate(range(self.pattern_length, -1, -2)):
            yield n_singles, n_doubles

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
        return self.patterns[index]

    def head(self, n: int = 5) -> Patterns:
        return self[:n]

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
