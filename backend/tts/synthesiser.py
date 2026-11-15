import io
import wave
from collections.abc import Mapping
from pathlib import Path
from typing import Protocol

from piper import PiperVoice, SynthesisConfig

from tts.pace import even_pace_length_scale
from tts.tracks import Track
from tts.voices import VOICES, EvenPace, FixedSpeed, Voice


class Synthesiser(Protocol):
    def synthesise(self, text: str, track: Track) -> bytes:
        """The text spoken for the track, as a WAV file."""
        ...


class PiperSynthesiser:
    """Speaks with Piper. Each model file is loaded once, when this is created."""

    def __init__(
        self, models_directory: Path, voices: Mapping[Track, Voice] = VOICES
    ) -> None:
        self._voices = voices
        self._models = {
            model_file: PiperVoice.load(models_directory / model_file)
            for model_file in {voice.model_file for voice in voices.values()}
        }

    def synthesise(self, text: str, track: Track) -> bytes:
        voice = self._voices[track]
        model = self._models[voice.model_file]
        return _render(model, text, voice, self._length_scale(model, text, voice))

    def _length_scale(self, model: PiperVoice, text: str, voice: Voice) -> float:
        match voice.speed:
            case FixedSpeed(length_scale=length_scale):
                return length_scale
            case EvenPace() as pace:
                return even_pace_length_scale(
                    seconds_at_natural_pace=_seconds(_render(model, text, voice, 1.0)),
                    sound_count=_sound_count(model, text),
                    pace=pace,
                )


def _render(model: PiperVoice, text: str, voice: Voice, length_scale: float) -> bytes:
    config = SynthesisConfig(
        speaker_id=voice.speaker_id,
        length_scale=length_scale,
        noise_scale=voice.noise_scale,
        noise_w_scale=voice.rhythm_noise,
    )
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        model.synthesize_wav(text, wav_file, syn_config=config)

    return buffer.getvalue()


def _seconds(wav_bytes: bytes) -> float:
    with wave.open(io.BytesIO(wav_bytes)) as wav_file:
        return wav_file.getnframes() / wav_file.getframerate()


def _sound_count(model: PiperVoice, text: str) -> int:
    sounds = "".join("".join(sentence) for sentence in model.phonemize(text))
    return max(1, len(sounds.replace(" ", "")))
