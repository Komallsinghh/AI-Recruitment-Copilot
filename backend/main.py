from fastapi import FastAPI
from typing import Annotated
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Recruitment Copilot API",
    description="AI-powered resume screening and candidate matching system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "AI Recruitment Copilot Backend is Running!",
        "status": "success"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile, File, HTTPException, Form
import shutil
from resume_parser import extract_text, extract_candidate_name
from job_analyzer import extract_skills
from matching import calculate_match

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/upload-resumes")
async def upload_resumes(file: UploadFile = File(...)):
    files = [file]

    allowed_extensions = {".pdf", ".docx"}
    uploaded_files = []

    for file in files:
        extension = Path(file.filename).suffix.lower()

        if extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file: {file.filename}"
            )

        safe_name = f"{uuid4().hex}{extension}"
        file_path = UPLOAD_DIR / safe_name

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        uploaded_files.append({
            "original_name": file.filename,
            "saved_name": safe_name,
            "status": "uploaded"
        })

    return {
        "message": "Resumes uploaded successfully",
        "total_uploaded": len(uploaded_files),
        "files": uploaded_files
    }

@app.post("/analyze-resume")
async def analyze_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    extension = Path(file.filename).suffix.lower()

    if extension not in {".pdf", ".docx"}:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported."
        )

    try:
        resume_text = extract_text(file)
        
        if not resume_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from resume."
            )

        candidate_name = extract_candidate_name(
            resume_text,
            file.filename
        )

        candidate_skills = extract_skills(resume_text)
        job_skills = extract_skills(job_description)

        result = calculate_match(
            resume_text,
            job_description,
            candidate_skills,
            job_skills
        )

        return {
            "candidate_name": candidate_name,
            "filename": file.filename,
            "ats_score": result["ats_score"],
            "match_score": result["score"],
            "matched_skills": result["matched"],
            "missing_skills": result["missing"],
            "suggestions": result["suggestions"],
            "score_breakdown": result["breakdown"],
            "explanation": result["explanation"]
        }

    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
@app.post("/rank-candidates")
async def rank_candidates(
    files: Annotated[list[UploadFile], File()],
    job_description: Annotated[str, Form()]
):
    if not files:
        raise HTTPException(
            status_code=400,
            detail="Please upload at least one resume."
        )

    if len(files) > 30:
        raise HTTPException(
            status_code=400,
            detail="Maximum 30 resumes can be uploaded at once."
        )

    rankings = []
    errors = []

    for file in files:
        try:
            extension = Path(file.filename).suffix.lower()

            if extension not in {".pdf", ".docx"}:
                errors.append({
                    "filename": file.filename,
                    "error": "Unsupported file type"
                })
                continue

            resume_text = extract_text(file)

            if not resume_text.strip():
                errors.append({
                    "filename": file.filename,
                    "error": "Could not extract resume text"
                })
                continue

            candidate_name = extract_candidate_name(
                resume_text,
                file.filename
            )

            candidate_skills = extract_skills(resume_text)
            job_skills = extract_skills(job_description)

            result = calculate_match(
                resume_text,
                job_description,
                candidate_skills,
                job_skills
            )

            rankings.append({
                "candidate_name": candidate_name,
                "filename": file.filename,
                "match_score": result["score"],
                "ats_score": result["ats_score"],
                "matched_skills": result["matched"],
                "missing_skills": result["missing"],
                "suggestions": result["suggestions"],
                "explanation": result["explanation"]
            })

        except Exception as error:
            errors.append({
                "filename": file.filename,
                "error": str(error)
            })

    rankings.sort(
        key=lambda candidate: candidate["match_score"],
        reverse=True
    )

    for position, candidate in enumerate(rankings, start=1):
        candidate["rank"] = position

    return {
        "message": "Candidate ranking completed",
        "total_processed": len(rankings),
        "total_failed": len(errors),
        "rankings": rankings,
        "errors": errors
    }