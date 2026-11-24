import os
import pdfplumber
from docx import Document


def extract_text(uploaded_file):
    # Support both Streamlit and FastAPI uploaded files
    filename = (
        getattr(uploaded_file, "name", None)
        or getattr(uploaded_file, "filename", "")
    ).lower()

    # FastAPI UploadFile provides the actual file through .file
    file_obj = getattr(uploaded_file, "file", uploaded_file)

    if hasattr(file_obj, "seek"):
        file_obj.seek(0)

    if filename.endswith(".pdf"):
        pages = []

        with pdfplumber.open(file_obj) as pdf:
            for page in pdf.pages:
                pages.append(page.extract_text() or "")

        return "\n".join(pages)

    elif filename.endswith(".docx"):
        doc = Document(file_obj)
        return "\n".join(
            paragraph.text for paragraph in doc.paragraphs
        )

    else:
        raise ValueError(
            "Unsupported file type. Please upload PDF or DOCX."
        )


def extract_candidate_name(text, filename=""):
    for line in [
        x.strip()
        for x in text.splitlines()
        if x.strip()
    ][:8]:

        words = line.split()

        if 2 <= len(words) <= 4 and all(
            word.replace("-", "").replace("'", "").isalpha()
            for word in words
        ):
            if not any(
                keyword in line.lower()
                for keyword in [
                    "resume", "curriculum",
                    "profile", "email"
                ]
            ):
                return line

    return (
        os.path.splitext(filename)[0]
        .replace("_", " ")
        .replace("-", " ")
        .title()
        or "Unknown Candidate"
    )