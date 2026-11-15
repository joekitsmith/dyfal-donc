import pytest

from api.mappings import to_audio_links, to_speech_text
from api.schemas import AudioTrack
from engine.exercises import Exercise

EXERCISE = Exercise(english="I can go", welsh="Galla i fynd", items=("lex:mynd",))


class TestToAudioLinks:
    def test_links_each_track_of_the_exercise(self) -> None:
        links = to_audio_links("i-can-go")

        assert links.english == "/exercises/i-can-go/audio/english"
        assert links.welsh == "/exercises/i-can-go/audio/welsh"
        assert links.welsh_slow == "/exercises/i-can-go/audio/welsh-slow"

    def test_escapes_an_id_that_is_not_safe_in_a_path(self) -> None:
        assert to_audio_links("ex:1/a").english == "/exercises/ex%3A1%2Fa/audio/english"

    @pytest.mark.parametrize("track", AudioTrack)
    def test_every_track_has_a_link(self, track: AudioTrack) -> None:
        links = tuple(to_audio_links("i-can-go").model_dump().values())

        assert f"/exercises/i-can-go/audio/{track.value}" in links


class TestToSpeechText:
    def test_the_english_track_speaks_the_english(self) -> None:
        assert to_speech_text(EXERCISE, AudioTrack.ENGLISH) == "I can go"

    @pytest.mark.parametrize("track", (AudioTrack.WELSH, AudioTrack.WELSH_SLOW))
    def test_both_welsh_tracks_speak_the_welsh(self, track: AudioTrack) -> None:
        assert to_speech_text(EXERCISE, track) == "Galla i fynd"
