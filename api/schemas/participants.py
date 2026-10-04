"""Contracts used when participants create or update their profile."""
from pydantic import BaseModel, Field
class RegisterParticipantRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    bio: str = Field(default="", max_length=500)
class ParticipantResponse(BaseModel):
    id: str
    name: str
    bio: str
