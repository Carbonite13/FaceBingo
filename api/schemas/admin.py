"""Administrative API contracts."""
from pydantic import BaseModel
class EventStatusUpdate(BaseModel):
    active: bool | None = None
    registration_required: bool | None = None
class EventStatusResponse(BaseModel):
    active: bool
    registration_required: bool
