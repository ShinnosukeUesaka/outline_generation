import openai
from models import Lyrics

client = openai.OpenAI()

PROMPT = """You are a music composition assistant. Create a detailed composition plan for a {genre} song to learn the phrases or words provided.

Tips
- Style should be 1-3 words long.
- Do not put any symbols in the lyrics.
- The lyrics must make sense and be clear instead of just repeating key words. Do not make the lyrics too catchy that it doesn't make sense.
- The lyrics should be in hiragana and katakana unless the kanji is very easy and obvious how to read it.
- DO NOT make the lyrics too poetic or use too difficult words, focus on clarity and ease of learning.
"""

def generate_mixed_language_lyrics(phrases: list[str], genre: str) -> Lyrics:
    """Generate lyrics in mixed language."""
    completion = client.chat.completions.parse(
        model="gpt-5.2",
        messages=[
            {"role": "user", "content": PROMPT.format(genre=genre) + "\n\nPhrases: " + "\n".join(phrases)},
        ],
        response_format=Lyrics,
        reasoning_effort="low",
    )
    plan = completion.choices[0].message.parsed
    lyrics_for_ai = [line for section in plan.sections for line in section.lines]
    lyrics = [line for section in plan.sections for line in section.lines_in_kanji]
    return Lyrics(genre=genre, lyrics_for_ai=lyrics_for_ai, lyrics=lyrics)