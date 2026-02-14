import contextlib
import io
import os
from pathlib import Path

import streamlit as st

from generate_lyrics.from_phrases import generate_lyrics_from_phrases
from generate_lyrics.from_video import generate_lyrics_from_video
from generate_lyrics.mixed_language import generate_mixed_language_lyrics
from generate_music import from_lyrics, from_mixed_language, from_phrases, from_video
from models import Lyrics

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESOURCES_DIR = PROJECT_ROOT / "resources"
MODE_VIDEO = "From Video URL"
MODE_PHRASES = "From Phrases"
MODE_MIXED = "From Phrases (Mixed Language)"
MODE_MANUAL = "From Existing Lyrics"


def _to_abs_path(path_str: str) -> Path:
    path = Path(path_str).expanduser()
    if not path.is_absolute():
        path = (PROJECT_ROOT / path).resolve()
    else:
        path = path.resolve()
    return path


def _resolve_output_dir(resources_base: Path, topic_name: str) -> Path:
    clean_topic = topic_name.strip()
    if not clean_topic:
        raise ValueError("Topic/folder name is required.")
    if clean_topic in {".", ".."}:
        raise ValueError("Invalid topic/folder name.")

    output_dir = (resources_base / clean_topic).resolve()
    if resources_base.resolve() not in output_dir.parents:
        raise ValueError("Topic/folder name must stay inside the resources base directory.")
    return output_dir


def _parse_phrases(raw_text: str) -> list[str]:
    return [line.strip() for line in raw_text.splitlines() if line.strip()]


def _check_required_env(run_full_pipeline: bool) -> list[str]:
    missing = []
    if not os.getenv("OPENAI_API_KEY"):
        missing.append("OPENAI_API_KEY")
    if run_full_pipeline and not os.getenv("KIE_API_KEY"):
        missing.append("KIE_API_KEY")
    return missing


def _run_with_captured_logs(fn, *args, **kwargs):
    logs = io.StringIO()
    with contextlib.redirect_stdout(logs), contextlib.redirect_stderr(logs):
        try:
            result = fn(*args, **kwargs)
            return result, logs.getvalue(), None
        except Exception as exc:
            return None, logs.getvalue(), exc


def _generate(
    mode: str,
    genre: str,
    run_full_pipeline: bool,
    output_dir: Path,
    video_url: str,
    phrases_text: str,
    lyrics_text: str,
    lyrics_for_ai_text: str,
) -> Lyrics:
    if mode == MODE_VIDEO:
        if not video_url.strip():
            raise ValueError("Video URL is required for video mode.")
        if run_full_pipeline:
            return from_video(video_url.strip(), genre, output_dir)
        return generate_lyrics_from_video(video_url.strip(), genre)

    if mode == MODE_PHRASES:
        phrases = _parse_phrases(phrases_text)
        if not phrases:
            raise ValueError("Please provide at least one phrase.")
        if run_full_pipeline:
            return from_phrases(phrases, genre, output_dir)
        return generate_lyrics_from_phrases(phrases, genre)

    if mode == MODE_MIXED:
        phrases = _parse_phrases(phrases_text)
        if not phrases:
            raise ValueError("Please provide at least one phrase.")
        if run_full_pipeline:
            return from_mixed_language(phrases, genre, output_dir)
        return generate_mixed_language_lyrics(phrases, genre)

    if mode == MODE_MANUAL:
        if not lyrics_text.strip():
            raise ValueError("Lyrics text is required for manual mode.")
        lyrics_obj = Lyrics(
            lyrics=lyrics_text.strip(),
            lyrics_for_ai=(lyrics_for_ai_text.strip() or lyrics_text.strip()),
        )
        if run_full_pipeline:
            return from_lyrics(lyrics_obj, genre, output_dir)
        return lyrics_obj

    raise ValueError(f"Unsupported mode: {mode}")


st.set_page_config(page_title="Outline Generation UI", layout="wide")
st.title("Outline Generation UI")
st.caption("Generate lyrics/music assets from video, phrase lists, or manual lyrics.")
st.code("streamlit run outline_generation/ui.py", language="bash")

if "last_lyrics" not in st.session_state:
    st.session_state.last_lyrics = None
if "last_logs" not in st.session_state:
    st.session_state.last_logs = ""
if "last_output_dir" not in st.session_state:
    st.session_state.last_output_dir = ""
if "last_mode" not in st.session_state:
    st.session_state.last_mode = ""
if "last_full_pipeline" not in st.session_state:
    st.session_state.last_full_pipeline = False

with st.form("outline_generation_form"):
    mode = st.radio(
        "Input mode",
        [MODE_VIDEO, MODE_PHRASES, MODE_MIXED, MODE_MANUAL],
        horizontal=True,
    )
    genre = st.text_area(
        "Genre / style prompt",
        height=120,
        placeholder="Example: Addictive Japanese female vocaloid, short intro/outro, clear English pronunciation...",
    )
    run_full_pipeline = st.checkbox(
        "Run full pipeline (generate music.mp3 + alignment + info.txt)",
        value=True,
    )

    resources_base_input = st.text_input("Resources base directory", value=str(DEFAULT_RESOURCES_DIR))
    topic_name = st.text_input("Topic / folder name", value="new_topic")

    video_url = ""
    phrases_text = ""
    lyrics_text = ""
    lyrics_for_ai_text = ""

    if mode == MODE_VIDEO:
        video_url = st.text_input("Video URL", placeholder="https://www.youtube.com/watch?v=...")
    elif mode in (MODE_PHRASES, MODE_MIXED):
        phrases_text = st.text_area(
            "Phrases / words (one per line)",
            height=180,
            placeholder="famous\nweekend\nsoon\nstill\n...",
        )
    else:
        lyrics_text = st.text_area("Lyrics", height=220)
        lyrics_for_ai_text = st.text_area(
            "Lyrics for AI (optional, defaults to Lyrics)",
            height=220,
        )

    submitted = st.form_submit_button("Generate")

if submitted:
    missing_env = _check_required_env(run_full_pipeline)
    if missing_env:
        st.error(f"Missing required environment variables: {', '.join(missing_env)}")
    elif not genre.strip():
        st.error("Genre / style prompt is required.")
    else:
        try:
            resources_base = _to_abs_path(resources_base_input)
            output_dir = _resolve_output_dir(resources_base, topic_name)
            if run_full_pipeline:
                output_dir.mkdir(parents=True, exist_ok=True)

            with st.spinner("Generating... this can take several minutes for full pipeline runs."):
                lyrics_obj, logs, generation_error = _run_with_captured_logs(
                    _generate,
                    mode,
                    genre.strip(),
                    run_full_pipeline,
                    output_dir,
                    video_url,
                    phrases_text,
                    lyrics_text,
                    lyrics_for_ai_text,
                )

            st.session_state.last_logs = logs
            if generation_error:
                raise generation_error

            st.session_state.last_lyrics = lyrics_obj
            st.session_state.last_output_dir = str(output_dir)
            st.session_state.last_mode = mode
            st.session_state.last_full_pipeline = run_full_pipeline
            st.success("Generation completed.")
        except Exception as exc:
            st.exception(exc)

if st.session_state.last_lyrics:
    st.subheader("Generated Lyrics")
    st.text_area("lyrics", value=st.session_state.last_lyrics.lyrics, height=220, disabled=True)
    st.text_area("lyrics_for_ai", value=st.session_state.last_lyrics.lyrics_for_ai, height=220, disabled=True)

    if st.session_state.last_full_pipeline:
        output_dir = Path(st.session_state.last_output_dir)
        music_path = output_dir / "music.mp3"
        info_path = output_dir / "info.txt"

        st.subheader("Saved Output")
        st.write(f"`{output_dir}`")

        if music_path.exists():
            st.audio(str(music_path))
            st.write(f"Music file: `{music_path}`")
        else:
            st.warning(f"`music.mp3` not found at `{music_path}`")

        if info_path.exists():
            st.write(f"Info file: `{info_path}`")
            st.text_area("info.txt", value=info_path.read_text(), height=220, disabled=True)
        else:
            st.warning(f"`info.txt` not found at `{info_path}`")

if st.session_state.last_logs:
    with st.expander("Execution logs"):
        st.code(st.session_state.last_logs)
