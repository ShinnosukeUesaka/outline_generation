import pathlib

from generate_lyrics.from_phrases import generate_lyrics_from_phrases
from generate_lyrics.from_video import generate_lyrics_from_video
from models import Lyrics
from util.get_time_stamp import align_lyrics, extract_timestamps
from util.kie_api import generate_music_kie


def compose_music(lyrics: Lyrics, output_dir: pathlib.Path) -> None:
    """Generate music MP3 from lyrics using KIE AI."""
    output_dir.mkdir(parents=True, exist_ok=True)
    generate_music_kie(
        prompt="\n".join(lyrics.lyrics_for_ai),
        style=lyrics.genre,
        title="Generated Song",
        output_path=output_dir / "music.mp3",
    )
    print(f"Music saved to: {output_dir / 'music.mp3'}")


def generate_timestamps(lyrics: Lyrics, output_dir: pathlib.Path) -> str:
    """Extract timestamps from generated music and align with lyrics."""
    music_path = output_dir / "music.mp3"
    timestamped_words = extract_timestamps(music_path)
    aligned_lyrics = align_lyrics("\n".join(lyrics.lyrics_for_ai), timestamped_words)
    return aligned_lyrics


def save_info(lyrics: Lyrics, aligned_lyrics: str, output_dir: pathlib.Path) -> None:
    """Write info.txt with genre, lyrics, aligned lyrics, and kanji lyrics."""
    all_info = f"""
genre: {lyrics.genre}
lyrics_for_ai: {lyrics.lyrics_for_ai}
aligned_lyrics: {aligned_lyrics}
lyrics: {lyrics.lyrics}
"""
    with open(output_dir / "info.txt", "w") as f:
        f.write(all_info)
    print(f"Info saved to: {output_dir / 'info.txt'}")


def run_pipeline(lyrics: Lyrics, output_dir: pathlib.Path) -> None:
    """Run the full pipeline: compose music, extract timestamps, save info."""
    compose_music(lyrics, output_dir)
    aligned_lyrics = generate_timestamps(lyrics, output_dir)
    save_info(lyrics, aligned_lyrics, output_dir)


def from_video(video_url: str, genre: str, output_dir: pathlib.Path) -> Lyrics:
    """Convenience: generate lyrics from video and run the full pipeline."""
    lyrics = generate_lyrics_from_video(video_url, genre)
    run_pipeline(lyrics, output_dir)
    return lyrics


def from_phrases(phrases: list[str], genre: str, output_dir: pathlib.Path) -> Lyrics:
    """Convenience: generate lyrics from phrases and run the full pipeline."""
    lyrics = generate_lyrics_from_phrases(phrases, genre)
    run_pipeline(lyrics, output_dir)
    return lyrics


if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=q-PdhDzqimg"
    j_rustic_indie = "earthy acoustic instruments mixed with japanese indie rock sensibility. short entro"
    resources_path = pathlib.Path("../resources")
    from_video(video_url, j_rustic_indie, output_dir=resources_path / "muromati_v5")