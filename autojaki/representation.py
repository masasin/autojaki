from collections import UserList
import functools as ft
import itertools as it
import operator as op
from typing import Generator, Iterator, Optional, Union, overload

from .helpers import (
    NoteRepresentations,
    NoteLength,
    NoteString,
    PatternString,
    DecodeMapping,
    EncodeMapping,
)


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


class Pattern(UserList):
    def __repr__(self) -> str:
        return f"Pattern({str(self)})"

    def __str__(self) -> PatternString:
        return "".join(str(note) for note in self.notes)

    @property
    def notes(self):
        return self.data

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

    @overload
    def __getitem__(self, index: slice) -> "Patterns": ...

    @overload
    def __getitem__(self, index: int) -> Pattern: ...

    def __getitem__(self, index: Union[slice, int]) -> Union["Patterns", Pattern]:
        try:
            return next(it.islice(self.patterns, index, index + 1))
        except TypeError:
            return Patterns(it.islice(self, index.start, index.stop, index.step))

    def __add__(self, other) -> "Patterns":
        if isinstance(other, Pattern):
            return Patterns(it.chain(self.patterns, other))
        elif isinstance(other, Patterns):
            return Patterns(it.chain(self.patterns, other.patterns))

    def join(self) -> Pattern:
        return ft.reduce(op.add, self)
