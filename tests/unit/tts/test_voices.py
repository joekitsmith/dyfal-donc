import pytest

from tts.tracks import Track
from tts.voices import MAXIMUM_LENGTH_SCALE, VOICES, EvenPace


class TestVoices:
    @pytest.mark.parametrize("track", Track)
    def test_every_track_has_a_voice(self, track: Track) -> None:
        assert track in VOICES

    def test_the_two_welsh_tracks_are_different_speakers_of_one_model(self) -> None:
        woman, man = VOICES[Track.WELSH_STANDARD], VOICES[Track.WELSH_SLOW]

        assert woman.model_file == man.model_file
        assert woman.speaker_id != man.speaker_id

    def test_english_is_a_different_model_from_welsh(self) -> None:
        assert (
            VOICES[Track.ENGLISH].model_file != VOICES[Track.WELSH_STANDARD].model_file
        )

    def test_the_slow_welsh_track_takes_longer_for_each_sound(self) -> None:
        woman, man = VOICES[Track.WELSH_STANDARD].speed, VOICES[Track.WELSH_SLOW].speed

        assert isinstance(woman, EvenPace)
        assert isinstance(man, EvenPace)
        assert man.seconds_per_sound > woman.seconds_per_sound

    def test_a_stretch_has_a_ceiling(self) -> None:
        assert EvenPace(seconds_per_sound=0.1).ceiling == MAXIMUM_LENGTH_SCALE
