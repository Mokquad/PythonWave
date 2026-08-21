import argparse
import math
import random
import struct
import wave

SAMPLE_RATE = 44100
STEPS_PER_CHORD = 16
NUM_CHORDS = 4
TOTAL_STEPS = STEPS_PER_CHORD * NUM_CHORDS

NOTE_FREQS = {
    "C": 130.81, "C#": 138.59, "D": 146.83, "D#": 155.56, "E": 164.81,
    "F": 174.61, "F#": 185.00, "G": 196.00, "G#": 207.65, "A": 220.00,
    "A#": 233.08, "B": 246.94
}
NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")

SCALES = {
    "Minor": (0, 2, 3, 5, 7, 8, 10),
    "Major": (0, 2, 4, 5, 7, 9, 11)
}

PROGRESSIONS = (
    (0, 5, 2, 6),
    (0, 3, 4, 5),
    (0, 4, 5, 3),
    (5, 3, 0, 4)
)

def get_note_by_steps(root_freq, steps):
    return root_freq * (2 ** (steps / 12))

def synth_saw(freq, duration, volume=0.2, pluck=True):
    num_samples = int(SAMPLE_RATE * duration)
    if freq == 0:
        return [0] * num_samples

    samples = []
    period = SAMPLE_RATE / freq
    for i in range(num_samples):
        val = 2.0 * ((i % period) / period) - 1.0
        env = (num_samples - i) / num_samples if (pluck and i > num_samples * 0.1) else 1.0
        samples.append(int(val * 32767 * volume * env))
    return samples

def synth_kick(duration):
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        freq = 45 + (160 - 45) * math.exp(-70 * t)
        val = math.sin(2 * math.pi * freq * t)
        env = math.exp(-18 * t)
        samples.append(int(val * 32767 * 0.70 * env))
    return samples

def synth_snare(duration):
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        noise = random.uniform(-1.0, 1.0)
        tone = math.sin(2 * math.pi * 170 * t) * 0.4
        val = noise + tone
        env = math.exp(-22 * t)
        samples.append(int(val * 32767 * 0.35 * env))
    return samples

def generate_chords(root_freq, scale_name, prog_pattern):
    scale_intervals = SCALES[scale_name]
    chords_frequencies = []

    for step in prog_pattern:
        chord_root_step = scale_intervals[step % len(scale_intervals)]
        chord_root_freq = get_note_by_steps(root_freq, chord_root_step)
        
        is_minor_chord = "Minor" in scale_name if step in (0, 3, 4) else "Major" in scale_name
        third_step = 3 if is_minor_chord else 4

        f1 = chord_root_freq
        f2 = get_note_by_steps(chord_root_freq, third_step)
        f3 = get_note_by_steps(chord_root_freq, 7)
        chords_frequencies.append((f1, f2, f3))

    return chords_frequencies

def generate_procedural_melody(chords):

    one_bar_pattern = []
    current_chord_note_idx = 0
    last_played_idx = -1
    
    rhythm_templates = (
        (1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0),
        (1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0),
        (1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0)
    )
    selected_rhythm = random.choice(rhythm_templates)
    
    for step_in_bar in range(STEPS_PER_CHORD):
        if step_in_bar == 0:
            one_bar_pattern.append(("chord", 0))  
            current_chord_note_idx = 0
            last_played_idx = 0
        else:
            if selected_rhythm[step_in_bar] == 1:
                step_direction = random.choice([-1, 1])
                current_chord_note_idx += step_direction
                
                if current_chord_note_idx > 2:
                    current_chord_note_idx = 0
                elif current_chord_note_idx < 0:
                    current_chord_note_idx = 2
                
                if current_chord_note_idx == last_played_idx:
                    current_chord_note_idx = (current_chord_note_idx + 1) % 3
                
                last_played_idx = current_chord_note_idx
                
                if random.random() < 0.15:
                    one_bar_pattern.append(("accent", current_chord_note_idx))
                else:
                    one_bar_pattern.append(("note", current_chord_note_idx))
            else:
                one_bar_pattern.append(("rest", 0))
                
    melody_notes = []
    for step in range(TOTAL_STEPS):
        step_in_bar = step % STEPS_PER_CHORD
        note_type, note_idx = one_bar_pattern[step_in_bar]
        
        chord_idx = step // STEPS_PER_CHORD
        current_chord = chords[chord_idx]
        
        if note_type == "chord":
            melody_notes.append(("chord", current_chord))
        elif note_type == "note":
            melody_notes.append(("note", current_chord[note_idx] * 2))
        elif note_type == "accent":
            melody_notes.append(("accent", current_chord[note_idx] * 4))
        else:
            melody_notes.append(("rest", 0))
            
    return melody_notes

def export_midi(chords, melody_structure, bpm, filename):
    try:
        from miditime.MIDITime import MIDITime
    except ImportError:
        print("Error: Install MIDI Time for MIDI Exporting!")
        return

    midi_output = MIDITime(bpm, filename)
    midinotes = []
    current_time = 0.0

    for step, (note_type, value) in enumerate(melody_structure):
        if step % 2 == 0:
            midinotes.append([current_time, 40, 100, 0.25])
            
        if note_type == "note":
            midinotes.append([current_time, 64, 90, 0.25])
        elif note_type == "accent":
            midinotes.append([current_time, 76, 90, 0.25])
            
        current_time += 0.25

    midi_output.add_track(midinotes)
    midi_output.save_midi()
    print(f"MIDI file saved as: {filename}")

def main():
    parser = argparse.ArgumentParser(
        description="Generate Chiptune (Electronic) Music in Terminal.."
    )
    parser.add_argument("-s", "--save-as", default="0.wav")
    parser.add_argument("-m", "--midi", nargs="?", const="0.mid")
    parser.add_argument("-b", "--bpm", type=int, default=125)
    args = parser.parse_args()

    step_duration = 60 / args.bpm / 4
    num_step_samples = int(SAMPLE_RATE * step_duration)

    root_name = random.choice(NOTE_NAMES)
    root_freq = NOTE_FREQS[root_name]
    scale_name = random.choice(list(SCALES.keys()))
    prog_pattern = random.choice(PROGRESSIONS)

    print(f"Key: {root_name} {scale_name} | Tempo: {args.bpm} BPM")

    chords = generate_chords(root_freq, scale_name, prog_pattern)
    melody_structure = generate_procedural_melody(chords)

    master_length = int(SAMPLE_RATE * step_duration * TOTAL_STEPS)
    lead_track = [0] * master_length
    bass_track = [0] * master_length
    drum_track = [0] * master_length

    for step in range(TOTAL_STEPS):
        chord_idx = step // STEPS_PER_CHORD
        current_chord = chords[chord_idx]
        root_bass_freq = current_chord[0] / 2
        start_sample = int(step * SAMPLE_RATE * step_duration)
        step_in_bar = step % 16

        is_kick = step_in_bar in (0, 4, 8, 12)
        is_snare = step_in_bar in (4, 12)
        drum_samples = [0] * num_step_samples

        if is_kick and is_snare:
            k_part = synth_kick(step_duration)
            s_part = synth_snare(step_duration)
            drum_samples = [int((k + s) * 0.65) for k, s in zip(k_part, s_part)]
        elif is_kick:
            drum_samples = synth_kick(step_duration)
        elif is_snare:
            drum_samples = synth_snare(step_duration)

        if step_in_bar % 2 == 0:
            bass_samples = synth_saw(root_bass_freq, step_duration, volume=0.22, pluck=False)
        else:
            bass_samples = [0] * num_step_samples

        note_type, note_value = melody_structure[step]
        
        if note_type == "chord":
            s1 = synth_saw(note_value[0] * 2, step_duration, volume=0.15)
            s2 = synth_saw(note_value[1] * 2, step_duration, volume=0.15)
            s3 = synth_saw(note_value[2] * 2, step_duration, volume=0.15)
            lead_samples = [x + y + z for x, y, z in zip(s1, s2, s3)]
        elif note_type == "note":
            lead_samples = synth_saw(note_value, step_duration, volume=0.28, pluck=True)
        elif note_type == "accent":
            lead_samples = synth_saw(note_value, step_duration, volume=0.24, pluck=True)
        else:
            lead_samples = [0] * num_step_samples

        for i in range(len(drum_samples)):
            if start_sample + i < master_length:
                drum_track[start_sample + i] = drum_samples[i]
                bass_track[start_sample + i] = bass_samples[i]
                lead_track[start_sample + i] = lead_samples[i]

    final_track = []
    for i in range(master_length):
        mixed_sample = lead_track[i] + bass_track[i] + drum_track[i]
        if mixed_sample > 32767:
            mixed_sample = 32767
        elif mixed_sample < -32768:
            mixed_sample = -32768
        final_track.append(mixed_sample)

    with wave.open(args.save_as, "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(struct.pack(f"<{len(final_track)}h", *final_track))
    
    print(f"Audio saved to: {args.save_as}")

    if args.midi:
        export_midi(chords, melody_structure, args.bpm, args.midi)

if __name__ == "__main__":
    main()
