class ExerciseNotFoundError(Exception):
    pass


class SpeechUnavailableError(Exception):
    """The speech service did not give audio."""
