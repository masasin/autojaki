import abc
import dataclasses as dc
import functools as ft
import itertools as it
import operator as op
import random
from typing import Generator, Iterator, Optional, Union


NoteRepresentations = str
NoteLength = int
NoteString = str
PatternLength = int
PatternString = str
DecodeMapping = dict[NoteLength, NoteString]
EncodeMapping = dict[NoteString, NoteLength]


class Note:
    representations: NoteRepresentations = "·–"

    def __init__(self, length: NoteLength, representations: NoteRepresentations = representations):
        self.length: NoteLength = length
        self.symbol: NoteString = self.decode_mapping(representations)[length]
        self._representations: NoteRepresentations = representations

    def __repr__(self) -> str:
        return f"Note({self.length})"

    def __str__(self) -> NoteString:
        return self.symbol

    @staticmethod
    def decode_mapping(representations: NoteRepresentations) -> DecodeMapping:
        return {length: string for length, string in enumerate(representations, start=1)}

    @staticmethod
    def encode_mapping(representations: NoteRepresentations) -> EncodeMapping:
        return {string: length for length, string in enumerate(representations, start=1)}

    @classmethod
    def from_string(
            cls,
            note_string: NoteString,
            representations: Optional[NoteRepresentations] = representations,
            display_default: bool = True,
    ) -> "Note":
        return cls(
            cls.encode_mapping(representations)[note_string],
            representations=cls.representations if display_default else representations,
        )

    @property
    def is_single(self) -> bool:
        return self.length == 1

    @property
    def is_double(self) -> bool:
        return self.length == 2


class Pattern:
    def __init__(self, notes: Iterator[Note], *, separator: str = ""):
        self.notes: list[Note] = list(notes)
        self.separator: str = separator

    def __iter__(self) -> Generator[Note, None, None]:
        yield from self.notes

    def __repr__(self) -> str:
        return f"Pattern({str(self)})"

    def __str__(self) -> PatternString:
        return self.separator.join(str(note) for note in self.notes)

    def __add__(self, other) -> "Pattern":
        if isinstance(other, Note):
            return Pattern(it.chain(self.notes, other))
        elif isinstance(other, Pattern):
            return Pattern(it.chain(self.notes, other.notes))

    @classmethod
    def from_string(
            cls,
            pattern_string: PatternString,
            representations: Optional[NoteRepresentations] = None,
            display_default: bool = True,
    ) -> "Pattern":
        return cls((
            Note.from_string(
                note_string,
                representations=representations,
                display_default=display_default
            )
            for note_string in pattern_string)
        )


class Patterns:
    def __init__(self, patterns: Iterator[Pattern], *, separator: str = ", "):
        self.patterns: Iterator[Pattern] = patterns
        self.separator: str = separator

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
    def __init__(self, pattern_length: PatternLength):
        self.pattern_length: PatternLength = pattern_length
        self.patterns: Patterns = self._all_patterns()

    def __len__(self) -> int:
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


@dc.dataclass
class SynthVelocities:
    accent: int = 127
    normal: int = 100
    soft: int = 50


@dc.dataclass
class Midi:
    voice: int = dc.field(repr=False)
    note_number: int
    velocity: int


class Synthesizer(abc.ABC):
    @abc.abstractmethod
    def play_pattern(self, pattern: Pattern) -> Generator:
        raise NotImplementedError

    @abc.abstractmethod
    def play_note(self, note: Note) -> Generator:
        raise NotImplementedError


class MidiSynthesizer(Synthesizer):
    def __init__(self, note_number: int = 60, velocities: SynthVelocities = SynthVelocities(), voice: int = 0):
        self.note_number = note_number
        self.velocities = velocities
        self.voice = voice

    def play_pattern(self, pattern: Pattern) -> Generator[Midi, None, None]:
        pattern_prev, pattern_curr = it.tee(pattern)
        first_note = next(pattern_curr)
        yield from self.play_note(first_note)
        for prev, curr in zip(pattern_prev, pattern_curr):
            yield from self.play_note(curr, follows_double=prev.is_double)

    def play_note(self, note: Note, follows_double: bool = False) -> Generator[Midi, None, None]:
        if note.is_single:
            velocity = self.velocities.accent if follows_double else self.velocities.normal
            yield Midi(voice=self.voice, note_number=self.note_number, velocity=velocity)
        elif note.is_double:
            yield Midi(voice=self.voice, note_number=self.note_number, velocity=self.velocities.normal)
            yield Midi(voice=self.voice, note_number=self.note_number, velocity=self.velocities.soft)


if __name__ == "__main__":
    print(f"Patterns repr: {PatternGenerator(5).head()!r}")
    print(" Patterns str:          ", PatternGenerator(5).head())
    print(f" Pattern repr: {PatternGenerator(5)[3]!r}")
    print("  Pattern str:        ", PatternGenerator(5)[3])
    print("Choice:", PatternGenerator(5).choose(5))
    print("Head: ", PatternGenerator(5).head())
    print(f"Join: {PatternGenerator(5).head().join()!r}")
    print()
    print("Midi stuff")
    print("----------")
    pattern = Pattern.from_string("_...__..", representations="._")
    synth = MidiSynthesizer()
    print("Playing", repr(pattern))
    for output in synth.play_pattern(pattern):
        print(output)
