import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import settings
from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.billing_schema import (
    PlanOption,
    PlansResponse,
    SubscriptionCreateRequest,
    SubscriptionCreateResponse,
    SubscriptionStatusResponse,
)
from app.services.plan_service import (
    PLAN_DISPLAY_DATA,
    PLAN_PLUS,
    PLAN_PRO,
    can_upgrade_to_plan,
)
from app.services.razorpay_service import (
    razorpay_api_request,
    verify_razorpay_webhook_signature,
)


router = APIRouter(prefix="/api/billing", tags=["Billing"])


PLAN_RAZORPAY_IDS = {
    PLAN_PLUS: settings.RAZORPAY_PLUS_PLAN_ID,
    PLAN_PRO: settings.RAZORPAY_PRO_PLAN_ID,
}

ACTIVE_SUBSCRIPTION_STATUSES = {"authenticated", "active"}
PENDING_SUBSCRIPTION_STATUSES = {"created", "pending", "halted"}


def _get_metadata_from_subscription(subscription: dict):
    notes = subscription.get("notes")
    if isinstance(notes, dict):
        return notes
    return {}


def _get_plan_from_subscription(subscription: dict):
    metadata = _get_metadata_from_subscription(subscription)
    selected_plan = (metadata.get("plan") or "").lower()

    if selected_plan in {PLAN_PLUS, PLAN_PRO}:
        return selected_plan

    subscription_plan_id = subscription.get("plan_id")

    for plan_name, configured_plan_id in PLAN_RAZORPAY_IDS.items():
        if configured_plan_id and configured_plan_id == subscription_plan_id:
            return plan_name

    return None


def _payment_state_for_subscription(status_value: str):
    normalized = (status_value or "").lower()

    if normalized in ACTIVE_SUBSCRIPTION_STATUSES:
        return "paid"
    if normalized in PENDING_SUBSCRIPTION_STATUSES:
        return "pending"
    return "unpaid"


def _apply_plan_to_user(
    db: Session,
    user_id: str | None,
    plan: str | None,
):
    if not user_id or plan not in {PLAN_PLUS, PLAN_PRO}:
        return None

    try:
        parsed_user_id = UUID(user_id)
    except ValueError:
        return None

    user = db.query(User).filter(User.id == parsed_user_id).first()

    if not user:
        return None

    if user.plan != plan:
        user.plan = plan
        db.commit()
        db.refresh(user)

    return user


def _sync_user_plan_from_subscription(db: Session, subscription: dict):
    status_value = (subscription.get("status") or "").lower()

    if status_value not in ACTIVE_SUBSCRIPTION_STATUSES:
        return None

    metadata = _get_metadata_from_subscription(subscription)
    resolved_plan = _get_plan_from_subscription(subscription)
    user_id = metadata.get("user_id")

    return _apply_plan_to_user(
        db=db,
        user_id=user_id,
        plan=resolved_plan,
    )


@router.get("/plans", response_model=PlansResponse)
def get_plan_options(current_user: User = Depends(get_current_user)):
    current_plan = (current_user.plan or "free").lower()
    options = []

    for plan_id in [PLAN_PLUS, PLAN_PRO]:
        data = PLAN_DISPLAY_DATA[plan_id]
        options.append(
            PlanOption(
                id=plan_id,
                name=data["name"],
                description=data["description"],
                price_label=data["price_label"],
                features=data["features"],
                is_current=current_plan == plan_id,
                can_purchase=can_upgrade_to_plan(current_plan, plan_id),
            )
        )

    return PlansResponse(current_plan=current_plan, plans=options)


@router.post("/subscriptions", response_model=SubscriptionCreateResponse)
def create_subscription(
    payload: SubscriptionCreateRequest,
    current_user: User = Depends(get_current_user),
):
    selected_plan = payload.plan.lower()
    current_plan = (current_user.plan or "free").lower()

    if selected_plan not in PLAN_RAZORPAY_IDS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan selected."
        )

    if not can_upgrade_to_plan(current_plan, selected_plan):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected plan cannot be purchased from your current tier."
        )

    plan_id = PLAN_RAZORPAY_IDS[selected_plan]

    if not plan_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Razorpay plan ID is not configured for {selected_plan}."
        )

    subscription = razorpay_api_request(
        method="POST",
        endpoint="/subscriptions",
        payload={
            "plan_id": plan_id,
            "total_count": 1200,
            "quantity": 1,
            "customer_notify": True,
            "notes": {
                "user_id": str(current_user.id),
                "plan": selected_plan,
                "email": current_user.email,
            },
        }
    )

    auth_url = subscription.get("short_url")
    subscription_id = subscription.get("id")

    if not auth_url or not subscription_id:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Razorpay did not return subscription checkout details."
        )

    return SubscriptionCreateResponse(
        subscription_id=subscription_id,
        auth_url=auth_url,
    )


@router.get("/subscriptions/{subscription_id}", response_model=SubscriptionStatusResponse)
def get_subscription_status(
    subscription_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subscription = razorpay_api_request(
        method="GET",
        endpoint=f"/subscriptions/{subscription_id}",
    )

    metadata = _get_metadata_from_subscription(subscription)
    owner_id = metadata.get("user_id")

    if owner_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot access this subscription."
        )

    updated_user = _sync_user_plan_from_subscription(db, subscription)
    applied_plan = (updated_user.plan if updated_user else current_user.plan or "free").lower()
    subscription_status = (subscription.get("status") or "").lower()

    return SubscriptionStatusResponse(
        subscription_id=subscription.get("id"),
        status=subscription_status,
        payment_state=_payment_state_for_subscription(subscription_status),
        plan_applied=applied_plan,
    )


@router.post("/webhook")
async def razorpay_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    raw_body = await request.body()
    signature = request.headers.get("x-razorpay-signature")
    verify_razorpay_webhook_signature(raw_body, signature)

    try:
        event_data = json.loads(raw_body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook payload."
        ) from exc

    event_name = event_data.get("event") or ""

    if event_name.startswith("subscription."):
        subscription = (
            event_data.get("payload", {})
            .get("subscription", {})
            .get("entity", {})
        )
        if subscription:
            _sync_user_plan_from_subscription(db, subscription)

    return {"received": True}
