import json
import os
import pathlib
import re
import subprocess
import tempfile

import openai
import pydantic
from elevenlabs import ElevenLabs
from elevenlabs.environment import ElevenLabsEnvironment

client = openai.OpenAI()
class Section(pydantic.BaseModel):
    section_name: str = pydantic.Field(..., min_length=1, max_length=100, description="The name of the section. Must be between 1 and 100 characters. (Eg. Intro, Verse, Chorus, etc.)")
    positive_local_styles: list[str] = pydantic.Field(..., description="The styles and musical directions that should be present in this section. Use English language for best result.")
    negative_local_styles: list[str] = pydantic.Field(..., description="The styles and musical directions that should not be present in this section. Use English language for best result.")
    duration_ms: int = pydantic.Field(..., ge=3000, le=120000, description="The duration of the section in milliseconds. Must be between 3000ms and 120000ms.")
    lines: list[str] = pydantic.Field(..., description="The lyrics of the section. Max 200 characters per line.")
    lines_in_kanji: list[str] = pydantic.Field(..., description="The lyrics of the section in kanji.")


class CompositionPlan(pydantic.BaseModel):
    positive_global_styles: list[str] = pydantic.Field(..., description="The styles and musical directions that should be present in the entire song. Use English language for best result.")
    negative_global_styles: list[str] = pydantic.Field(..., description="The styles and musical directions that should not be present in the entire song. Use English language for best result.")
    sections: list[Section] = pydantic.Field(..., description="The sections of the song.")



PROMPT = """You are a music composition assistant. Create a detailed composition plan for a {genre} song to learn the important topic covered in the transcript. The lyrics should be catchy with some repeats. It must be Japanese. Break the song into logical sections with appropriate styles, durations, and lyrics.

Tips on lyrics:
- Do not include useless lyrics like "みっつの点を おぼえよう"
- Do not repeat the same information in multiple sections.


Tips
- Style should be 1-3 words long.
- The whole song should be under 12 lines.
- 30 characters is about 5 seconds of lyrics, make sure to calculate the duration of each section based on this.
- Do not put any symbols in the lyrics.
- The lyrics must make sense and be clear instead of just repeating key words. Do not make the lyrics too catchy that it doesn't make sense.
- The lyrics should be in hiragana and katakana unless the kanji is very easy and obvious how to read it.
- DO NOT make the lyrics too poetic or use too difficult words, focus on clarity and ease of learning.
"""

def song_plan_from_video(video_url: str, genre: str, output_dir: pathlib.Path, detailed_composition_plan: bool = False) -> CompositionPlan:
    print("Hello from outline-generation!")

    
    # Download and extract audio from video
    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = os.path.join(temp_dir, "audio.mp3")
        
        # Use yt-dlp to download and extract audio
        subprocess.run([
            "yt-dlp",
            "-x",
            "--audio-format", "mp3",
            "-o", audio_path,
            video_url
        ], check=True)
        
        # Transcribe audio using OpenAI
        with open(audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=audio_file
            )
        
        transcript_text = transcription.text
        print(f"Transcription: {transcript_text}")
        
        # Generate CompositionPlan using OpenAI structured outputs
        completion = client.chat.completions.parse(
            model="gpt-5.2",
            messages=[
                {"role": "user", "content": PROMPT.format(genre=genre) + "\n\nTranscript: " + transcript_text},
            ],
            response_format=CompositionPlan,
            reasoning_effort="low"
        )
        
        plan = completion.choices[0].message.parsed
        lyrics = "\n".join([line for section in plan.sections for line in section.lines])

        print(plan)
        # Generate music using ElevenLabs
        
        elevenlabs_client = ElevenLabs(
            environment=ElevenLabsEnvironment.PRODUCTION
        )
        
        if detailed_composition_plan:
            # Compose music based on the composition plan
            music_response = elevenlabs_client.music.compose(
                composition_plan={
                    "positive_global_styles": plan.positive_global_styles,
                    "negative_global_styles": plan.negative_global_styles,
                    "sections": [
                        {
                            "section_name": section.section_name,
                            "positive_local_styles": section.positive_local_styles,
                            "negative_local_styles": section.negative_local_styles,
                            "duration_ms": section.duration_ms,
                            "lines": section.lines
                        }
                        for section in plan.sections
                    ]
                }
            )

        else:

            prompt = f"""
genre: {genre}
lyrics: {lyrics}
Vocalist should start at 3 seconds. The outro should be 3 seconds long.
"""
            music_response = elevenlabs_client.music.compose(
                prompt=prompt
            )
        # Save the generated music
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "music.mp3"
        with open(output_path, "wb") as music_file:
            for chunk in music_response:
                music_file.write(chunk)
        
        print(f"Music saved to: {output_path}")

        # Generate transcript from video using ElevenLabs Speech-to-Text
        print("Generating transcript from video...")
        
        # Use the downloaded audio file for transcription
        with open(output_path, "rb") as audio_file:
            transcript_response = elevenlabs_client.speech_to_text.convert(
                model_id="scribe_v2",
                file=audio_file,
                language_code="ja",  # Japanese language code
                timestamps_granularity="character",
                diarize=False
            )
        
        # Extract words with timestamps
        timestamped_words = ""
        for word in transcript_response.words:
            timestamped_words += f"{word.text} ({word.start}-{word.end})\n"
        
        print(f"Extracted words with timestamps: {timestamped_words}")
        
        # Use OpenAI to align the extracted transcript with original lyrics
        print("Aligning transcript with original lyrics...")
        
        
        
        alignment_prompt = f"""You are given:
1. Original lyrics (accurate text but no timestamps)
2. Extracted transcript with timestamps (timestamps are accurate but text may have errors)

Your task is to align the original lyrics with the timestamps from the extracted transcript.

Original lyrics:
{lyrics}

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
                {"role": "user", "content": alignment_prompt}
            ]
        )
        
        aligned_lyrics = alignment_completion.choices[0].message.content
        print("Aligned lyrics with timestamps:")
        print(aligned_lyrics)
        kanji_lyrics = [line for section in plan.sections for line in section.lines_in_kanji]

        all_info = f"""
genre: {genre}
lyrics: {lyrics}
aligned_lyrics: {aligned_lyrics}
kanji_lyrics: {kanji_lyrics}
"""

        with open(output_dir / "info.txt", "w") as f:
            f.write(all_info)
        
        return plan


if __name__ == "__main__":
    # https://www.youtube.com/watch?v=mcPgPnRRXcA&list=PLzHNbKbtyAo1ehDzrKculxQ3EX05B-miA 生物の誕生
    video_url = "https://www.youtube.com/watch?v=q-PdhDzqimg"
    genre = "a raw, emotionally charged track that fuses alternative R&B, gritty soul, indie rock, and folk. The song should still feel like a live, one-take, emotionally spontaneous performance. The song is fairly fast paced."
    j_rustic_indie = "earthy acoustic instruments mixed with japanese indie rock sensibility"

    #print(plan)
    resources_path = pathlib.Path("../resources")
    plan = song_plan_from_video(video_url, j_rustic_indie, output_dir=resources_path / "muromati_v5", detailed_composition_plan=True)
