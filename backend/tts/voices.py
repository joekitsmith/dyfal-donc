from collections.abc import Mapping
from dataclasses import dataclass

from tts.tracks import Track

MINIMUM_LENGTH_SCALE = 1.0
MAXIMUM_LENGTH_SCALE = 3.0
ENGLISH_MODEL_FILE = "en_GB-alan-medium.onnx"
WELSH_MODEL_FILE = "cy_GB-bu_tts.onnx"
WELSH_WOMAN_SPEAKER = 0
WELSH_MAN_SPEAKER = 2
WELSH_NOISE_SCALE = 0.2
WELSH_RHYTHM_NOISE = 0.0
WELSH_WOMAN_SECONDS_PER_SOUND = 0.0807
WELSH_MAN_SECONDS_PER_SOUND = 0.104


@dataclass(frozen=True, slots=True, kw_only=True)
class FixedSpeed:
    """Stretch every phrase by the same factor. 1 is the voice's natural pace."""

    length_scale: float


@dataclass(frozen=True, slots=True, kw_only=True)
class EvenPace:
    """Stretch each phrase so that every sound takes about the same time.

    A single factor suits some phrases and rushes others, because the voice
    says some phrases faster than others. The factor is worked out from how
    long the phrase takes at its natural pace, and never exceeds ``ceiling``.
    """

    seconds_per_sound: float
    ceiling: float = MAXIMUM_LENGTH_SCALE


@dataclass(frozen=True, slots=True, kw_only=True)
class Voice:
    """How one track is spoken. ``None`` leaves a setting at the model's default."""

    model_file: str
    speaker_id: int | None
    speed: FixedSpeed | EvenPace
    noise_scale: float | None
    rhythm_noise: float | None


VOICES: Mapping[Track, Voice] = {
    Track.ENGLISH: Voice(
        model_file=ENGLISH_MODEL_FILE,
        speaker_id=None,
        speed=FixedSpeed(length_scale=1.0),
        noise_scale=None,
        rhythm_noise=None,
    ),
    Track.WELSH_STANDARD: Voice(
        model_file=WELSH_MODEL_FILE,
        speaker_id=WELSH_WOMAN_SPEAKER,
        speed=EvenPace(seconds_per_sound=WELSH_WOMAN_SECONDS_PER_SOUND),
        noise_scale=WELSH_NOISE_SCALE,
        rhythm_noise=WELSH_RHYTHM_NOISE,
    ),
    Track.WELSH_SLOW: Voice(
        model_file=WELSH_MODEL_FILE,
        speaker_id=WELSH_MAN_SPEAKER,
        speed=EvenPace(seconds_per_sound=WELSH_MAN_SECONDS_PER_SOUND),
        noise_scale=WELSH_NOISE_SCALE,
        rhythm_noise=WELSH_RHYTHM_NOISE,
    ),
}
