import gradio as gr
from music21 import chord, scale, note, stream, key
from midiutil import MIDIFile
import io
import random

def get_scales_for_chord(chord_name, song_key):
    # Simple mapping of chord types to compatible improv scales (jazz-inspired)
    chord_obj = chord.Chord(chord_name)
    root = chord_obj.root().name
    if chord_obj.isMajorTriad():
        return [f"{root} Ionian (Major)", f"{root} Lydian"]
    elif chord_obj.isMinorTriad():
        return [f"{root} Dorian", f"{root} Aeolian (Natural Minor)"]
    elif chord_obj.isDominantSeventh():
        return [f"{root} Mixolydian", f"{root} Altered Dominant"]
    else:
        return [f"{root} Major (default)"]

def generate_arpeggio_pattern(chord_name):
    # Generate a simple arpeggio pattern as notes
    ch = chord.Chord(chord_name)
    arpeggio = [n.nameWithOctave for n in ch.notes] + [ch.notes[0].transpose(12).nameWithOctave]  # Up and down
    return " -> ".join(arpeggio + arpeggio[::-1])

def generate_melody_idea(chords, song_key):
    # Generate a random simple melody based on scales over chords
    try:
        k = key.Key(song_key)
        melody_notes = []
        for ch in chords:
            sc = scale.MajorScale() if 'major' in song_key.lower() else scale.MinorScale()
            sc = sc.derive(chord.Chord(ch).root())
            pitches = sc.getPitches()[random.randint(0, 4):random.randint(5, 7)]  # Random segment
            melody_notes.extend([p.nameWithOctave for p in pitches])
        return " ".join(melody_notes)
    except:
        return "Could not generate melody—check key format (e.g., 'C major')."

def create_midi_exercise(chords):
    # Create a simple MIDI file with arpeggios over the chords
    midi = MIDIFile(1)
    track = 0
    time = 0
    midi.addTempo(track, time, 120)
    channel = 0
    volume = 100
    duration = 1  # Quarter note

    for ch_name in chords:
        ch = chord.Chord(ch_name)
        for pitch in ch.pitches:
            midi.addNote(track, channel, pitch.midi, time, duration, volume)
            time += duration
        time += duration * 2  # Pause

    binary_io = io.BytesIO()
    midi.writeFile(binary_io)
    binary_io.seek(0)
    return binary_io

def generate_exercises(chord_progression, song_key="C major"):
    chords = chord_progression.strip().split()
    if not chords:
        return "Please enter a chord progression."

    output = f"**Song Key:** {song_key}\n**Chord Progression:** {' '.join(chords)}\n\n"

    # Scales for improv
    output += "### Suggested Scales for Improvisation:\n"
    for ch in chords:
        scales = get_scales_for_chord(ch, song_key)
        output += f"- Over {ch}: {', '.join(scales)}\n"

    # Arpeggios
    output += "\n### Arpeggio Exercises (Practice in both hands, ascending/descending):\n"
    for ch in chords:
        arp = generate_arpeggio_pattern(ch)
        output += f"- For {ch}: {arp}\n"

    # Melody ideas
    melody_idea = generate_melody_idea(chords, song_key)
    output += f"\n### Simple Melody Improv Idea (Play over the progression):\n{melody_idea}\n\n"
    output += "Practice Tip: Start slow, loop the progression, and gradually add your own variations using the scales above."

    # MIDI file
    midi_file = create_midi_exercise(chords)

    return output, midi_file

# Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# Custom Piano Improv Exercise Generator")
    chord_input = gr.Textbox(label="Chord Progression (space-separated, e.g., 'C Am F G')")
    key_input = gr.Textbox(label="Song Key (e.g., 'C major' or 'A minor')", value="C major")
    generate_btn = gr.Button("Generate Exercises")
    output_text = gr.Markdown()
    midi_output = gr.File(label="Download MIDI Exercise File")

    generate_btn.click(generate_exercises, inputs=[chord_input, key_input], outputs=[output_text, midi_output])

demo.launch()
