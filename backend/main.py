import json
import os
import random
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
QUESTION_BANK_PATH = DATA_DIR / "questions.json"
SESSIONS_PATH = DATA_DIR / "sessions.json"

DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-pro")


load_dotenv()


class StartSessionRequest(BaseModel):
    job_role: str = Field(..., example="SDE Intern")
    interview_type: str = Field(..., example="behavioral")
    user_name: str = Field(..., example="Alex")


class AnswerRequest(BaseModel):
    session_id: str
    question_id: str
    user_answer_text: str


def ensure_data_files() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not QUESTION_BANK_PATH.exists():
        raise FileNotFoundError(f"Question bank not found at {QUESTION_BANK_PATH}")
    if not SESSIONS_PATH.exists():
        SESSIONS_PATH.write_text("{}", encoding="utf-8")


def load_sessions() -> Dict[str, Any]:
    ensure_data_files()
    with open(SESSIONS_PATH, "r", encoding="utf-8") as f:
        content = f.read().strip()
        return json.loads(content) if content else {}


def save_sessions(sessions: Dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(SESSIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(sessions, f, indent=2)


def load_question_bank() -> List[Dict[str, Any]]:
    ensure_data_files()
    with open(QUESTION_BANK_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def pick_questions(bank: List[Dict[str, Any]], total: int = 10) -> List[Dict[str, Any]]:
    shuffled = bank[:]
    random.shuffle(shuffled)
    return shuffled[:total]


def configure_gemini() -> None:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Missing GEMINI_API_KEY environment variable")
    genai.configure(api_key=api_key)


def extract_json_block(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    return cleaned.strip()


def evaluate_answer(
    question: Dict[str, Any], user_answer: str, job_role: str
) -> Dict[str, Any]:
    configure_gemini()
    model = genai.GenerativeModel(DEFAULT_MODEL)

    criteria = [
        "Relevance & completeness vs the question",
        "Structure & clarity (organized, concise, logical flow)",
        "Technical depth (for technical questions; for behavioral focus on specifics and impact)",
        "Communication (tone, avoidance of filler, confidence)",
    ]

    prompt = f"""
You are an interview coach evaluating a candidate for the role: {job_role}.

Question:
{question['question']}

Category: {question['category']}
Difficulty: {question['difficulty']}
Sample good points to look for:
{json.dumps(question.get('sample_good_points', []), indent=2)}

Candidate answer:
{user_answer}

Scoring rubric (1-5, integers):
- relevance: Addresses the question and key points.
- structure: Clear organization, concise delivery, logical flow.
- depth: Technical depth for technical questions; specificity/impact for behavioral.
- communication: Clarity of language, avoids filler, confident tone.

Return ONLY valid JSON in this exact shape. No extra text.
{{
  "scores": {{
    "relevance": 1-5,
    "structure": 1-5,
    "depth": 1-5,
    "communication": 1-5
  }},
  "feedback": [
    "Bullet on what to improve or what went well"
  ],
  "suggested_answer": "A short, improved answer (2-5 sentences)"
}}
"""

    response = model.generate_content(prompt)
    text = response.text if hasattr(response, "text") else str(response)
    cleaned = extract_json_block(text)
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="LLM returned non-JSON output")
    return parsed


app = FastAPI(title="Interview Coach API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/start_session")
def start_session(payload: StartSessionRequest = Body(...)) -> Dict[str, Any]:
    sessions = load_sessions()
    bank = load_question_bank()
    questions = pick_questions(bank, total=10)

    session_id = str(uuid.uuid4())
    session = {
        "session_id": session_id,
        "user_name": payload.user_name,
        "job_role": payload.job_role,
        "interview_type": payload.interview_type,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "questions": questions,
        "current_index": 0,
        "answers": [],
    }

    sessions[session_id] = session
    save_sessions(sessions)

    first_question = questions[0] if questions else None
    return {"session_id": session_id, "question": first_question}


@app.post("/answer")
def answer(payload: AnswerRequest = Body(...)) -> Dict[str, Any]:
    sessions = load_sessions()
    session = sessions.get(payload.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    idx = session.get("current_index", 0)
    questions = session.get("questions", [])
    if idx >= len(questions):
        raise HTTPException(status_code=400, detail="Session already completed")

    current_question = questions[idx]
    if current_question["id"] != payload.question_id:
        raise HTTPException(status_code=400, detail="Question does not match the session state")

    try:
        evaluation = evaluate_answer(
            question=current_question,
            user_answer=payload.user_answer_text,
            job_role=session.get("job_role", "SDE Intern"),
        )
    except HTTPException:
        # Bubble up known HTTP errors (e.g., missing GEMINI_API_KEY)
        raise
    except Exception:
        # Fallback evaluation so the route still responds even if LLM fails.
        evaluation = {
            "scores": {
                "relevance": 3,
                "structure": 3,
                "depth": 3,
                "communication": 3,
            },
            "feedback": [
                "LLM evaluation failed; returning default scores.",
                "Ensure GEMINI_API_KEY is set and backend can reach Gemini.",
            ],
            "suggested_answer": "Provide a clear, concise, and structured answer covering the key points.",
        }

    session["answers"].append(
        {
            "question_id": payload.question_id,
            "question": current_question["question"],
            "user_answer": payload.user_answer_text,
            "evaluation": evaluation,
        }
    )
    session["current_index"] = idx + 1

    next_question: Optional[Dict[str, Any]] = None
    if session["current_index"] < len(questions):
        next_question = questions[session["current_index"]]

    sessions[payload.session_id] = session
    save_sessions(sessions)

    return {"evaluation": evaluation, "next_question": next_question}


@app.get("/summary/{session_id}")
def summary(session_id: str) -> Dict[str, Any]:
    sessions = load_sessions()
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    answers = session.get("answers", [])
    score_totals: Dict[str, List[int]] = {
        "relevance": [],
        "structure": [],
        "depth": [],
        "communication": [],
    }

    for item in answers:
        scores = item.get("evaluation", {}).get("scores", {})
        for key in score_totals:
            val = scores.get(key)
            if isinstance(val, (int, float)):
                score_totals[key].append(val)

    averages = {
        key: (sum(vals) / len(vals)) if vals else None for key, vals in score_totals.items()
    }

    return {
        "session_id": session_id,
        "user_name": session.get("user_name"),
        "job_role": session.get("job_role"),
        "interview_type": session.get("interview_type"),
        "created_at": session.get("created_at"),
        "total_questions": len(session.get("questions", [])),
        "answered": len(answers),
        "scores_average": averages,
        "answers": answers,
    }
