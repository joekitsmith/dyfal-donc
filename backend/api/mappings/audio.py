from urllib.parse import quote

from api.schemas import AudioLinks, AudioTrack
from engine.exercises import Exercise

AUDIO_PATH = "/exercises/{exercise_id}/audio/{track}"


def to_audio_links(exercise_id: str) -> AudioLinks:
    def path(track: AudioTrack) -> str:
        return AUDIO_PATH.format(exercise_id=quote(exercise_id, safe=""), track=track)

    return AudioLinks(
        english=path(AudioTrack.ENGLISH),
        welsh=path(AudioTrack.WELSH),
        welsh_slow=path(AudioTrack.WELSH_SLOW),
    )


def to_speech_text(exercise: Exercise, track: AudioTrack) -> str:
    """The course text that the track speaks. Clients never supply text."""
    if track is AudioTrack.ENGLISH:
        return exercise.english

    return exercise.welsh
