from tts.voices import MINIMUM_LENGTH_SCALE, EvenPace


def even_pace_length_scale(
    *, seconds_at_natural_pace: float, sound_count: int, pace: EvenPace
) -> float:
    """The stretch that makes a phrase take ``seconds_per_sound`` for each sound.

    Never faster than natural, and never past the pace's ceiling. A phrase with
    no audio has nothing to stretch.
    """
    if seconds_at_natural_pace <= 0:
        return MINIMUM_LENGTH_SCALE

    wanted = pace.seconds_per_sound * sound_count / seconds_at_natural_pace
    return min(pace.ceiling, max(MINIMUM_LENGTH_SCALE, wanted))
