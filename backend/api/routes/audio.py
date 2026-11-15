from fastapi import APIRouter, Response

from api.controllers import speak_exercise, speak_item
from api.dependencies import CourseReleaseDependency, SpeechClientDependency
from api.mappings import to_welsh_track
from api.schemas import AudioTrack, WelshPace

WAV_MEDIA_TYPE = "audio/wav"

router = APIRouter()


@router.get(
    "/exercises/{exercise_id}/audio/english",
    response_class=Response,
    responses={200: {"content": {WAV_MEDIA_TYPE: {}}}},
)
def get_english_audio(
    exercise_id: str, release: CourseReleaseDependency, speech: SpeechClientDependency
) -> Response:
    audio = speak_exercise(release, speech, exercise_id, AudioTrack.ENGLISH)
    return Response(content=audio, media_type=WAV_MEDIA_TYPE)


@router.get(
    "/exercises/{exercise_id}/audio/welsh/{pace}",
    response_class=Response,
    responses={200: {"content": {WAV_MEDIA_TYPE: {}}}},
)
def get_welsh_audio(
    exercise_id: str,
    pace: WelshPace,
    release: CourseReleaseDependency,
    speech: SpeechClientDependency,
) -> Response:
    audio = speak_exercise(release, speech, exercise_id, to_welsh_track(pace))
    return Response(content=audio, media_type=WAV_MEDIA_TYPE)


@router.get(
    "/items/{item_id}/audio",
    response_class=Response,
    responses={200: {"content": {WAV_MEDIA_TYPE: {}}}},
)
def get_item_audio(
    item_id: str, release: CourseReleaseDependency, speech: SpeechClientDependency
) -> Response:
    return Response(
        content=speak_item(release, speech, item_id), media_type=WAV_MEDIA_TYPE
    )
