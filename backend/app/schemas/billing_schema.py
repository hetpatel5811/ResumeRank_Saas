from typing import Literal

from pydantic import BaseModel


class PlanOption(BaseModel):
    id: Literal["plus", "pro"]
    name: str
    description: str
    price_label: str
    features: list[str]
    is_current: bool
    can_purchase: bool


class PlansResponse(BaseModel):
    current_plan: str
    plans: list[PlanOption]


class SubscriptionCreateRequest(BaseModel):
    plan: Literal["plus", "pro"]


class SubscriptionCreateResponse(BaseModel):
    subscription_id: str
    auth_url: str


class SubscriptionStatusResponse(BaseModel):
    subscription_id: str
    status: str
    payment_state: str
    plan_applied: str
