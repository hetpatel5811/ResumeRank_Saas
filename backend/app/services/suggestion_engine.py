# from typing import List, Dict


# def generate_suggestions(score_data: Dict) -> List[Dict]:
#     suggestions = []

#     missing_skills = score_data.get("missing_skills", [])
#     missing_keywords = score_data.get("missing_keywords", [])

#     for skill in missing_skills[:5]:
#         suggestions.append({
#             "category": "skills",
#             "priority": "high",
#             "suggestion_text": f"Add or mention '{skill}' in your resume if you have real experience with it."
#         })

#     for keyword in missing_keywords[:5]:
#         suggestions.append({
#             "category": "keywords",
#             "priority": "medium",
#             "suggestion_text": f"Include the keyword '{keyword}' naturally in your project or experience bullet points."
#         })

#     if score_data.get("experience_score", 0) < 70:
#         suggestions.append({
#             "category": "experience",
#             "priority": "high",
#             "suggestion_text": "Your resume experience may not match the required years. Add clear dates and explain relevant project/work experience."
#         })

#     if score_data.get("format_score", 0) < 70:
#         suggestions.append({
#             "category": "format",
#             "priority": "medium",
#             "suggestion_text": "Improve resume format by adding clear sections like Summary, Skills, Experience, Projects, and Education."
#         })

#     if not suggestions:
#         suggestions.append({
#             "category": "general",
#             "priority": "low",
#             "suggestion_text": "Your resume is well matched. You can still improve by adding more measurable achievements."
#         })

#     return suggestions

from typing import List, Dict


def get_priority(score: int) -> str:
    if score < 50:
        return "high"
    if score < 75:
        return "medium"
    return "low"


def generate_suggestions(score_data: Dict) -> List[Dict]:
    suggestions = []

    missing_skills = score_data.get("missing_skills", [])
    missing_keywords = score_data.get("missing_keywords", [])

    keyword_score = score_data.get("keyword_score", 0)
    skills_score = score_data.get("skills_score", 0)
    experience_score = score_data.get("experience_score", 0)
    format_score = score_data.get("format_score", 0)
    overall_score = score_data.get("overall_score", 0)

    # Skills suggestions
    for skill in missing_skills[:7]:
        suggestions.append({
            "category": "skills",
            "priority": "high" if skills_score < 70 else "medium",
            "suggestion_text": (
                f"Add '{skill}' to your Skills or Projects section only if you have real hands-on experience with it."
            )
        })

    # Keyword suggestions
    for keyword in missing_keywords[:7]:
        suggestions.append({
            "category": "keywords",
            "priority": "medium",
            "suggestion_text": (
                f"Use the keyword '{keyword}' naturally in your resume summary, project description, or experience bullet points."
            )
        })

    # Keyword score based suggestion
    if keyword_score < 50:
        suggestions.append({
            "category": "keywords",
            "priority": "high",
            "suggestion_text": (
                "Your resume has low keyword similarity with the job description. Add more role-specific terms from the JD in a natural way."
            )
        })
    elif keyword_score < 75:
        suggestions.append({
            "category": "keywords",
            "priority": "medium",
            "suggestion_text": (
                "Your resume partially matches the job description. Improve alignment by adding important missing keywords."
            )
        })

    # Skills score based suggestion
    if skills_score < 50:
        suggestions.append({
            "category": "skills",
            "priority": "high",
            "suggestion_text": (
                "Your skills section does not strongly match the JD. Add relevant technologies in a dedicated Skills section."
            )
        })
    elif skills_score < 75:
        suggestions.append({
            "category": "skills",
            "priority": "medium",
            "suggestion_text": (
                "Your skills match is decent, but you can improve it by grouping skills into Languages, Frameworks, Databases, and Cloud/DevOps."
            )
        })

    # Experience suggestion
    if experience_score < 50:
        suggestions.append({
            "category": "experience",
            "priority": "high",
            "suggestion_text": (
                "Your resume does not clearly show the required years of experience. Add clear dates, role titles, and project duration."
            )
        })
    elif experience_score < 75:
        suggestions.append({
            "category": "experience",
            "priority": "medium",
            "suggestion_text": (
                "Your experience is close to the requirement. Highlight relevant backend/project experience more clearly."
            )
        })

    # Format suggestion
    if format_score < 50:
        suggestions.append({
            "category": "format",
            "priority": "high",
            "suggestion_text": (
                "Your resume format may not be ATS-friendly. Use clear sections: Summary, Skills, Experience, Projects, Education."
            )
        })
    elif format_score < 75:
        suggestions.append({
            "category": "format",
            "priority": "medium",
            "suggestion_text": (
                "Improve resume formatting by keeping consistent dates, bullet points, and section headings."
            )
        })

    # Overall suggestion
    if overall_score >= 85:
        suggestions.append({
            "category": "overall",
            "priority": "low",
            "suggestion_text": (
                "Your resume is strongly aligned with this job. Make small improvements by adding measurable impact in bullet points."
            )
        })
    elif overall_score >= 70:
        suggestions.append({
            "category": "overall",
            "priority": "medium",
            "suggestion_text": (
                "Your resume is a good match. Improve missing skills and keywords to increase your score."
            )
        })
    else:
        suggestions.append({
            "category": "overall",
            "priority": "high",
            "suggestion_text": (
                "Your resume needs stronger alignment with this JD. Focus on missing skills, keywords, and clear project impact."
            )
        })

    # Remove duplicate suggestion text
    unique_suggestions = []
    seen_texts = set()

    for item in suggestions:
        if item["suggestion_text"] not in seen_texts:
            unique_suggestions.append(item)
            seen_texts.add(item["suggestion_text"])

    return unique_suggestions[:15]