from collections.abc import Mapping, Sequence
from datetime import datetime

from api.mappings.audio import to_audio_links
from api.schemas import (
    ItemResponse,
    SentenceResponse,
    OverviewResponse,
    SessionRecapResponse,
    SessionSummaryResponse,
)
from engine.curriculum import Curriculum, Lexeme
from engine.exercises import Exercise
from engine.learner import SessionSummary


def to_item_responses(
    curriculum: Curriculum, item_ids: Sequence[str]
) -> tuple[ItemResponse, ...]:
    """The items in both languages. An item the course no longer has is left out."""
    known = {item.id: item for item in curriculum.items}

    return tuple(
        ItemResponse(
            id=item.id,
            welsh=item.welsh if isinstance(item, Lexeme) else item.template,
            english=item.english,
            forms=item.forms if isinstance(item, Lexeme) else (),
        )
        for item_id in item_ids
        if (item := known.get(item_id)) is not None
    )


def to_sentence_responses(
    exercises: Mapping[str, Exercise], exercise_ids: Sequence[str]
) -> tuple[SentenceResponse, ...]:
    """The exercises with their text and audio. One the course no longer has is left out."""
    return tuple(
        SentenceResponse(
            id=exercise_id,
            english=exercise.english,
            welsh=exercise.welsh,
            audio=to_audio_links(exercise_id),
        )
        for exercise_id in exercise_ids
        if (exercise := exercises.get(exercise_id)) is not None
    )


def to_session_recap_response(
    session_id: int,
    summary: SessionSummary,
    *,
    ongoing: bool,
    curriculum: Curriculum,
) -> SessionRecapResponse:
    return SessionRecapResponse(
        id=session_id,
        started_at=summary.started_at,
        ended_at=summary.ended_at,
        duration_seconds=int(summary.duration.total_seconds()),
        ongoing=ongoing,
        exercises_completed=summary.exercises_completed,
        items_introduced=to_item_responses(curriculum, summary.items_introduced),
    )


def to_session_summary_response(
    session_id: int,
    summary: SessionSummary,
    *,
    ongoing: bool,
    curriculum: Curriculum,
    exercises: Mapping[str, Exercise],
) -> SessionSummaryResponse:
    recap = to_session_recap_response(
        session_id, summary, ongoing=ongoing, curriculum=curriculum
    )

    return SessionSummaryResponse(
        **recap.model_dump(),
        items_reviewed=len(summary.items_reviewed),
        items_lapsed=to_item_responses(curriculum, summary.items_lapsed),
        missed_exercises=to_sentence_responses(exercises, summary.missed_exercises),
    )


def to_overview_response(
    *,
    now: datetime,
    review_due: int,
    learning_due: int,
    topic: str | None,
    introduced: int,
    course_items: int,
    latest_session: SessionRecapResponse | None,
) -> OverviewResponse:
    return OverviewResponse(
        now=now,
        review_due=review_due,
        learning_due=learning_due,
        new_words_ready=topic is not None,
        topic=topic,
        introduced=introduced,
        course_items=course_items,
        latest_session=latest_session,
    )
