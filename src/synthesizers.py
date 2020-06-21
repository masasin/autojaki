import abc
import dataclasses as dc
import itertools as it
from typing import Generator

from representation import Note, Pattern


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
