import pretty_midi
import soundfile as sf
from midi_generator import generate_perfect_midi, humanize_midi


def generate_sample(
        bpm,
        key,
        is_major,
        note_divisions,
        chord_types,
        instruments,
        octave_ranges,
        length_bars,
        out_dir,
        sample_name,
        rest_prob=0.1
):
    """Generates a single sample with midi and audio files."""
    midi_path = out_dir / f"{sample_name}.mid"
    audio_path = out_dir / f"{sample_name}.wav"

    # Generate MIDI data
    perfect_pm = generate_perfect_midi(
        bpm, key, is_major, note_divisions,
        chord_types, instruments, octave_ranges,
        length_bars, str(midi_path),
        rest_prob=float(rest_prob)
    )

    # Humanize the MIDI
    imperfect_pm = humanize_midi(perfect_pm, bpm)

    # Convert humanized MIDI to Audio using Fluidsynth
    audio = imperfect_pm.fluidsynth()
    sf.write(str(audio_path), audio, samplerate=44100)
