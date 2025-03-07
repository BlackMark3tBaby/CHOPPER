import os
os.environ["PATH"] += os.pathsep + r"C:\Users\drump\ffmpeg\ffmpeg-7.1-essentials_build\bin"

from pydub import AudioSegment
AudioSegment.ffmpeg = r"C:\Users\drump\ffmpeg\ffmpeg-7.1-essentials_build\bin\ffmpeg.exe"
AudioSegment.ffprobe = r"C:\Users\drump\ffmpeg\ffmpeg-7.1-essentials_build\bin\ffprobe.exe"

import librosa

def chop_audio(
    input_audio_path,
    output_folder=None,
    chunk_type="bars",       # "bars" or "beats"
    chunk_size=4,            # e.g. 4 bars or 16 beats
    skip_type="bars",        # "bars" or "beats"
    skip_count=0,            # how many bars or beats to skip from the start
    output_prefix="segment",
    log_callback=print       # <-- function to handle log messages
):
    """
    Detect beats with librosa, then slice the audio in segments of a given length
    in bars or beats. Optionally skip some bars/beats at start. Exports MP3 slices.

    If log_callback is given, all messages will be passed to that function instead of print().
    """

    def log(msg):
        # Helper to call the log_callback
        log_callback(msg)

    # 1. Load audio for analysis
    log(f"Loading audio from: {input_audio_path}")
    y, sr = librosa.load(input_audio_path, sr=None, mono=True)

    log("Detecting beats...")
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

    # tempo might be an array
    if hasattr(tempo, "__len__"):
        tempo = float(tempo[0])

    log(f"Estimated tempo (BPM): {tempo:.2f}")

    if len(beat_frames) == 0:
        log("No beats detected. Exiting.")
        return

    # 2. Convert frames to times
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    # 3. Determine how many beats to skip
    beats_per_bar = 4  # for 4/4 time
    if skip_type == "bars":
        beats_to_skip = skip_count * beats_per_bar
    else:  # skip_type == "beats"
        beats_to_skip = skip_count

    # 4. Determine how many beats per chunk
    if chunk_type == "bars":
        beats_per_chunk = chunk_size * beats_per_bar
    else:  # chunk_type == "beats"
        beats_per_chunk = chunk_size

    # 5. Load audio in pydub for slicing
    full_audio = AudioSegment.from_file(input_audio_path)

    # Determine output folder
    if not output_folder:
        base_name = os.path.splitext(input_audio_path)[0]
        output_folder = base_name + "_chopped"

    os.makedirs(output_folder, exist_ok=True)
    log(f"Output folder: {output_folder}")

    # 6. Slice in increments
    segment_count = 0
    for i in range(beats_to_skip, len(beat_times), beats_per_chunk):
        start_sec = beat_times[i]

        # If there's enough leftover for a full chunk
        if i + beats_per_chunk < len(beat_times):
            end_sec = beat_times[i + beats_per_chunk]
        else:
            # Use last beat or track end
            track_duration_sec = len(full_audio) / 1000.0
            if i + 1 < len(beat_times):
                end_sec = beat_times[-1]
            else:
                end_sec = track_duration_sec

        start_ms = start_sec * 1000
        end_ms = end_sec * 1000

        segment_audio = full_audio[start_ms:end_ms]
        segment_count += 1

        output_filename = os.path.join(output_folder, f"{output_prefix}_{segment_count}.mp3")
        segment_audio.export(output_filename, format="mp3", bitrate="192k")
        log(f"Exported segment {segment_count} to: {output_filename}")

    log("All segments exported!")
