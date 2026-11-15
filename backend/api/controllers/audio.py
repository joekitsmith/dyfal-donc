from api.course import CourseRelease
from api.errors import ExerciseNotFoundError, ItemNotFoundError
from api.mappings import to_speech_text
from api.schemas import AudioTrack
from api.speech import SpeechClient
from engine.curriculum import Lexeme


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


def speak_item(release: CourseRelease, speech: SpeechClient, item_id: str) -> bytes:
    """A word at a standard pace, spoken from the course's own text. A phrase has no audio."""
    item = next((item for item in release.curriculum.items if item.id == item_id), None)
    if not isinstance(item, Lexeme):
        raise ItemNotFoundError(f"Item {item_id} has no audio")

    return speech.synthesise(item.welsh, AudioTrack.WELSH_STANDARD)
