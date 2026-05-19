import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


SKILLS_FILE = Path(__file__).resolve().parent.parent / "data" / "skills_taxonomy.json"


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#.\s/-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def load_skills_taxonomy() -> List[str]:
    with open(SKILLS_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    skills = []

    for category_skills in data.values():
        skills.extend(category_skills)

    return list(set([skill.lower() for skill in skills]))


def extract_top_keywords(text: str, top_n: int = 25) -> List[str]:
    cleaned_text = normalize_text(text)

    if not cleaned_text:
        return []

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=100
    )

    tfidf_matrix = vectorizer.fit_transform([cleaned_text])
    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.toarray()[0]

    keyword_scores = list(zip(feature_names, scores))
    keyword_scores = sorted(keyword_scores, key=lambda x: x[1], reverse=True)

    keywords = [keyword for keyword, score in keyword_scores[:top_n]]

    return keywords


def calculate_keyword_score(
    jd_text: str,
    resume_text: str
) -> Tuple[int, List[str], List[str]]:
    jd_clean = normalize_text(jd_text)
    resume_clean = normalize_text(resume_text)

    if not jd_clean or not resume_clean:
        return 0, [], []

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=300
    )

    vectors = vectorizer.fit_transform([jd_clean, resume_clean])
    similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

    keyword_score = round(similarity * 100)

    jd_keywords = extract_top_keywords(jd_text, top_n=30)

    matched_keywords = []
    missing_keywords = []

    resume_words = set(resume_clean.split())

    for keyword in jd_keywords:
        keyword_parts = keyword.split()

        if all(part in resume_words for part in keyword_parts):
            matched_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)

    return keyword_score, matched_keywords[:15], missing_keywords[:15]


def extract_skills(text: str) -> List[str]:
    cleaned_text = normalize_text(text)
    taxonomy = load_skills_taxonomy()

    found_skills = []

    for skill in taxonomy:
        skill_pattern = re.escape(skill.lower())
        pattern = r"(?<!\w)" + skill_pattern + r"(?!\w)"

        if re.search(pattern, cleaned_text):
            found_skills.append(skill)

    return sorted(list(set(found_skills)))


def calculate_skills_score(
    jd_text: str,
    resume_text: str
) -> Tuple[int, List[str], List[str]]:
    jd_skills = set(extract_skills(jd_text))
    resume_skills = set(extract_skills(resume_text))

    if not jd_skills:
        return 100, [], []

    matched_skills = sorted(list(jd_skills.intersection(resume_skills)))
    missing_skills = sorted(list(jd_skills.difference(resume_skills)))

    skills_score = round((len(matched_skills) / len(jd_skills)) * 100)

    return skills_score, matched_skills, missing_skills


def extract_required_years(jd_text: str) -> int:
    text = normalize_text(jd_text)

    patterns = [
        r"(\d+)\+?\s*years",
        r"(\d+)\+?\s*yrs",
        r"minimum\s*(\d+)",
        r"at least\s*(\d+)"
    ]

    years = []

    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                years.append(int(match))
            except ValueError:
                pass

    if not years:
        return 0

    return max(years)


def extract_resume_years(resume_text: str) -> int:
    text = resume_text.lower()

    date_ranges = re.findall(
        r"(20\d{2}|19\d{2})\s*[-–]\s*(20\d{2}|present|current)",
        text
    )

    total_years = 0

    for start, end in date_ranges:
        start_year = int(start)

        if end in ["present", "current"]:
            end_year = 2026
        else:
            end_year = int(end)

        if end_year >= start_year:
            total_years += end_year - start_year

    explicit_years = re.findall(r"(\d+)\+?\s*years?\s*(of)?\s*experience", text)

    for item in explicit_years:
        try:
            total_years = max(total_years, int(item[0]))
        except ValueError:
            pass

    return total_years


def calculate_experience_score(jd_text: str, resume_text: str) -> int:
    required_years = extract_required_years(jd_text)
    resume_years = extract_resume_years(resume_text)

    if required_years == 0:
        return 100

    if resume_years >= required_years:
        return 100

    return round((resume_years / required_years) * 100)


def calculate_format_score(resume_text: str) -> int:
    text = resume_text.lower()

    score = 0

    standard_sections = [
        "skills",
        "experience",
        "education",
        "summary"
    ]

    for section in standard_sections:
        if section in text:
            score += 15

    word_count = len(text.split())

    if 400 <= word_count <= 900:
        score += 25
    elif 250 <= word_count < 400 or 900 < word_count <= 1200:
        score += 15
    else:
        score += 5

    date_patterns = re.findall(
        r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|\d{2}/\d{4}|20\d{2})",
        text
    )

    if len(date_patterns) >= 2:
        score += 15

    return min(score, 100)


def calculate_overall_score(
    keyword_score: int,
    skills_score: int,
    experience_score: int,
    format_score: int
) -> int:
    overall = (
        keyword_score * 0.35 +
        skills_score * 0.30 +
        experience_score * 0.20 +
        format_score * 0.15
    )

    return round(overall)


def run_resume_scoring(jd_text: str, resume_text: str) -> Dict:
    keyword_score, matched_keywords, missing_keywords = calculate_keyword_score(
        jd_text,
        resume_text
    )

    skills_score, matched_skills, missing_skills = calculate_skills_score(
        jd_text,
        resume_text
    )

    experience_score = calculate_experience_score(jd_text, resume_text)
    format_score = calculate_format_score(resume_text)

    overall_score = calculate_overall_score(
        keyword_score,
        skills_score,
        experience_score,
        format_score
    )

    return {
        "overall_score": overall_score,
        "keyword_score": keyword_score,
        "skills_score": skills_score,
        "experience_score": experience_score,
        "format_score": format_score,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }