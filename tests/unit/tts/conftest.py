import pytest

from tts.tracks import Track


class FakeSynthesiser:
    """Answers with the text and track it was asked for, so tests can see them."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, Track]] = []

    def synthesise(self, text: str, track: Track) -> bytes:
        self.calls.append((text, track))
        return b"RIFF" + f"{track.value}:{text}".encode()


@pytest.fixture
def synthesiser() -> FakeSynthesiser:
    return FakeSynthesiser()
