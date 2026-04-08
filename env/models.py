from pydantic import BaseModel
from typing import List, Optional, Literal


class Email(BaseModel):
    id: str
    subject: str
    body: str
    category: Literal["spam", "complaint", "inquiry"]
    urgency: int  # 1–5
    archived: bool = False
    replied: bool = False


class Observation(BaseModel):
    inbox: List[Email]
    current_email_id: Optional[str] = None
    draft_response: Optional[str] = None
    echoed_message: str


class Action(BaseModel):
    action_type: Literal["archive", "send_reply"]
    email_id: Optional[str]


class Reward(BaseModel):
    value: float