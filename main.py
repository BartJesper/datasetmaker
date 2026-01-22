import sys
import random
from pathlib import Path
from audio_generator import generate_sample

# All different datasets and their parameters.
DATASETS = {
    "default": (                       # Default dataset, no alterations.
        ["whole", "half", "quarter"],  # Lengths of notes.
        ["single"],                    # Types of chords or combinations of notes.
        0.1,                           # Amount of rest: 0.1 -> 10%.
        ["Acoustic Grand Piano"],      # List of all instruments that play simultaneously.
    ),
    "note_medium": (                   # Medium difficulty notes, contains eighth and sixteenth notes.
        ["whole", "half", "quarter", "eighth", "sixteenth"],
        ["single"],
        0.1,
        ["Acoustic Grand Piano"],
    ),
    "note_hard": (                     # Hard difficulty notes, contains triples on top of the medium.
        ["whole", "half", "quarter", "eighth", "sixteenth", "quarter_triplet", "eighth_triplet"],
        ["single"],
        0.1,
        ["Acoustic Grand Piano"],
    ),
    "chords_medium": (                 # Medium difficulty chords, adds triad chords.
        ["whole", "half", "quarter"],
        ["single", "triad"],
        0.1,
        ["Acoustic Grand Piano"],
    ),
    "chords_hard": (                   # Hard difficulty chords, adds seventh chords on top of the medium.
        ["whole", "half", "quarter"],
        ["single", "triad", "seventh"],
        0.1,
        ["Acoustic Grand Piano"],
    ),
    "rest_medium": (                   # Medium difficulty rest, adds 0.3 chance on rests.
        ["whole", "half", "quarter"],
        ["single"],
        0.3,
        ["Acoustic Grand Piano"],
    ),
    "rest_hard": (                     # Hard difficulty rest, adds 0.6 chance on rests.
        ["whole", "half", "quarter"],
        ["single"],
        0.6,
        ["Acoustic Grand Piano"],
    ),
}

# The octave range for the instruments.
OCTAVE_RANGE = {
    "Acoustic Grand Piano": {
        "min": 0,
        "max": 1
    },
}

# Different tonics for the keys, only accept sharps, no flats.
KEYS = [
    "C", "C#", "D", "D#",
    "E", "F", "F#", "G",
    "G#", "A", "A#", "B"
]


def make_unique_folder(base_dir: Path, name: str) -> Path:
    """Create a uniquely named folder."""
    folder = base_dir / name
    count = 1
    while folder.exists():
        folder = base_dir / f"{name}({count})"
        count += 1

    folder.mkdir(parents=True)
    return folder


def main():
    if len(sys.argv) < 2:
        print("Usage: main.py <total_amount> <path (optional)>")
        return

    total_amount = int(sys.argv[1])
    base = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.cwd()

    datasets_root = make_unique_folder(base, "datasets")

    # Proportions: 80% Train, 10% Validation, 10% Test
    train_count = int(total_amount*0.8)
    val_count = int(total_amount*0.1)
    test_count = total_amount - train_count - val_count

    splits = [("train", train_count), ("validation", val_count), ("test", test_count)]

    # Start generating per dataset.
    for ds_name, params in DATASETS.items():
        note_divisions, chords, rest_prob, instruments = params
        ds_dir = datasets_root / f"dataset_{ds_name}"

        print(f"Generating {ds_name}...")
        for split_name, split_limit in splits:
            # Directory
            split_dir = ds_dir / split_name
            split_dir.mkdir(parents=True, exist_ok=True)

            # Start generating samples.
            for i in range(1, split_limit + 1):
                # Sample parameters
                bpm = random.randint(80, 150)
                key = random.choice(KEYS)
                is_major = random.choice([True, False])

                generate_sample(
                    bpm=bpm,
                    key=key,
                    is_major=is_major,
                    note_divisions=note_divisions,
                    chord_types=chords,
                    instruments=instruments,
                    octave_ranges=OCTAVE_RANGE,
                    length_bars=4,
                    out_dir=split_dir,
                    sample_name=f"sample-{i:03d}",
                    rest_prob=rest_prob
                )

    print(f"\n✔ DONE — datasets generated in: {datasets_root}")


if __name__ == '__main__':
    main()
