import pathlib

from generate_lyrics.from_phrases import generate_lyrics_from_phrases
from generate_lyrics.from_video import generate_lyrics_from_video
from generate_lyrics.mixed_language import generate_mixed_language_lyrics
from models import Lyrics
from util.get_time_stamp import align_lyrics, extract_timestamps
from util.kie_api import generate_music_kie


def compose_music(lyrics: Lyrics, genre: str, output_dir: pathlib.Path) -> None:
    """Generate music MP3 from lyrics using KIE AI."""
    output_dir.mkdir(parents=True, exist_ok=True)
    music_path = output_dir / "music.mp3"
    generate_music_kie(
        prompt=lyrics.lyrics_for_ai,
        style=genre,
        title="Generated Song",
        output_path=music_path,
    )
    if not music_path.exists():
        raise RuntimeError(f"Music file was not saved to {music_path}. KIE API may have returned no audio tracks.")
    print(f"Music saved to: {music_path}")


def generate_timestamps(lyrics: Lyrics, output_dir: pathlib.Path) -> str:
    """Extract timestamps from generated music and align with lyrics."""
    music_path = output_dir / "music.mp3"
    timestamped_words = extract_timestamps(music_path)
    aligned_lyrics = align_lyrics("\n".join(lyrics.lyrics_for_ai), timestamped_words)
    return aligned_lyrics


def save_info(lyrics: Lyrics, aligned_lyrics: str, output_dir: pathlib.Path) -> None:
    """Write info.txt with lyrics, aligned lyrics, and kanji lyrics."""
    all_info = f"""
aligned_lyrics: {aligned_lyrics}
lyrics: {lyrics.lyrics}
"""
    with open(output_dir / "info.txt", "w") as f:
        f.write(all_info)
    print(f"Info saved to: {output_dir / 'info.txt'}")


def run_pipeline(lyrics: Lyrics, genre: str, output_dir: pathlib.Path) -> None:
    """Run the full pipeline: compose music, extract timestamps, save info."""
    compose_music(lyrics, genre, output_dir)
    aligned_lyrics = generate_timestamps(lyrics, output_dir)
    save_info(lyrics, aligned_lyrics, output_dir)


def from_video(video_url: str, genre: str, output_dir: pathlib.Path) -> Lyrics:
    """Convenience: generate lyrics from video and run the full pipeline."""
    lyrics = generate_lyrics_from_video(video_url, genre)
    run_pipeline(lyrics, genre, output_dir)
    return lyrics


def from_phrases(phrases: list[str], genre: str, output_dir: pathlib.Path) -> Lyrics:
    """Convenience: generate lyrics from phrases and run the full pipeline."""
    lyrics = generate_lyrics_from_phrases(phrases, genre)
    run_pipeline(lyrics, genre, output_dir)
    return lyrics


def from_mixed_language(phrases: list[str], genre: str, output_dir: pathlib.Path) -> Lyrics:
    """Convenience: generate mixed-language lyrics from phrases and run the full pipeline."""
    lyrics = generate_mixed_language_lyrics(phrases, genre)
    run_pipeline(lyrics, genre, output_dir)
    return lyrics

def from_lyrics(lyrics: Lyrics, genre: str, output_dir: pathlib.Path) -> Lyrics:
    """Convenience: run the full pipeline with existing lyrics."""
    run_pipeline(lyrics, genre, output_dir)
    return lyrics


if __name__ == "__main__":
    # video_url = "https://www.youtube.com/watch?v=q-PdhDzqimg"
    # j_rustic_indie = "earthy acoustic instruments mixed with japanese indie rock sensibility. short intro and outro"
    # resources_path = pathlib.Path("../resources")
    # from_video(video_url, j_rustic_indie, output_dir=resources_path / "muromati_v5")

    # vocab_list = [
    #     "famous",
    #     "weekend",
    #     "soon",
    #     "still",
    #     "popular",
    #     "practice",
    #     "during",
    #     "enjoy",
    #     "favorite",
    #     "sell",
    #     "bring",
    #     "expensive",
    #     "join",
    #     "so",
    #     "leave",
    #     "enough",
    #     "happen",
    #     "different",
    #     "invite",
    #     "how about"
    # ]

    # vocab_list = [
    #     "plan",
    #     "ask",
    #     "until",
    #     "almost",
    #     "sick",
    #     "excited",
    #     "science",
    #     "library",
    #     "visit",
    #     "cheap",
    #     "then",
    #     "show",
    #     "instead",
    #     "what about",
    #     "garden",
    #     "look for",
    #     "meet",
    #     "because of",
    #     "by",
    #     "stay"
    # ]
    # #genre = "earthy acoustic instruments mixed with japanese indie rock sensibility. short intro and outro"
    # genre = "Addictive Japanese female vocaloid, artistic. very short intro and outro. Good English pronunciation. English part is emphasized."
    
    # resources_path = pathlib.Path("../resources")
    # from_mixed_language(vocab_list, genre, output_dir=resources_path / "eiken_3_vocaloid_2")
    lyrics = """Hola, vamos a cantar Hello, let’s sing
Cumbia suena en mi casa Cumbia sounds in my house
Sí, sí, sí; no, no, no Yes, yes, yes; no, no, no
Gracias, por favor Thank you, please
Buenos días, buenas noches Good morning, good night
Nos vemos, hasta luego See you, see you later
¿Dónde? en la casa Where? in the house
¿Cuándo? hoy, mañana When? today, tomorrow
La comida está lista The food is ready
Abrir, cerrar la puerta Open, close the door
Dormir después Sleep after
Cantar conmigo Sing with me
Sí, no, gracias, por favor Yes, no, thank you, please
Hoy, mañana, nos vemos Today, tomorrow, see you
Hola, adiós, cumbia va Hello, goodbye, the cumbia goes
Buenos días, buenas noches Good morning, good night
¿Dónde? la casa, la casa Where? the house, the house
¿Cuándo? hoy o mañana When? today or tomorrow
Abrir la puerta, cerrar Open the door, close
Dormir después, cantar Sleep after, sing
La comida, gracias The food, thank you
Nos vemos, hasta luego See you, see you later
Hola, adiós Hello, goodbye
Sí o no Yes or no
Sí, no, gracias, por favor Yes, no, thank you, please
Hoy, mañana, nos vemos Today, tomorrow, see you
Hola, adiós, cumbia va Hello, goodbye, the cumbia goes
Buenos días, buenas noches Good morning, good night
Cantar y adiós Sing and goodbye
Hasta luego See you later"""
    lyrics = Lyrics(lyrics=lyrics, lyrics_for_ai=lyrics)
    genre = """Latin cumbia, short into and outro

Song requirements

Alternate Spanish and English line by line
(Spanish → English → Spanish → English…)

Teach about 20 words or phrases in the song

Make the song catchy and easy to repeat

Beginner level (A1)

Structure

[Intro]

very short

bilingual (Spanish + English)

[Verse 1]

vocabulary learning

[Hook]

memorable

repeatable

[Verse 2]

vocabulary learning continued

[Hook]

[Outro]

very short

motivational learning message

Language rules

Spanish pronunciation must be natural

English translations must be simple and clear

Avoid long sentences

Focus on words, phrases, and daily conversation

Style rules

Educational but fun

Rhythmic

Designed for YouTube / Shorts learning content

Easy for viewers to sing along"""
    from_lyrics(lyrics, genre, output_dir=pathlib.Path("../resources") / "spanish_1")