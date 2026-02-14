import pydantic


class Lyrics(pydantic.BaseModel):
    lyrics: str
    lyrics_for_ai: str
    