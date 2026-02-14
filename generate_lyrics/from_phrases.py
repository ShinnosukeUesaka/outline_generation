import openai
from models import Lyrics

client = openai.OpenAI()

PROMPT = """You are a music composition assistant. Create a detailed composition plan for a {genre} song to learn the phrases or words provided.

Tips
- Do not put any symbols in the lyrics.
- The lyrics must make sense and be clear instead of just repeating key words. Do not make the lyrics too catchy that it doesn't make sense.
- The lyrics should be in hiragana and katakana unless the kanji is very easy and obvious how to read it.
- DO NOT make the lyrics too poetic or use too difficult words, focus on clarity and ease of learning.

"""


def generate_lyrics_from_phrases(phrases: list[str], genre: str) -> Lyrics:
    """Generate lyrics from a list of phrases/words to learn."""
    completion = client.chat.completions.parse(
        model="gpt-5.2",
        messages=[
            {"role": "user", "content": PROMPT.format(genre=genre) + "\n\nPhrases: " + "\n".join(phrases)},
        ],
        response_format=Lyrics,
        reasoning_effort="low",
    )

    lyrics = completion.choices[0].message.parsed
    print(lyrics)
    return lyrics
