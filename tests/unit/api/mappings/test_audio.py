import pytest

from api.mappings import to_audio_links, to_speech_text, to_welsh_track
from api.schemas import AudioTrack, WelshPace
from engine.exercises import Exercise

EXERCISE = Exercise(english="I can go", welsh="Galla i fynd", items=("lex:mynd",))


class TestToAudioLinks:
    def test_links_each_track_of_the_exercise(self) -> None:
        links = to_audio_links("i-can-go")

        assert links.english == "/exercises/i-can-go/audio/english"
        assert links.welsh.standard == "/exercises/i-can-go/audio/welsh/standard"
        assert links.welsh.slow == "/exercises/i-can-go/audio/welsh/slow"

    def test_escapes_an_id_that_is_not_safe_in_a_path(self) -> None:
        assert to_audio_links("ex:1/a").english == "/exercises/ex%3A1%2Fa/audio/english"

    def test_every_track_has_a_link(self) -> None:
        links = to_audio_links("i-can-go")

        assert {links.english, links.welsh.standard, links.welsh.slow} == {
            "/exercises/i-can-go/audio/english",
            "/exercises/i-can-go/audio/welsh/standard",
            "/exercises/i-can-go/audio/welsh/slow",
        }


class TestToWelshTrack:
    def test_each_pace_has_its_own_track(self) -> None:
        assert to_welsh_track(WelshPace.STANDARD) is AudioTrack.WELSH_STANDARD
        assert to_welsh_track(WelshPace.SLOW) is AudioTrack.WELSH_SLOW


class TestToSpeechText:
    def test_the_english_track_speaks_the_english(self) -> None:
        assert to_speech_text(EXERCISE, AudioTrack.ENGLISH) == "I can go"

    @pytest.mark.parametrize(
        "track", (AudioTrack.WELSH_STANDARD, AudioTrack.WELSH_SLOW)
    )
    def test_both_welsh_tracks_speak_the_welsh(self, track: AudioTrack) -> None:
        assert to_speech_text(EXERCISE, track) == "Galla i fynd"
