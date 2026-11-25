import streamlit as st
import pandas as pd
import os
import io
from resume_parser import extract_text, extract_candidate_name
from job_analyzer import extract_skills
from matching import calculate_match
from database import init_db, save_candidate, save_job, save_match, get_candidates

st.set_page_config(page_title="AI Recruitment Copilot", page_icon="🤝", layout="wide")
init_db()

st.title("🤝 AI Recruitment Copilot")
st.caption("A recruiter decision-support prototype: parse resumes, analyze job requirements, and compare candidates.")
st.info("This prototype provides explainable matching assistance. It does not make hiring decisions.")

tab1, tab2, tab3 = st.tabs(["Candidate Matching", "Candidate Database", "About"])

with tab1:
    st.subheader("1. Enter the job description")
    job_title = st.text_input("Job title", value="Python Developer")
    job_description = st.text_area(
        "Paste job description",
        value="We are looking for a Python developer with SQL, data analysis, communication and problem solving skills. Knowledge of machine learning and pandas is preferred.",
        height=160
    )
    job_skills = extract_skills(job_description)
    st.write("**Skills detected in job description:**", ", ".join(job_skills) if job_skills else "No known skills detected. Add skill names to the description.")

    st.subheader("2. Upload candidate resumes")
    uploaded_files = st.file_uploader("Upload PDF or DOCX resumes", type=["pdf", "docx"], accept_multiple_files=True)
    demo_mode = st.button("🚀 Run Demo with 10 Sample Resumes")

    if demo_mode:
        sample_folder = os.path.join(os.path.dirname(__file__), "sample_resumes")
        uploaded_files = []

        if os.path.exists(sample_folder):
            for filename in sorted(os.listdir(sample_folder)):
                if filename.startswith("Candidate") and filename.lower().endswith((".pdf", ".docx")):
                    file_path = os.path.join(sample_folder, filename)

                    with open(file_path, "rb") as file:
                        sample_file = io.BytesIO(file.read())
                        sample_file.name = filename
                        uploaded_files.append(sample_file)

            st.success(f"{len(uploaded_files)} demo resumes loaded successfully!")
        else:
            st.error("Sample resumes folder not found.")

    if st.button("Analyze and rank candidates", type="primary") or demo_mode:
        if not job_description.strip():
            st.error("Please enter a job description.")
        elif not uploaded_files:
            st.error("Please upload at least one PDF or DOCX resume.")
        else:
            save_job(job_title, job_description, job_skills)
            results = []
            for uploaded in uploaded_files:
                try:
                    raw_text = extract_text(uploaded)
                    if not raw_text.strip():
                        st.warning(f"No readable text found in {uploaded.name}. It may be a scanned PDF.")
                        continue
                    name = extract_candidate_name(raw_text, uploaded.name)
                    candidate_skills = extract_skills(raw_text)
                    result = calculate_match(raw_text, job_description, candidate_skills, job_skills)
                    save_candidate(name, uploaded.name, raw_text, candidate_skills)
                    save_match(name, job_title, result)
                    results.append({
    "Candidate": name,
    "Resume": uploaded.name,

    "ATS Score": result["ats_score"],
    "Match Score": result["score"],

    "Skills Score": result["breakdown"]["skills"],
    "Keyword Score": result["breakdown"]["keywords"],
    "Education Score": result["breakdown"]["education"],
    "Experience Score": result["breakdown"]["experience"],
    "Structure Score": result["breakdown"]["structure"],

    "Matched Skills": ", ".join(result["matched"]),
    "Missing Skills": ", ".join(result["missing"]),

    "Matched Keywords": ", ".join(result["matched_keywords"]),
    "Missing Keywords": ", ".join(result["missing_keywords"]),

    "Suggestions": " | ".join(result["suggestions"]),
    "Explanation": result["explanation"]
})
                except Exception as e:
                    st.error(f"Could not process {uploaded.name}: {e}")
            if results:
                df = pd.DataFrame(results).sort_values(
                    "ATS Score", ascending=False
                )

                st.success(f"Analysis complete. Processed {len(df)} resume(s).")

                st.dataframe(df, use_container_width=True, hide_index=True)

                st.bar_chart(df.set_index("Candidate")["ATS Score"])

                for row in df.to_dict("records"):
                    with st.expander(
                        f'{row["Candidate"]} — ATS Score: {row["ATS Score"]}%'
                    ):
                        st.subheader("ATS Compatibility Analysis")

                        col1, col2 = st.columns(2)

                        col1.metric("ATS Score", f'{row["ATS Score"]}%')
                        col2.metric("Job Match Score", f'{row["Match Score"]}%')

                        st.subheader("Score Breakdown")

                        score_columns = st.columns(5)

                        metrics = [
                            ("Skills", "Skills Score"),
                            ("Keywords", "Keyword Score"),
                            ("Education", "Education Score"),
                            ("Experience", "Experience Score"),
                            ("Structure", "Structure Score")
                        ]

                        for col, (label, key) in zip(score_columns, metrics):
                            col.metric(label, f'{row[key]}%')

                        st.subheader("Skills Analysis")
                        st.write("Matched Skills:", row["Matched Skills"] or "None")
                        st.write("Missing Skills:", row["Missing Skills"] or "None")

                        st.subheader("Keyword Analysis")
                        st.write("Matched Keywords:", row["Matched Keywords"] or "None")
                        st.write("Missing Keywords:", row["Missing Keywords"] or "None")

                        st.subheader("Resume Improvement Suggestions")
                        st.info(row["Suggestions"])

                        st.caption(row["Explanation"])

                st.download_button(
                    "Download results as CSV",
                    df.to_csv(index=False).encode("utf-8"),
                    "recruitment_results.csv",
                    "text/csv"
                )

            else:
                st.warning("No readable resumes were processed.")
with tab2:
    st.subheader("Saved candidate profiles")
    rows = get_candidates()
    if rows:
        db_df = pd.DataFrame(rows, columns=["Name", "Resume file", "Skills", "Added at"])
        st.dataframe(db_df, use_container_width=True, hide_index=True)
        query = st.text_input("Search candidates by skill (example: Python)")
        if query:
            filtered = db_df[db_df["Skills"].str.contains(query, case=False, na=False)]
            st.write(f"Found {len(filtered)} candidate(s).")
            st.dataframe(filtered, use_container_width=True, hide_index=True)
    else:
        st.write("No candidates saved yet. Analyze resumes in the Candidate Matching tab.")

with tab3:
    st.subheader("Project overview")
    st.markdown("""
    **Main modules**
    - Resume parsing: extracts text from PDF and DOCX files.
    - Candidate profile: detects a name and a set of known skills.
    - Job description analysis: detects required skills from the job text.
    - Matching engine: combines skill coverage and TF-IDF text similarity.
    - Database: stores candidate profiles, job descriptions and match results in SQLite.

    **Technology:** Python, Streamlit, pdfplumber, python-docx, scikit-learn, pandas and SQLite.

    **Prototype limitation:** skill detection uses a predefined vocabulary and may miss synonyms or skills outside that list. Scanned PDFs need OCR, which is not included. Always verify extracted information manually.
    """)
