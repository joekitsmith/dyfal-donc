from api.course import CourseRelease
from api.errors import ExerciseNotFoundError
from api.mappings import to_speech_text
from api.schemas import AudioTrack
from api.speech import SpeechClient


def speak_exercise(
    release: CourseRelease,
    speech: SpeechClient,
    exercise_id: str,
    track: AudioTrack,
) -> bytes:
    """One track of an exercise, spoken from the course's own text."""
    exercise = release.exercises.get(exercise_id)
    if exercise is None:
        raise ExerciseNotFoundError(f"Exercise {exercise_id} does not exist")

    return speech.synthesise(to_speech_text(exercise, track), track)
