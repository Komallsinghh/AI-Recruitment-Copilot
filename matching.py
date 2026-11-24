import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


STOPWORDS = {
    "the", "and", "for", "with", "you", "your", "are",
    "will", "have", "has", "this", "that", "from", "our",
    "job", "role", "work", "working", "candidate", "required",
    "looking", "seeking", "experience", "skills", "ability",
    "years", "year", "using", "knowledge"
}

EDUCATION_KEYWORDS = [
    "b.tech", "bachelor", "b.e.", "b.sc", "bca",
    "m.tech", "master", "mca", "m.sc", "degree",
    "computer science", "engineering", "diploma"
]

EXPERIENCE_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*\+?\s*years?",
    re.IGNORECASE
)

RESUME_SECTIONS = [
    "education",
    "experience",
    "skills",
    "projects",
    "certifications"
]


def extract_keywords(text):
    words = re.findall(
        r"[a-zA-Z][a-zA-Z0-9+#.]*",
        text.lower()
    )

    return sorted({
        word for word in words
        if len(word) > 2 and word not in STOPWORDS
    })


def calculate_education_score(resume_text, job_text):
    resume = resume_text.lower()
    job = job_text.lower()

    required = [
        word for word in EDUCATION_KEYWORDS
        if word in job
    ]

    if not required:
        return 100.0

    matched = [
        word for word in required
        if word in resume
    ]

    return round(len(matched) / len(required) * 100, 2)


def calculate_experience_score(resume_text, job_text):
    resume = resume_text.lower()
    job = job_text.lower()

    job_years = EXPERIENCE_PATTERN.findall(job)
    resume_years = EXPERIENCE_PATTERN.findall(resume)

    if not job_years:
        return 100.0

    required_years = float(job_years[0])

    if not resume_years:
        return 0.0

    candidate_years = max(
        float(x) for x in resume_years
    )

    if required_years <= 0:
        return 100.0

    return round(
        min(candidate_years / required_years, 1) * 100,
        2
    )


def calculate_structure_score(resume_text):
    resume = resume_text.lower()

    found_sections = [
        section for section in RESUME_SECTIONS
        if section in resume
    ]

    return round(
        len(found_sections) / len(RESUME_SECTIONS) * 100,
        2
    )


def calculate_match(
    resume_text,
    job_text,
    candidate_skills,
    job_skills
):
    resume_text = resume_text or ""
    job_text = job_text or ""

    candidate_skills = {
        str(skill).lower()
        for skill in (candidate_skills or [])
    }

    job_skills = {
        str(skill).lower()
        for skill in (job_skills or [])
    }

    # 1. Skills Matching - 35%
    matched = sorted(candidate_skills & job_skills)
    missing = sorted(job_skills - candidate_skills)

    if job_skills:
        skill_score = (
            len(matched) / len(job_skills) * 100
        )
    else:
        skill_score = 0.0

    # 2. Keyword Matching - 25%
    job_keywords = set(extract_keywords(job_text))
    resume_keywords = set(extract_keywords(resume_text))

    matched_keywords = sorted(
        job_keywords & resume_keywords
    )

    missing_keywords = sorted(
        job_keywords - resume_keywords
    )

    if job_keywords:
        keyword_score = (
            len(matched_keywords) / len(job_keywords) * 100
        )
    else:
        keyword_score = 0.0

    # 3. Education Matching - 15%
    education_score = calculate_education_score(
        resume_text, job_text
    )

    # 4. Experience Matching - 15%
    experience_score = calculate_experience_score(
        resume_text, job_text
    )

    # 5. Resume Structure - 10%
    structure_score = calculate_structure_score(
        resume_text
    )

    # ATS Compatibility Score
    ats_score = round(
        0.35 * skill_score
        + 0.25 * keyword_score
        + 0.15 * education_score
        + 0.15 * experience_score
        + 0.10 * structure_score,
        2
    )

    # TF-IDF Similarity
    try:
        vectors = TfidfVectorizer(
            stop_words="english"
        ).fit_transform([
            resume_text,
            job_text
        ])

        similarity = float(
            cosine_similarity(
                vectors[0:1],
                vectors[1:2]
            )[0][0]
        )

    except ValueError:
        similarity = 0.0

    # Existing Job Match Score
    match_score = round(
        0.70 * skill_score
        + 0.30 * similarity * 100,
        2
    )

    # Improvement Suggestions
    suggestions = []

    if missing:
        suggestions.append(
            "Review relevant missing skills: "
            + ", ".join(missing)
        )

    if missing_keywords:
        suggestions.append(
            "Review missing job keywords and include "
            "only relevant ones."
        )

    if education_score < 100:
        suggestions.append(
            "Review the education requirements."
        )

    if experience_score < 100:
        suggestions.append(
            "Review the experience requirements."
        )

    if structure_score < 100:
        suggestions.append(
            "Improve resume structure with clear sections."
        )

    if not suggestions:
        suggestions.append(
            "Your resume covers the evaluated criteria well."
        )

    explanation = (
        f"{len(matched)} of {len(job_skills)} required "
        f"skills matched. ATS Compatibility Score: "
        f"{ats_score}/100."
    )

    return {
        "score": match_score,
        "ats_score": ats_score,
        "matched": matched,
        "missing": missing,
        "similarity": round(similarity * 100, 2),
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "breakdown": {
            "skills": round(skill_score, 2),
            "keywords": round(keyword_score, 2),
            "education": education_score,
            "experience": experience_score,
            "structure": structure_score
        },
        "suggestions": suggestions,
        "explanation": explanation
    }