import pydantic


class Section(pydantic.BaseModel):
    section_name: str = pydantic.Field(
        ...,
        min_length=1,
        max_length=100,
        description="The name of the section. Must be between 1 and 100 characters. (Eg. Intro, Verse, Chorus, etc.)",
    )
    positive_local_styles: list[str] = pydantic.Field(
        ...,
        description="The styles and musical directions that should be present in this section. Use English language for best result.",
    )
    negative_local_styles: list[str] = pydantic.Field(
        ...,
        description="The styles and musical directions that should not be present in this section. Use English language for best result.",
    )
    duration_ms: int = pydantic.Field(
        ...,
        ge=3000,
        le=120000,
        description="The duration of the section in milliseconds. Must be between 3000ms and 120000ms.",
    )
    lines: list[str] = pydantic.Field(
        ...,
        description="The lyrics of the section. Max 200 characters per line.",
    )
    lines_in_kanji: list[str] = pydantic.Field(
        ...,
        description="The lyrics of the section in kanji.",
    )


class CompositionPlan(pydantic.BaseModel):
    positive_global_styles: list[str] = pydantic.Field(
        ...,
        description="The styles and musical directions that should be present in the entire song. Use English language for best result.",
    )
    negative_global_styles: list[str] = pydantic.Field(
        ...,
        description="The styles and musical directions that should not be present in the entire song. Use English language for best result.",
    )
    sections: list[Section] = pydantic.Field(
        ...,
        description="The sections of the song.",
    )


class Lyrics(pydantic.BaseModel):
    genre: str
    lyrics_for_ai: list[str]
    lyrics: list[str]
