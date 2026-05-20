from typing import Literal, Optional

from pydantic import BaseModel


class SupportMessageItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class SupportChatRequest(BaseModel):
    message: str
    page: Optional[str] = None
    history: list[SupportMessageItem] = []


class SupportChatResponse(BaseModel):
    answer: str
    suggested_actions: list[str]
    ai_enabled: bool
