import re

SKILLS = [
    "python", "java", "c++", "c", "sql", "mysql", "postgresql", "mongodb",
    "html", "css", "javascript", "react", "node.js", "flask", "django",
    "fastapi", "streamlit", "machine learning", "deep learning", "nlp",
    "data analysis", "pandas", "numpy", "scikit-learn", "tensorflow",
    "pytorch", "git", "github", "excel", "power bi", "tableau",
    "communication", "teamwork", "problem solving", "leadership",
    "data structures", "algorithms", "operating systems", "computer networks"
]

def extract_skills(text):
    text_lower = text.lower()
    found = []
    for skill in SKILLS:
        pattern = r"(?<![a-z0-9])" + re.escape(skill.lower()) + r"(?![a-z0-9])"
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(set(found))
