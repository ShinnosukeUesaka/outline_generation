from pathlib import Path

import openai

client = openai.OpenAI()


def extract_timestamps(music_path: Path) -> str:
    """Transcribe music with word-level timestamps using OpenAI gpt-4o-transcribe.

    Returns a string of "text (start-end)\n" lines.
    """
    with open(music_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="verbose_json",
            timestamp_granularities=["word"],
        )

    timestamped_words = ""
    for word in transcription.words:
        timestamped_words += f"{word.word} ({word.start}-{word.end})\n"

    print(f"Extracted words with timestamps:\n{timestamped_words}")
    return timestamped_words


def align_lyrics(plain_lyrics: str, timestamped_words: str) -> str:
    """Align original lyrics with extracted timestamps using OpenAI."""
    alignment_prompt = f"""You are given:
1. Original lyrics (accurate text but no timestamps)
2. Extracted transcript with timestamps (timestamps are accurate but text may have errors)

Your task is to align the original lyrics with the timestamps from the extracted transcript.

Original lyrics:
{plain_lyrics}

Extracted transcript with timestamps:
{timestamped_words}

Please return a JSON array where each element contains:
- "text": the original lyric line/phrase
- "start": start timestamp in seconds
- "end": end timestamp in seconds

Match the original lyrics to the closest timestamps from the extracted transcript."""

    alignment_completion = client.chat.completions.create(
        model="gpt-5.2",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that aligns lyrics with timestamps."},
            {"role": "user", "content": alignment_prompt},
        ],
    )

    aligned_lyrics = alignment_completion.choices[0].message.content
    print("Aligned lyrics with timestamps:")
    print(aligned_lyrics)
    return aligned_lyrics
