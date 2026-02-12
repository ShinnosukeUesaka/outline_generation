import pydantic


class Lyrics(pydantic.BaseModel):
    lyrics: list[str]
    lyrics_for_ai: list[str]
    