from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import shutil, os
from parser import extract_text
from ollama_client import score_resume

app = FastAPI()

# Robust CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 1. ADD THIS: Serves your index.html directly from the backend
@app.get("/")
async def read_root():
    return {"status": "Backend is running smoothly!", "endpoint": "/screen"}

@app.post("/screen")
async def screen_resumes(
    jd: str = Form(...),
    resumes: list[UploadFile] = File(...)
):
    results = []

    for resume_file in resumes:
        path = os.path.join(UPLOAD_DIR, resume_file.filename)
        try:
            with open(path, "wb") as f:
                shutil.copyfileobj(resume_file.file, f)

            text = extract_text(path)
            if not text or not text.strip():
                 raise ValueError("No extractable text found in the file (empty or unsupported format)")

            evaluation = score_resume(jd, text)

            # Ensure correct formatting and keys exist
            results.append({
                "filename": resume_file.filename,
                "score": int(evaluation.get("score", 0)),
                "matched_skills": evaluation.get("matched_skills", []),
                "missing_skills": evaluation.get("missing_skills", []),
                "summary": evaluation.get("summary", "No evaluation summary generated."),
                "verdict": evaluation.get("verdict", "Unknown Match")
            })
        except Exception as e:
            results.append({
                "filename": resume_file.filename,
                "score": 0,
                "matched_skills": [],
                "missing_skills": [],
                "summary": f"Failed to process this resume: {e}",
                "verdict": "Error"
            })
        finally:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass

    results.sort(key=lambda x: x.get("score", 0), reverse=True)
    return {"results": results}
