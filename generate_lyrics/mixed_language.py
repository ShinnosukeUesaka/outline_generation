import openai
from models import Lyrics

client = openai.OpenAI()

PROMPT = """You are a music lyrics composer. Write a lyrics for a song to learn the phrases or words provided for a Japanese student learning English.

Tips
- Do not put any symbols (eg. ", ", ".", "!", "?", etc.) in the lyrics except for the song queue and () for the words (see the example lyrics)
- The lyrics must make sense and be clear instead of just repeating key words. Do not make the lyrics too catchy that it doesn't make sense.
- The lyrics should be in hiragana and katakana unless the kanji is very easy and obvious how to read it.
- DO NOT make the lyrics too poetic or use too difficult words, focus on clarity and ease of learning.
- **The lyrics should make clear who the word should be used**
- The order doesn't really matter, try to come up with a good lyrics that flows well line to line.
- Each line should feature a single word (a Japanese sentence containing a English word). Do not use more than one word per line. or use more than one word per line.
- Every line should feature a single word
- Make sure each line is not too long.

Structure:
[Verse 1]

[Chorus 1]

[Verse 2]

[Chorus 2]

The lyrics should have these sections. Verse 1 2 and Chorus 1 2 must have the same structure. The number of lines should match, and ideally the structure and syllables should match as well.

Output fields:
lyrics: This will be the lyrics (similar to the example lyrics below) using kanji normally. 
lyrics_for_ai:  This will be a lines of the lyrics. It's the same lyrics as lyrics but all of Kanji must be replaced with Hiragana and Katankana.
For both fields song queue should be included ([Verse 1] [Chorus 1] [Verse 2] [Chorus 2])



Example lyrics:
[Verse 1]
私は little 女の子 (little)
でも large な 夢を 持ってる (large)

every day 学校に 行く (every day)
友達の 声を hear する (friend)

先生が プリントを hand する (teacher)
私の number は 3番 (number)

休みの during は 本を 読む (during)
家で study する (study)

[Chorus 1]
continues
"""

def generate_mixed_language_lyrics(phrases: list[str], genre: str) -> Lyrics:
    """Generate lyrics in mixed language."""
    messages=[
            {"role": "user", "content": PROMPT + "\n\nPhrases: " + "\n".join(phrases)},
    ]
    completion = client.chat.completions.parse(
        model="gpt-5.2",
        messages=messages,
        response_format=Lyrics,
        reasoning_effort="medium",
    )
    lyrics = completion.choices[0].message.parsed
    print(lyrics.lyrics)
    print(lyrics.lyrics_for_ai)
    return lyrics


if __name__ == "__main__":

    vocab_list = [
        "famous",
        "weekend",
        "soon",
        "still",
        "popular",
        "practice",
        "during",
        "enjoy",
        "favorite",
        "sell",
        "bring",
        "expensive",
        "join",
        "so",
        "leave",
        "enough",
        "happen",
        "different",
        "invite",
        "how about"
    ]
    genre = "earthy acoustic instruments mixed with japanese indie rock sensibility. short intro and outro"
    lyrics = generate_mixed_language_lyrics(vocab_list, genre)
    print(lyrics)