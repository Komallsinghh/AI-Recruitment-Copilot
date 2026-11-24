# AI Recruitment Copilot — runnable prototype

## Requirements
- Windows 10/11
- Python 3.9 or newer
- VS Code (optional; any editor works)

## Run on Windows PowerShell
Open this folder in VS Code. Open Terminal > New Terminal and run:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

If PowerShell blocks activation, run this once in the current terminal:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

The app opens in your browser, usually at http://localhost:8501.

## How to demonstrate
1. Open Candidate Matching.
2. Enter a job title and paste a job description.
3. Upload one or more text-based PDF/DOCX resumes.
4. Click Analyze and rank candidates.
5. Show the score, matched skills, missing skills, explanation, chart and CSV export.
6. Open Candidate Database and search candidates by skill.

## Matching formula
Final score = (70% × detected required-skill coverage) + (30% × TF-IDF cosine similarity).

Skill coverage = number of required skills detected in the resume / number of required skills detected in the job description.

## Important limitations
- This is a one-day academic prototype, not a production hiring platform.
- Skill extraction uses a small predefined vocabulary.
- TF-IDF is a traditional NLP text-similarity technique, not a transformer embedding model.
- Scanned/image-only PDFs are not OCR processed.
- The score is decision support only and must not be used as an automatic hiring decision.
- SQLite is used as a lightweight local prototype database instead of MySQL/PostgreSQL.
