from representation import Pattern
from generation import PatternGenerator
from synthesizers import MidiSynthesizer


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
    p = Pattern.from_string("_...__..", representations="._")
    synth = MidiSynthesizer()
    print("Playing", repr(p))
    for output in synth.play_pattern(p):
        print(output)
