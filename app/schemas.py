from typing import Any
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

class RoomInput(BaseModel):
    room_type: str = Field(min_length=2, max_length=50)
    quantity: int = Field(ge=1, le=50)

class HomeRequest(BaseModel):
    budget: int = Field(gt=0, le=10_000_000)
    rooms: list[RoomInput] = Field(min_length=1, max_length=20)
    style: str = Field(default="modern", max_length=80)
    notes: str = Field(default="", max_length=1000)

class PartyRequest(BaseModel):
    budget: int = Field(gt=0, le=10_000_000)
    guest_count: int = Field(gt=0, le=10_000)
    event_type: str = Field(min_length=2, max_length=80)
    venue_type: str = Field(default="indoor", max_length=80)
    city: str = Field(default="", max_length=100)
    notes: str = Field(default="", max_length=1000)

class RecommendationItem(BaseModel):
    category: str
    name: str
    estimated_price: int = Field(ge=0)
    quantity: int = Field(default=1, ge=1)
    platform: str
    search_url: str
    reason: str
    budget_share: int = Field(default=0, ge=0)

class RecommendationResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    planner: str
    budget: int
    allocated_total: int
    remaining: int
    summary: str
    tips: list[str]
    items: list[RecommendationItem]
    ai_powered: bool
    source_note: str
    history_id: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
