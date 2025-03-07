import os
os.environ["PATH"] += os.pathsep + r"C:\Users\drump\ffmpeg\ffmpeg-7.1-essentials_build\bin"

from pydub import AudioSegment
AudioSegment.ffmpeg = r"C:\Users\drump\ffmpeg\ffmpeg-7.1-essentials_build\bin\ffmpeg.exe"
AudioSegment.ffprobe = r"C:\Users\drump\ffmpeg\ffmpeg-7.1-essentials_build\bin\ffprobe.exe"

import librosa

# THIS IS THE ORIGINAL PROOF OF CONCEPT. CAN BE TESTED BY MANUALLY ADDING FILE PATHS AND EXECUTING THIS FILE

def chop_into_4_bar_segments(input_audio_path, output_prefix="segment"):
    """
    Automatically detects beats in an audio file using librosa,
    then slices it into 4-bar (16-beat) segments and exports them as MP3 files.
    """

    # 1. Load audio with librosa (mono=True for analysis).
    #    sr=None uses the file’s native sample rate.
    print("Loading audio...")
    y, sr = librosa.load(input_audio_path, sr=None, mono=True)

    # 2. Detect tempo and beat frames
    print("Detecting beats...")
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

    # --- FIX: Convert tempo to float if it's an array ---
    if hasattr(tempo, "__len__"):
        # E.g., if tempo is array([120.0]), get the first element
        tempo = float(tempo[0])

    print(f"Estimated tempo (BPM): {tempo:.2f}")

    if len(beat_frames) == 0:
        print("No beats detected. Exiting.")
        return

    # 3. Convert beat frames to times in seconds
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    # 4. In 4/4, 4 bars = 16 beats
    beats_per_4_bars = 16

    # -- Need to skip any bars at the beginning? 1 bar = 4 beats
    beats_to_skip = 7

    # 5. Load audio using pydub for slicing/export (keep full fidelity)
    full_audio = AudioSegment.from_file(input_audio_path)

    # Creates the folder
    base_name = os.path.splitext(input_audio_path)[0]
    output_folder = base_name + "_chopped"
    os.makedirs(output_folder, exist_ok=True)

    # 6. Slice in 16-beat chunks
    segment_count = 0
    for i in range(beats_to_skip, len(beat_times), beats_per_4_bars):
        start_sec = beat_times[i]

        if i + beats_per_4_bars < len(beat_times):
            end_sec = beat_times[i + beats_per_4_bars]
        else:
            # Last chunk might be shorter
            track_duration_sec = len(full_audio) / 1000.0
            if i + 1 < len(beat_times):
                end_sec = beat_times[-1]
            else:
                end_sec = track_duration_sec

        # Convert to ms for pydub
        start_ms = start_sec * 1000
        end_ms = end_sec * 1000

        segment_audio = full_audio[start_ms:end_ms]
        segment_count += 1

        # Save each chop into the "my_input_song_chopped" folder
        output_filename = os.path.join(output_folder, f"{output_prefix}_{segment_count}.mp3")
        segment_audio.export(output_filename, format="mp3", bitrate="192k")
        print(f"Exported segment {segment_count}: {output_filename}")

    print("All segments exported!")

if __name__ == "__main__":
    # Change these to suit your needs:
    input_audio_file = "Beetlegeuse.mp3"       # <--- rename your input file for each song youre chopping
    output_prefix_name = "chop"          # <--- prefix for each output MP3

    chop_into_4_bar_segments(input_audio_file, output_prefix=output_prefix_name)
