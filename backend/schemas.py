from pydantic import BaseModel

class StudyRequest(BaseModel):
    text: str
    mode: str