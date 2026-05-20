import re
from typing import Dict, List

from app.services.scoring_engine import extract_top_keywords, normalize_text


COMMON_SECTION_ALIASES = {
    "summary": ["summary", "professional summary", "profile", "objective"],
    "experience": ["experience", "work experience", "professional experience", "employment"],
    "skills": ["skills", "technical skills", "core competencies"],
    "education": ["education", "academic background", "qualification"],
    "projects": ["projects", "project experience", "academic projects"],
    "certifications": ["certifications", "licenses", "certificates"],
}


def _check_file_type(resume_filename: str) -> Dict:
    lower = (resume_filename or "").lower()
    passed = lower.endswith(".pdf") or lower.endswith(".docx")
    return {
        "check_id": "file_type",
        "title": "File Type",
        "status": "pass" if passed else "fail",
        "severity": "high" if not passed else "low",
        "message": "Use PDF or DOCX format for better ATS parsing."
    }


def _check_contact_details(resume_text: str) -> Dict:
    text = resume_text or ""
    has_email = bool(re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text))
    has_phone = bool(re.search(r"(\+?\d[\d\s\-()]{8,}\d)", text))
    passed = has_email and has_phone

    return {
        "check_id": "contact_details",
        "title": "Contact Information",
        "status": "pass" if passed else "fail",
        "severity": "high" if not passed else "low",
        "message": "Include both a professional email and a phone number."
    }


def _check_standard_sections(resume_text: str) -> Dict:
    lower = (resume_text or "").lower()
    found_sections = []

    for canonical, aliases in COMMON_SECTION_ALIASES.items():
        if any(alias in lower for alias in aliases):
            found_sections.append(canonical)

    core_sections = {"summary", "experience", "skills", "education"}
    found_core_count = len(core_sections.intersection(set(found_sections)))

    if found_core_count >= 4:
        status_value = "pass"
        severity = "low"
    elif found_core_count >= 3:
        status_value = "warn"
        severity = "medium"
    else:
        status_value = "fail"
        severity = "high"

    return {
        "check_id": "sections",
        "title": "Standard Section Headings",
        "status": status_value,
        "severity": severity,
        "message": "Use clear headings like Summary, Experience, Skills, and Education."
    }


def _check_word_count(resume_text: str) -> Dict:
    words = (resume_text or "").split()
    word_count = len(words)

    if 350 <= word_count <= 1000:
        status_value = "pass"
        severity = "low"
    elif 250 <= word_count < 350 or 1000 < word_count <= 1200:
        status_value = "warn"
        severity = "medium"
    else:
        status_value = "fail"
        severity = "high"

    return {
        "check_id": "word_count",
        "title": "Resume Length",
        "status": status_value,
        "severity": severity,
        "message": "Keep resume content concise. A strong ATS range is usually 350-1000 words."
    }


def _check_bullets(resume_text: str) -> Dict:
    lines = (resume_text or "").splitlines()
    bullet_lines = [
        line for line in lines
        if re.match(r"^\s*[-•*]\s+", line.strip()) or re.match(r"^\s*\d+\.\s+", line.strip())
    ]
    bullet_count = len(bullet_lines)

    if bullet_count >= 5:
        status_value = "pass"
        severity = "low"
    elif bullet_count >= 2:
        status_value = "warn"
        severity = "medium"
    else:
        status_value = "fail"
        severity = "high"

    return {
        "check_id": "bullets",
        "title": "Bullet Point Clarity",
        "status": status_value,
        "severity": severity,
        "message": "Use bullet points for achievements and responsibilities instead of long paragraphs."
    }


def _check_dates(resume_text: str) -> Dict:
    text = resume_text or ""
    date_hits = re.findall(
        r"(20\d{2}|19\d{2}|present|current|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)",
        text.lower()
    )
    passed = len(date_hits) >= 3

    return {
        "check_id": "dates",
        "title": "Date Consistency",
        "status": "pass" if passed else "warn",
        "severity": "low" if passed else "medium",
        "message": "Add clear start/end dates for roles and projects."
    }


def _check_table_like_content(resume_text: str) -> Dict:
    text = resume_text or ""
    pipe_count = text.count("|")
    tab_count = text.count("\t")
    suspicious = pipe_count >= 8 or tab_count >= 10

    return {
        "check_id": "table_layout",
        "title": "Complex Layout Risk",
        "status": "warn" if suspicious else "pass",
        "severity": "medium" if suspicious else "low",
        "message": "Avoid heavy tables/columns where possible because some ATS parsers struggle with them."
    }


def _check_keyword_alignment(resume_text: str, job_description: str) -> Dict:
    if not job_description.strip():
        return {
            "check_id": "keyword_alignment",
            "title": "Keyword Alignment",
            "status": "warn",
            "severity": "medium",
            "message": "No job description provided for keyword alignment check."
        }

    jd_keywords = extract_top_keywords(job_description, top_n=20)
    resume_clean_words = set(normalize_text(resume_text).split())
    matched_count = 0

    for keyword in jd_keywords:
        parts = keyword.split()
        if all(part in resume_clean_words for part in parts):
            matched_count += 1

    ratio = (matched_count / len(jd_keywords)) if jd_keywords else 0

    if ratio >= 0.6:
        status_value = "pass"
        severity = "low"
    elif ratio >= 0.35:
        status_value = "warn"
        severity = "medium"
    else:
        status_value = "fail"
        severity = "high"

    return {
        "check_id": "keyword_alignment",
        "title": "JD Keyword Coverage",
        "status": status_value,
        "severity": severity,
        "message": "Mirror essential job-description keywords in experience and skills sections."
    }


def build_ats_audit(
    resume_text: str,
    resume_filename: str,
    job_description: str = "",
) -> Dict:
    checks: List[Dict] = [
        _check_file_type(resume_filename),
        _check_contact_details(resume_text),
        _check_standard_sections(resume_text),
        _check_word_count(resume_text),
        _check_bullets(resume_text),
        _check_dates(resume_text),
        _check_table_like_content(resume_text),
        _check_keyword_alignment(resume_text, job_description),
    ]

    score_map = {"pass": 1.0, "warn": 0.55, "fail": 0.0}
    score = round(
        (sum(score_map.get(check["status"], 0) for check in checks) / len(checks)) * 100
    )

    high_impact_fixes = [
        check["message"]
        for check in checks
        if check["status"] in {"fail", "warn"} and check["severity"] in {"high", "medium"}
    ][:6]

    return {
        "score": score,
        "checks": checks,
        "high_impact_fixes": high_impact_fixes,
    }
