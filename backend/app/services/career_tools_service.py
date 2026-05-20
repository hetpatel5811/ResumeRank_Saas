from typing import Dict, List

from app.services.scoring_engine import extract_top_keywords


def _pick_tone_phrase(tone: str) -> str:
    tone_map = {
        "professional": "I am excited to apply",
        "confident": "I am confident that my background aligns strongly",
        "concise": "I would like to apply",
    }
    return tone_map.get(tone, tone_map["professional"])


def generate_cover_letter(
    target_role: str,
    company_name: str,
    job_description: str,
    resume_points: List[str],
    tone: str,
) -> Dict:
    top_keywords = extract_top_keywords(job_description, top_n=10)
    keyword_line = ", ".join(top_keywords[:5]) if top_keywords else "the required skills"

    filtered_points = [point.strip() for point in resume_points if point.strip()]
    if not filtered_points:
        filtered_points = [
            "Delivered projects with measurable business impact.",
            "Collaborated across teams to solve technical and process challenges.",
            "Continuously improved quality, reliability, and delivery speed.",
        ]

    intro = (
        f"Dear Hiring Manager,\n\n"
        f"{_pick_tone_phrase(tone)} for the {target_role} role at {company_name}. "
        f"After reviewing the job description, I see strong alignment with {keyword_line}."
    )

    body_lines = []
    for point in filtered_points[:3]:
        body_lines.append(f"- {point}")

    body = (
        "\n\nIn my recent work, I have:\n"
        + "\n".join(body_lines)
        + "\n\nI can contribute quickly by applying these strengths to your team goals."
    )

    closing = (
        "\n\nThank you for your time and consideration. I would value the opportunity "
        "to discuss how I can support your team.\n\nSincerely,\n[Your Name]"
    )

    checklist = [
        "Replace [Your Name] with your details.",
        "Add one quantified achievement per bullet where possible.",
        "Mirror exact terminology from the job description naturally.",
    ]

    return {
        "cover_letter": intro + body + closing,
        "checklist": checklist,
    }


def optimize_linkedin_profile(linkedin_text: str, job_description: str) -> Dict:
    jd_keywords = extract_top_keywords(job_description, top_n=20)
    profile_keywords = set(word.lower() for word in extract_top_keywords(linkedin_text, top_n=40))

    missing_keywords = [kw for kw in jd_keywords if kw.lower() not in profile_keywords][:10]
    top_role_keywords = jd_keywords[:3] if jd_keywords else ["Product Development", "Stakeholder Collaboration", "Execution"]

    optimized_headline = (
        f"{top_role_keywords[0]} | {top_role_keywords[1]} | {top_role_keywords[2]}"
    )

    about_suggestions = [
        "Start with your years of experience and core domain focus.",
        "Add one line on business outcomes with metrics.",
        "Include tools/skills that directly match your target jobs.",
        "End with the type of opportunities you are targeting.",
    ]

    return {
        "optimized_headline": optimized_headline,
        "about_suggestions": about_suggestions,
        "missing_keywords": missing_keywords,
    }


def generate_interview_questions(
    target_role: str,
    job_description: str,
    experience_level: str,
) -> Dict:
    keywords = extract_top_keywords(job_description, top_n=12)
    top_focus = keywords[:4] if keywords else ["problem solving", "ownership", "communication", "execution"]

    seniority_line = {
        "fresher": "entry-level execution and learning agility",
        "mid": "independent delivery and cross-team collaboration",
        "senior": "strategy, leadership, and system-level ownership",
    }.get(experience_level, "independent delivery and collaboration")

    questions = [
        {
            "category": "behavioral",
            "question": f"Tell me about a time you solved a difficult problem related to {top_focus[0]}.",
            "why_it_matters": "Assesses structured thinking and practical impact."
        },
        {
            "category": "behavioral",
            "question": "Describe a situation where you handled conflicting priorities and still delivered.",
            "why_it_matters": "Evaluates prioritization and execution discipline."
        },
        {
            "category": "technical",
            "question": f"How would you approach implementing {top_focus[1]} for a real project?",
            "why_it_matters": "Checks technical depth and applied reasoning."
        },
        {
            "category": "technical",
            "question": f"What trade-offs would you consider when scaling work involving {top_focus[2]}?",
            "why_it_matters": "Measures architecture and decision-making quality."
        },
        {
            "category": "role-fit",
            "question": f"For this {target_role} role, how do you demonstrate {seniority_line}?",
            "why_it_matters": "Confirms role-level fit and communication clarity."
        },
        {
            "category": "project",
            "question": "Walk through a recent project from problem statement to measurable outcome.",
            "why_it_matters": "Validates end-to-end ownership and impact storytelling."
        },
    ]

    return {"questions": questions}


def optimize_resume_bullets(bullet_points: List[str], job_description: str) -> Dict:
    keywords = extract_top_keywords(job_description, top_n=12)
    selected_keywords = keywords[:6]
    optimized = []

    for idx, bullet in enumerate(bullet_points):
        clean = bullet.strip().rstrip(".")
        if not clean:
            continue

        keyword = selected_keywords[idx % len(selected_keywords)] if selected_keywords else "role-specific requirements"
        rewritten = f"{clean}, aligned with {keyword}, and delivered measurable business value."

        optimized.append(
            {
                "original": bullet,
                "optimized": rewritten,
                "reasoning": f"Adds stronger outcome language and incorporates keyword '{keyword}'."
            }
        )

    return {
        "optimized_bullets": optimized,
        "keywords_used": selected_keywords,
    }


def _tone_opening(tone: str) -> str:
    return {
        "professional": "I hope you are doing well.",
        "warm": "I hope your week is going great.",
        "concise": "I hope you are well.",
    }.get(tone, "I hope you are doing well.")


def _tone_close(tone: str) -> str:
    return {
        "professional": "Thank you for your time and consideration.",
        "warm": "Thanks again for your time and support.",
        "concise": "Thanks for your time.",
    }.get(tone, "Thank you for your time and consideration.")


def _format_highlights(highlights: List[str]) -> str:
    clean_points = [point.strip() for point in highlights if point and point.strip()]
    if not clean_points:
        clean_points = [
            "Strong role alignment with the posted requirements",
            "Relevant project outcomes with measurable impact",
        ]

    lines = [f"- {item}" for item in clean_points[:3]]
    return "\n".join(lines)


def generate_follow_up_email(
    target_role: str,
    company_name: str,
    context_notes: str,
    highlights: List[str],
    tone: str,
) -> Dict:
    subject = f"Follow-up on {target_role} application - {company_name}"
    highlight_block = _format_highlights(highlights)

    body = (
        f"Hi Hiring Team,\n\n"
        f"{_tone_opening(tone)} I wanted to follow up on my application for the "
        f"{target_role} role at {company_name}. {context_notes.strip()}\n\n"
        f"I believe I can contribute quickly in this role, especially through:\n"
        f"{highlight_block}\n\n"
        f"{_tone_close(tone)}\n\n"
        "Best regards,\n"
        "[Your Name]"
    )

    checklist = [
        "Replace [Your Name] and add your contact details.",
        "Mention exact application or interview date if available.",
        "Keep follow-up under 140 words for better response rates.",
    ]

    return {
        "subject": subject,
        "body": body,
        "checklist": checklist,
    }


def generate_thank_you_email(
    target_role: str,
    company_name: str,
    context_notes: str,
    highlights: List[str],
    tone: str,
) -> Dict:
    subject = f"Thank you - {target_role} interview"
    highlight_block = _format_highlights(highlights)

    body = (
        f"Hi Interview Panel,\n\n"
        f"{_tone_opening(tone)} Thank you for taking the time to speak with me about the "
        f"{target_role} role at {company_name}. {context_notes.strip()}\n\n"
        f"I enjoyed discussing how I can help with:\n"
        f"{highlight_block}\n\n"
        f"{_tone_close(tone)} I would be excited to contribute to your team.\n\n"
        "Best regards,\n"
        "[Your Name]"
    )

    checklist = [
        "Send within 24 hours of your interview.",
        "Reference one specific discussion point for personalization.",
        "Keep the tone positive and concise.",
    ]

    return {
        "subject": subject,
        "body": body,
        "checklist": checklist,
    }
