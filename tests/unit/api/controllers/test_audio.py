import pytest

from api.controllers import speak_exercise
from api.course import CourseRelease, load_course_release
from api.errors import ExerciseNotFoundError, SpeechUnavailableError
from api.schemas import AudioTrack
from api.settings import DEFAULT_CURRICULUM_DIRECTORY
from tests.unit.api.conftest import FakeSpeechClient


@pytest.fixture(scope="module")
def release() -> CourseRelease:
    return load_course_release(DEFAULT_CURRICULUM_DIRECTORY)


class TestSpeakExercise:
    def test_speaks_the_courses_own_english(
        self, release: CourseRelease, speech_client: FakeSpeechClient
    ) -> None:
        speak_exercise(release, speech_client, "i-can-go", AudioTrack.ENGLISH)

        assert speech_client.calls == [("I can go", AudioTrack.ENGLISH)]

    @pytest.mark.parametrize(
        "track", (AudioTrack.WELSH_STANDARD, AudioTrack.WELSH_SLOW)
    )
    def test_speaks_the_courses_own_welsh(
        self, release: CourseRelease, speech_client: FakeSpeechClient, track: AudioTrack
    ) -> None:
        speak_exercise(release, speech_client, "i-can-go", track)

        assert speech_client.calls == [("Galla i fynd", track)]

    def test_returns_the_audio(
        self, release: CourseRelease, speech_client: FakeSpeechClient
    ) -> None:
        audio = speak_exercise(
            release, speech_client, "i-can-go", AudioTrack.WELSH_STANDARD
        )

        assert audio == b"RIFFwelsh-standard:Galla i fynd"

    def test_an_unknown_exercise_is_not_spoken(
        self, release: CourseRelease, speech_client: FakeSpeechClient
    ) -> None:
        with pytest.raises(ExerciseNotFoundError, match="nonsense"):
            speak_exercise(release, speech_client, "nonsense", AudioTrack.ENGLISH)

        assert speech_client.calls == []

    def test_lets_an_unavailable_service_through(
        self, release: CourseRelease, speech_client: FakeSpeechClient
    ) -> None:
        speech_client.unavailable = True

        with pytest.raises(SpeechUnavailableError):
            speak_exercise(release, speech_client, "i-can-go", AudioTrack.ENGLISH)
