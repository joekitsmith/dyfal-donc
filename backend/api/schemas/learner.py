import uuid
from datetime import datetime

from pydantic import BaseModel


class LearnerResponse(BaseModel):
    id: uuid.UUID
    course_release: str
    created_at: datetime
