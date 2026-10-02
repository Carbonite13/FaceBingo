from pydantic import BaseModel

class ParticipantProfile(BaseModel):
    name: str
    bio: str
