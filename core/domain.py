from pydantic import BaseModel

class ParticipantProfile(BaseModel):
    id: str | None = None
    name: str
    bio: str
