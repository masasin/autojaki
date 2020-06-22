import abc
import dataclasses as dc
import itertools as it
import time
from typing import Generator, Optional

from .representation import Note, Pattern


@dc.dataclass
class SynthVelocities:
    accent: int = 127
    normal: int = 100
    soft: int = 50


@dc.dataclass
class MidiNote:
    on_channel: int
    note_number: int
    velocity: int
    on_duration: float = 0.15
    off_channel: int = 0x80
    off_duration: float = 0.05

    def play(self, midi_out):
        note_on = [self.on_channel, self.note_number, self.velocity]
        note_off = [self.off_channel, self.note_number, self.velocity]
        midi_out.send_message(note_on)
        time.sleep(self.on_duration)
        midi_out.send_message(note_off)
        time.sleep(self.off_duration)


class Synthesizer(abc.ABC):
    @abc.abstractmethod
    def play_pattern(self, pattern: Pattern) -> Generator:
        raise NotImplementedError

    @abc.abstractmethod
    def play_note(self, note: Note) -> Generator:
        raise NotImplementedError


class FakeMidiSynthesizer(Synthesizer):
    def __init__(self, note_number: int = 60, velocities: SynthVelocities = SynthVelocities(), midi_channel: int = 0):
        self.note_number = note_number
        self.velocities = velocities
        self.midi_channel = midi_channel

    def play_pattern(self, pattern: Pattern) -> Generator[MidiNote, None, None]:
        pattern_prev, pattern_curr = it.tee(pattern)
        first_note = next(pattern_curr)
        yield from self.play_note(first_note)
        for prev, curr in zip(pattern_prev, pattern_curr):
            yield from self.play_note(curr, follows_double=prev.is_double)

    def play_note(self, note: Note, follows_double: bool = False) -> Generator[MidiNote, None, None]:
        if note.is_single:
            velocity = self.velocities.accent if follows_double else self.velocities.normal
            yield MidiNote(on_channel=self.midi_channel, note_number=self.note_number, velocity=velocity)
        elif note.is_double:
            yield MidiNote(on_channel=self.midi_channel, note_number=self.note_number, velocity=self.velocities.normal)
            yield MidiNote(on_channel=self.midi_channel, note_number=self.note_number, velocity=self.velocities.soft)


class MidiSynthesizer(Synthesizer):
    def __init__(
            self,
            note_number: int = 60,
            velocities: SynthVelocities = SynthVelocities(),
            midi_channel: int = 0x90,
            midi_port: Optional[int] = None,

    ):
        self.note_number = note_number
        self.velocities = velocities
        self.midi_channel = midi_channel
        self.midi_port = midi_port
        self._midi_out = None

    def play_pattern(self, pattern: Pattern) -> None:
        pattern_prev, pattern_curr = it.tee(pattern)
        first_note = next(pattern_curr)
        with rtimidi.MidiOut() as self._midi_out:
            self._midi_out.open_port(self.midi_port, use_virtual=True, interactive=False)

            self.play_note(first_note)
            for prev, curr in zip(pattern_prev, pattern_curr):
                self.play_note(curr, follows_double=prev.is_double)

    def play_note(self, note: Note, follows_double: bool = False) -> None:
        if note.is_single:
            velocity = self.velocities.accent if follows_double else self.velocities.normal
            MidiNote(
                on_channel=self.midi_channel,
                note_number=self.note_number,
                velocity=velocity
            ).play(self._midi_out)
        elif note.is_double:
            MidiNote(
                on_channel=self.midi_channel,
                note_number=self.note_number,
                velocity=self.velocities.normal
            ).play(self._midi_out)
            MidiNote(
                on_channel=self.midi_channel,
                note_number=self.note_number,
                velocity=self.velocities.soft
            ).play(self._midi_out)
