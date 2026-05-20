PLAN_FREE = "free"
PLAN_PLUS = "plus"
PLAN_PRO = "pro"

VALID_PLANS = {PLAN_FREE, PLAN_PLUS, PLAN_PRO}

PLAN_SCAN_LIMITS = {
    PLAN_FREE: 3,
    PLAN_PLUS: 50,
    PLAN_PRO: None,
}

PLAN_LEVELS = {
    PLAN_FREE: 0,
    PLAN_PLUS: 1,
    PLAN_PRO: 2,
}

PLAN_DISPLAY_DATA = {
    PLAN_PLUS: {
        "name": "Plus",
        "description": "For active applicants who need a higher scan allowance.",
        "price_label": "₹49/mo",
        "features": [
            "Up to 50 scans",
            "Priority processing",
            "Premium support",
        ],
    },
    PLAN_PRO: {
        "name": "Pro",
        "description": "For heavy usage and power users who want no limits.",
        "price_label": "₹99/mo",
        "features": [
            "Unlimited scans",
            "Fastest processing",
            "Priority support",
        ],
    },
}


def get_scan_limit_for_plan(plan: str):
    normalized_plan = (plan or PLAN_FREE).lower()
    return PLAN_SCAN_LIMITS.get(normalized_plan, PLAN_SCAN_LIMITS[PLAN_FREE])


def can_upgrade_to_plan(current_plan: str, target_plan: str):
    current_level = PLAN_LEVELS.get((current_plan or PLAN_FREE).lower(), 0)
    target_level = PLAN_LEVELS.get((target_plan or "").lower())

    if target_level is None:
        return False

    return target_level > current_level
