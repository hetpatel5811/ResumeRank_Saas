from typing import Dict, List


CATEGORY_WEIGHTS = {
    "keyword_score": 0.35,
    "skills_score": 0.30,
    "experience_score": 0.20,
    "format_score": 0.15,
}

CATEGORY_LABELS = {
    "keyword_score": "Keyword Match",
    "skills_score": "Skills Match",
    "experience_score": "Experience",
    "format_score": "Format",
}


def build_score_diagnostics(score_data: Dict) -> Dict:
    weighted_breakdown: List[Dict] = []
    top_improvement_areas: List[Dict] = []

    for key, weight in CATEGORY_WEIGHTS.items():
        raw_score = int(score_data.get(key, 0))
        contribution = round(raw_score * weight, 2)
        potential_lift = round((100 - raw_score) * weight, 2)

        weighted_breakdown.append(
            {
                "category": CATEGORY_LABELS[key],
                "score": raw_score,
                "weight": weight,
                "contribution": contribution,
            }
        )

        top_improvement_areas.append(
            {
                "category": CATEGORY_LABELS[key],
                "score": raw_score,
                "potential_lift": potential_lift,
            }
        )

    top_improvement_areas = sorted(
        top_improvement_areas,
        key=lambda item: item["potential_lift"],
        reverse=True
    )

    return {
        "weighted_breakdown": weighted_breakdown,
        "top_improvement_areas": top_improvement_areas[:3],
        "high_impact_keywords": score_data.get("missing_keywords", [])[:8],
        "high_impact_skills": score_data.get("missing_skills", [])[:6],
    }
