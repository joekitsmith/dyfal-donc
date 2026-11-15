from pydantic import BaseModel


class TopicResponse(BaseModel):
    name: str
    requires: tuple[str, ...]


class CourseResponse(BaseModel):
    release: str
    item_count: int
    topics: tuple[TopicResponse, ...]
