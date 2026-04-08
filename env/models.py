from pydantic import BaseModel
from typing import List, Optional, Literal, Dict, Any


class Email(BaseModel):
    id: str
    subject: str
    body: str
    is_spam: bool = False
    category: Optional[str] = None
    archived: bool = False
    replied: bool = False


class Observation(BaseModel):
    inbox: List[Email]
    current_email_id: Optional[str] = None
    draft_response: Optional[str] = None
    echoed_message: str = ""


class Action(BaseModel):
    action_type: Literal[
        "open_email",
        "classify",
        "draft_reply",
        "send_reply",
        "archive"
    ]
    email_id: Optional[str] = None
    content: Optional[str] = None


class StepResult(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: Dict[str, Any] = {}