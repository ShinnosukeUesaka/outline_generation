import os
import subprocess
import tempfile

import openai
from models import Lyrics

client = openai.OpenAI()

PROMPT = """You are a music composition assistant. Create a detailed composition plan for a {genre} song to learn the important topic covered in the transcript. The lyrics should be catchy with some repeats. It must be Japanese. Break the song into logical sections with appropriate styles, durations, and lyrics.

Tips on lyrics:
- Do not include useless lyrics like "みっつの点を おぼえよう"
- Do not repeat the same information in multiple sections.


Tips
- The whole song should be under 12 lines.
- Do not put any symbols in the lyrics.
- The lyrics must make sense and be clear instead of just repeating key words. Do not make the lyrics too catchy that it doesn't make sense.
- The lyrics should be in hiragana and katakana unless the kanji is very easy and obvious how to read it.
- DO NOT make the lyrics too poetic or use too difficult words, focus on clarity and ease of learning.
"""


def generate_lyrics_from_video(video_url: str, genre: str) -> Lyrics:
    """Download a YouTube video, transcribe it, and generate lyrics."""
    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = os.path.join(temp_dir, "audio.mp3")

        subprocess.run(
            ["yt-dlp", "-x", "--audio-format", "mp3", "-o", audio_path, video_url],
            check=True,
        )

        with open(audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=audio_file,
            )

        transcript_text = transcription.text
        print(f"Transcription: {transcript_text}")

        completion = client.chat.completions.parse(
            model="gpt-5.2",
            messages=[
                {"role": "user", "content": PROMPT.format(genre=genre) + "\n\nTranscript: " + transcript_text},
            ],
            response_format=Lyrics,
            reasoning_effort="low",
        )

        lyrics = completion.choices[0].message.parsed
        print(lyrics)
        return lyrics
