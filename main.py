import argparse
import whisper

def seconds_to_srt_time(sec):
    """Convert seconds (float) to SRT time format (HH:MM:SS,mmm)"""
    hours = int(sec // 3600)
    minutes = int((sec % 3600) // 60)
    seconds = int(sec % 60)
    millis = int((sec - int(sec)) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"

def main():
    parser = argparse.ArgumentParser(
        description="Transcribe audio to SRT using Whisper with customizable words per subtitle"
    )
    parser.add_argument("audio_file", help="Path to the audio file (e.g. .mp3, .wav)")
    parser.add_argument(
        "--words-per-subtitle",
        type=int,
        default=0,
        help=(
            "Maximum number of words per subtitle line. "
            "If set to 0 (default), the entire segment text is used as a single subtitle."
        ),
    )
    args = parser.parse_args()

    # Load the Whisper model (choose model size like "base", "small", etc.)
    model = whisper.load_model("large")
    
    # Transcribe audio with detailed segments (each has a start time, end time, and text)
    result = model.transcribe(args.audio_file, verbose=True)
    segments = result.get("segments", [])
    
    srt_entries = []
    subtitle_counter = 1

    for seg in segments:
        seg_start = seg["start"]    # start time in seconds
        seg_end = seg["end"]        # end time in seconds
        seg_text = seg["text"].strip()

        if not seg_text:
            continue

        # If words_per_subtitle is not specified (or 0), use the whole segment.
        if args.words_per_subtitle <= 0:
            srt_entries.append(
                f"{subtitle_counter}\n{seconds_to_srt_time(seg_start)} --> {seconds_to_srt_time(seg_end)}\n{seg_text}\n"
            )
            subtitle_counter += 1
        else:
            # Otherwise, split the segment text into groups of up to the specified number of words.
            words = seg_text.split()
            num_words = len(words)
            total_duration = seg_end - seg_start

            for i in range(0, num_words, args.words_per_subtitle):
                group_words = words[i:i+args.words_per_subtitle]
                group_text = " ".join(group_words)
                # Calculate proportional timing within the segment.
                group_start = seg_start + (i / num_words) * total_duration
                group_end = seg_start + ((i + len(group_words)) / num_words) * total_duration

                srt_entries.append(
                    f"{subtitle_counter}\n{seconds_to_srt_time(group_start)} --> {seconds_to_srt_time(group_end)}\n{group_text}\n"
                )
                subtitle_counter += 1

    # Write SRT output to file.
    with open("output.srt", "w", encoding="utf-8") as f:
        f.write("\n".join(srt_entries))

    print("SRT file 'output.srt' created.")

if __name__ == "__main__":
    main()
