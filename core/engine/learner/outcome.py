from enum import StrEnum


class Outcome(StrEnum):
    """How the learner got on with an exercise.

    A learner who says nothing is assumed to have got it. Only a reported miss
    is recorded as ``MISSED_IT``, so a missed exercise can come round again.
    """

    GOT_IT = "got_it"
    MISSED_IT = "missed_it"
