Use uv package manager to install and run code.

Example:
```bash
uv add library_name
uv sync
uv run python generate_music.py
```

Use pathlib when ever possible.

## Module Structure
- `models.py` — Shared data models (Lyrics)
- `generate_music.py` — Top-level orchestrator (entry point)
- `generate_lyrics/` — Lyrics generation from video or phrases
- `util/kie_api.py` — KIE AI music generation wrapper
- `util/get_time_stamp.py` — OpenAI STT timestamps + alignment
