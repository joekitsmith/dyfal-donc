import pytest

from tts.pace import even_pace_length_scale
from tts.voices import MINIMUM_LENGTH_SCALE, EvenPace

PACE = EvenPace(seconds_per_sound=0.1, ceiling=3.0)


class TestEvenPaceLengthScale:
    def test_stretches_a_phrase_that_is_quicker_than_the_pace(self) -> None:
        scale = even_pace_length_scale(
            seconds_at_natural_pace=1.0, sound_count=15, pace=PACE
        )

        assert scale == pytest.approx(1.5)

    def test_gives_the_same_pace_to_phrases_of_different_speed(self) -> None:
        fast = even_pace_length_scale(
            seconds_at_natural_pace=0.8, sound_count=20, pace=PACE
        )
        slow = even_pace_length_scale(
            seconds_at_natural_pace=1.6, sound_count=20, pace=PACE
        )

        assert 0.8 * fast == pytest.approx(1.6 * slow)

    def test_never_speeds_a_phrase_up(self) -> None:
        scale = even_pace_length_scale(
            seconds_at_natural_pace=5.0, sound_count=10, pace=PACE
        )

        assert scale == MINIMUM_LENGTH_SCALE

    def test_never_stretches_past_the_ceiling(self) -> None:
        scale = even_pace_length_scale(
            seconds_at_natural_pace=0.1, sound_count=50, pace=PACE
        )

        assert scale == PACE.ceiling

    def test_a_phrase_with_no_audio_is_left_alone(self) -> None:
        scale = even_pace_length_scale(
            seconds_at_natural_pace=0.0, sound_count=5, pace=PACE
        )

        assert scale == MINIMUM_LENGTH_SCALE
