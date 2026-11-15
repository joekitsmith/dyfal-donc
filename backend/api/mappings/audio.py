from urllib.parse import quote

from api.schemas import AudioLinks, AudioTrack, WelshAudioLinks, WelshPace
from engine.exercises import Exercise

ENGLISH_AUDIO_PATH = "/exercises/{exercise_id}/audio/english"
WELSH_AUDIO_PATH = "/exercises/{exercise_id}/audio/welsh/{pace}"


def to_audio_links(exercise_id: str) -> AudioLinks:
    quoted = quote(exercise_id, safe="")

    return AudioLinks(
        english=ENGLISH_AUDIO_PATH.format(exercise_id=quoted),
        welsh=WelshAudioLinks(
            standard=WELSH_AUDIO_PATH.format(
                exercise_id=quoted, pace=WelshPace.STANDARD
            ),
            slow=WELSH_AUDIO_PATH.format(exercise_id=quoted, pace=WelshPace.SLOW),
        ),
    )


def to_welsh_track(pace: WelshPace) -> AudioTrack:
    """The track the speech service speaks the Welsh on at this pace."""
    return (
        AudioTrack.WELSH_STANDARD
        if pace is WelshPace.STANDARD
        else AudioTrack.WELSH_SLOW
    )


def to_speech_text(exercise: Exercise, track: AudioTrack) -> str:
    """The course text that the track speaks. Clients never supply text."""
    if track is AudioTrack.ENGLISH:
        return exercise.english

    return exercise.welsh
