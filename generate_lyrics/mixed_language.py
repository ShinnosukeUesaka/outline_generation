import openai
from models import Lyrics

client = openai.OpenAI()

PROMPT = """You are a music lyrics composer. Create a lyrics plan for a {genre} song to learn the phrases or words provided for a Japanese student learning English.

Tips
- Do not put any symbols in the lyrics.
- The lyrics must make sense and be clear instead of just repeating key words. Do not make the lyrics too catchy that it doesn't make sense.
- The lyrics should be in hiragana and katakana unless the kanji is very easy and obvious how to read it.
- DO NOT make the lyrics too poetic or use too difficult words, focus on clarity and ease of learning.
- lyrics_for_ai should use Hiragana and Katankana and English.
- lyrics should freely use Kanji.
- The lyrics should make clear who the word should be used.
- The order doesn't really matter, try to come up with a good lyrics that flows well line to line.

Example:
私は little おんなのこ
でも large な ゆめを もってる

every day がっこうに いく
ともだちの こえを hear する

せんせいが ぷりんとを hand する
わたしの number は 3ばん

やすみの during は ほんを よむ
いえで study する
"""

def generate_mixed_language_lyrics(phrases: list[str], genre: str) -> Lyrics:
    """Generate lyrics in mixed language."""
    completion = client.chat.completions.parse(
        model="gpt-5.2",
        messages=[
            {"role": "user", "content": PROMPT.format(genre=genre) + "\n\nPhrases: " + "\n".join(phrases)},
        ],
        response_format=Lyrics,
    )
    lyrics = completion.choices[0].message.parsed
    print(lyrics)
    return lyrics