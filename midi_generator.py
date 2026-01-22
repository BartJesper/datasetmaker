import pretty_midi
import random


def build_chord(
        chord_intervals: list,
        scale_degree_index: int,
        extended_scale: list,
        root_pitch: int,
        current_time: float,
        duration: float,
        instrument: pretty_midi.Instrument
):
    """Adding every note in a chord to the given instrument."""
    for interval in chord_intervals:
        pitch = root_pitch + extended_scale[scale_degree_index + interval]

        note = pretty_midi.Note(
            velocity=100,
            pitch=pitch,
            start=current_time,
            end=current_time + duration
        )
        instrument.notes.append(note)


def generate_note(
        current_time: float,
        duration: float,
        rest_prob: float,
        base_scale: list,
        extended_scale: list,
        chord_types: list,
        root_pitch: int,
        instrument: pretty_midi.Instrument
) -> float:
    """Generates a random note, chord or rest within the given length and scale."""
    if random.randrange(0, 100) / 100 < rest_prob:
        return current_time + duration

    # Generate random chord_type
    chord_type = random.choice(chord_types)

    # Pick a random scale degree (0-6 for the 7 notes in base scale)
    scale_degree_index = random.randint(0, len(base_scale) - 1)

    # Build the chord based on the chord type
    if chord_type == "single":
        # Play root note
        pitch = root_pitch + base_scale[scale_degree_index]
        note = pretty_midi.Note(
            velocity=100,
            pitch=pitch,
            start=current_time,
            end=current_time + duration
        )
        instrument.notes.append(note)

    elif chord_type == "triad":
        # Build a triad: root, third, fifth (scale degrees 0, 2, 4)
        chord_intervals = [0, 2, 4]
        build_chord(chord_intervals, scale_degree_index, extended_scale, root_pitch, current_time, duration, instrument)

    elif chord_type == "seventh":
        # Build a seventh: root, third, fifth, seventh (scale degrees 0, 2, 4, 6)
        chord_intervals = [0, 2, 4, 6]
        build_chord(chord_intervals, scale_degree_index, extended_scale, root_pitch, current_time, duration, instrument)

    elif chord_type == "ninth":
        # Build a ninth: root, third, fifth, seventh, ninth (scale degrees 0, 2, 4, 6, 8)
        chord_intervals = [0, 2, 4, 6, 8]
        build_chord(chord_intervals, scale_degree_index, extended_scale, root_pitch, current_time, duration, instrument)

    return current_time + duration


def generate_perfect_midi(
        bpm: int,
        key_root: str,
        is_major: bool,
        note_divisions: list,
        chord_types: list,
        instruments: list,
        octave_ranges: dict,
        length_bars: int,
        outfile: str,
        rest_prob: float = 0.15
):
    """Generate a perfect midi within the key."""
    pm = pretty_midi.PrettyMIDI(initial_tempo=bpm)

    # Key and scale selection
    key_map = {
        "C": 0, "C#": 1, "D": 2, "D#": 3,
        "E": 4, "F": 5, "F#": 6, "G": 7,
        "G#": 8, "A": 9, "A#": 10, "B": 11
    }
    key_offset = key_map[key_root]

    major_scale = [0, 2, 4, 5, 7, 9, 11]
    minor_scale = [0, 2, 3, 5, 7, 8, 10]
    base_scale = major_scale if is_major else minor_scale

    # Extend the scale to cover enough octaves for ninth chords
    extended_scale = base_scale + [note + 12 for note in base_scale] + [note + 24 for note in base_scale]

    # Note division selection
    division_map = {
        "whole": 4,
        "half": 2,
        "quarter": 1,
        "eighth": 1 / 2,
        "sixteenth": 1 / 4,
        "quarter_triplet": 2,
        "eighth_triplet": 1
    }

    seconds_per_beat = 60 / bpm

    for inst_name in instruments:
        instrument = pretty_midi.Instrument(
            program=pretty_midi.instrument_name_to_program(inst_name)
        )

        # Get octave range for this instrument
        octave_range = octave_ranges.get(inst_name, {"min": 0, "max": 1})
        octave_min = octave_range["min"]
        octave_max = octave_range["max"]

        # Pick a random octave within the allowed range for this instrument
        # C4 is MIDI note 60, so we use 60 + (octave * 12) as base
        random_octave = random.randint(octave_min, octave_max)
        root_pitch = 60 + (random_octave * 12) + key_offset

        current_time = 0.0
        # Generate notes bar-by-bar
        for _ in range(length_bars):
            beats_left = 4  # 4/4 bar

            while beats_left > 0:
                # Pick random note subdivision
                division = random.choice(note_divisions)
                beat_length = division_map[division]

                # Prevent overfilling the bar
                while beat_length > beats_left:
                    division = random.choice(note_divisions)
                    beat_length = division_map[division]

                duration = beat_length * seconds_per_beat

                # Handle triplet notes
                if division in ("quarter_triplet", "eighth_triplet"):
                    triplet_beat = beat_length / 3
                    triplet_duration = triplet_beat * seconds_per_beat

                    for _ in range(3):
                        current_time = generate_note(current_time, triplet_duration, rest_prob, base_scale,
                                                     extended_scale, chord_types, root_pitch, instrument)

                    beats_left -= beat_length
                    continue

                current_time = generate_note(current_time, duration, rest_prob, base_scale, extended_scale,
                                             chord_types, root_pitch, instrument)
                beats_left -= beat_length

        pm.instruments.append(instrument)

    pm.write(outfile)
    return pm


def humanize_midi(
        pm: pretty_midi.PrettyMIDI,
        bpm: int,
        timing_jitter_ms: int = 30,
        vel_noise: int = 20
):
    """Humanize the midi file."""
    imperfect = pretty_midi.PrettyMIDI(initial_tempo=bpm)

    for inst in pm.instruments:
        new_inst = pretty_midi.Instrument(program=inst.program)

        for note in inst.notes:
            # Timing jitter
            jitter = random.uniform(-timing_jitter_ms / 1000, timing_jitter_ms / 1000)

            start = max(0, note.start + jitter)
            end = max(start + 0.05, note.end + jitter)

            # Velocity variation
            offset = random.randint(-vel_noise, vel_noise)
            velocity = min(127, max(20, note.velocity + offset))

            new_inst.notes.append(
                pretty_midi.Note(
                    velocity=velocity,
                    pitch=note.pitch,
                    start=start,
                    end=end
                )
            )

        imperfect.instruments.append(new_inst)

    return imperfect
