from fastapi import APIRouter, Response

from api.controllers import speak_exercise
from api.dependencies import CourseReleaseDependency, SpeechClientDependency
from api.schemas import AudioTrack

WAV_MEDIA_TYPE = "audio/wav"

router = APIRouter(prefix="/exercises")


@router.get(
    "/{exercise_id}/audio/{track}",
    response_class=Response,
    responses={200: {"content": {WAV_MEDIA_TYPE: {}}}},
)
def get_audio(
    exercise_id: str,
    track: AudioTrack,
    release: CourseReleaseDependency,
    speech: SpeechClientDependency,
) -> Response:
    audio = speak_exercise(release, speech, exercise_id, track)
    return Response(content=audio, media_type=WAV_MEDIA_TYPE)
