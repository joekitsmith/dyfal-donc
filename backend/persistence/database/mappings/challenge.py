from persistence.database import models
from persistence.database.records import ChallengeRecord


def to_challenge_record(row: models.WebauthnChallenge) -> ChallengeRecord:
    return ChallengeRecord(
        challenge=row.challenge, purpose=row.purpose, user_id=row.user_id
    )
