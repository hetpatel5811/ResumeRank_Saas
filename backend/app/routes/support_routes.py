from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.support_schema import SupportChatRequest, SupportChatResponse
from app.services.support_agent_service import generate_support_reply


router = APIRouter(prefix="/api/support", tags=["Support"])


@router.post("/chat", response_model=SupportChatResponse)
def support_chat(
    payload: SupportChatRequest,
    current_user: User = Depends(get_current_user),
):
    _ = current_user
    result = generate_support_reply(
        message=payload.message,
        page=payload.page,
        history=[item.model_dump() for item in payload.history],
    )
    return result
