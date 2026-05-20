from typing import Dict, List

from app.config import settings

try:
    from openai import OpenAI
except ModuleNotFoundError:  # pragma: no cover
    OpenAI = None


SUPPORT_SYSTEM_PROMPT = """
You are ResumeRank Support Assistant.
Help users solve issues in this web app with clear, practical steps.

Current product areas:
- Authentication (register, login, token session)
- Resume analysis (PDF/DOCX upload, JD match score, skill/keyword suggestions)
- Scan history and delete scan
- Billing page exists but payments may be unavailable during onboarding
- Job tracker pipeline
- Career tools: cover letter, LinkedIn optimizer, interview practice, bullet optimizer

Rules:
- Be concise and actionable.
- Prefer numbered troubleshooting steps.
- If user asks for unavailable feature, acknowledge and provide workaround.
- Never invent backend states or claim you performed actions.
- Do not request secrets (API keys/passwords).
"""


def _build_context_message(user_message: str, page: str | None, history: List[Dict]) -> str:
    clipped_history = history[-8:]
    transcript_lines = []
    for item in clipped_history:
        role = item.get("role", "user").upper()
        content = (item.get("content", "") or "").strip()
        if content:
            transcript_lines.append(f"{role}: {content}")

    transcript = "\n".join(transcript_lines) if transcript_lines else "No prior messages."
    page_text = page or "unknown"

    return (
        f"Current page: {page_text}\n"
        f"Conversation history:\n{transcript}\n\n"
        f"User message:\n{user_message.strip()}\n\n"
        "Respond with practical support guidance."
    )


def _fallback_response() -> Dict:
    return {
        "answer": (
            "Support AI is not enabled yet. You can still try these steps:\n"
            "1. Refresh the page and log in again.\n"
            "2. Re-check your file format (PDF/DOCX) and internet connection.\n"
            "3. If payments fail, wait until Razorpay onboarding is fully approved.\n"
            "4. If the issue persists, share exact error text and page name in support."
        ),
        "suggested_actions": [
            "Refresh and retry",
            "Verify file format and token session",
            "Share exact error message",
        ],
        "ai_enabled": False,
    }


def generate_support_reply(message: str, page: str | None, history: List[Dict]) -> Dict:
    if not settings.OPENAI_API_KEY or OpenAI is None:
        return _fallback_response()

    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        response = client.responses.create(
            model=settings.OPENAI_SUPPORT_MODEL,
            input=[
                {"role": "system", "content": SUPPORT_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": _build_context_message(
                        user_message=message,
                        page=page,
                        history=history,
                    ),
                },
            ],
        )

        answer_text = (getattr(response, "output_text", "") or "").strip()
        if not answer_text:
            answer_text = "I could not generate a response right now. Please retry in a moment."

        suggested_actions = [
            "Try the suggested steps in order",
            "If issue remains, copy exact error text",
            "Retry after a fresh login session",
        ]

        return {
            "answer": answer_text,
            "suggested_actions": suggested_actions,
            "ai_enabled": True,
        }
    except Exception:
        return _fallback_response()
