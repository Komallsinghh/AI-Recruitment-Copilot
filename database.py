import sqlite3
from datetime import datetime

DB_NAME = "recruitment.db"

def connect():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    with connect() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, resume_file TEXT, resume_text TEXT, skills TEXT, created_at TEXT
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, description TEXT, skills TEXT, created_at TEXT
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS match_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_name TEXT, job_title TEXT, score REAL,
            matched_skills TEXT, missing_skills TEXT, explanation TEXT, created_at TEXT
        )""")

def save_candidate(name, filename, text, skills):
    with connect() as con:
        con.execute("INSERT INTO candidates(name,resume_file,resume_text,skills,created_at) VALUES(?,?,?,?,?)",
                    (name, filename, text, ", ".join(skills), datetime.now().isoformat(timespec="seconds")))

def save_job(title, description, skills):
    with connect() as con:
        con.execute("INSERT INTO jobs(title,description,skills,created_at) VALUES(?,?,?,?)",
                    (title, description, ", ".join(skills), datetime.now().isoformat(timespec="seconds")))

def save_match(name, title, result):
    with connect() as con:
        con.execute("""INSERT INTO match_results(candidate_name,job_title,score,matched_skills,missing_skills,explanation,created_at)
                    VALUES(?,?,?,?,?,?,?)""",
                    (name, title, result["score"], ", ".join(result["matched"]),
                     ", ".join(result["missing"]), result["explanation"],
                     datetime.now().isoformat(timespec="seconds")))

def get_candidates():
    with connect() as con:
        return con.execute("SELECT name,resume_file,skills,created_at FROM candidates ORDER BY id DESC").fetchall()
