from collections.abc import Mapping, Sequence
from datetime import datetime

from api.mappings.audio import to_item_audio_link
from api.mappings.learning_session import to_item_responses, to_sentence_responses
from api.schemas import (
    CourseProgressResponse,
    ItemDetailResponse,
    ItemKind,
    SentenceResponse,
    TopicProgressResponse,
)
from engine.curriculum import Curriculum, Item, Lexeme
from engine.exercises import Exercise
from engine.scheduler import TopicProgress


def to_course_progress_response(
    curriculum: Curriculum,
    exercises: Mapping[str, Exercise],
    progress: Sequence[TopicProgress],
) -> CourseProgressResponse:
    return CourseProgressResponse(
        topics=tuple(
            TopicProgressResponse(
                name=topic.name,
                started=topic.started,
                is_current=topic.is_current,
                exercises_answered=topic.exercises_answered,
                words=to_item_responses(curriculum, topic.words),
                phrases=to_item_responses(curriculum, topic.phrases),
                sayable=to_sentence_responses(exercises, topic.sayable_exercise_ids),
            )
            for topic in progress
        )
    )


def to_item_detail_response(
    item: Item, first_met_at: datetime, examples: Sequence[SentenceResponse]
) -> ItemDetailResponse:
    if isinstance(item, Lexeme):
        return ItemDetailResponse(
            id=item.id,
            kind=ItemKind.WORD,
            welsh=item.welsh,
            english=item.english,
            topic=item.topic,
            forms=item.forms,
            notes=item.notes,
            first_met_at=first_met_at,
            audio=to_item_audio_link(item.id),
            examples=tuple(examples),
        )

    return ItemDetailResponse(
        id=item.id,
        kind=ItemKind.PHRASE,
        welsh=item.template,
        english=item.english,
        topic=item.topic,
        forms=(),
        notes=item.notes,
        first_met_at=first_met_at,
        audio=None,
        examples=tuple(examples),
    )
