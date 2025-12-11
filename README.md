# Interview Coach (Text-Only MVP)

AI-powered mock interview coach for SDE interns/juniors. The FastAPI backend serves curated interview questions, scores your answers with Gemini, and returns coaching notes and a suggested improved answer. A lightweight HTML frontend drives the flow.

## Highlights
- 10-question sessions spanning behavioral + DSA/CS fundamentals.
- Per-answer scoring (relevance, structure, depth, communication) with bullet feedback.
- Suggested improved answer after every submission.
- JSON-backed persistence for sessions and question bank (no database needed).
- Simple frontend that talks to the API at `http://localhost:8000`.

## Project Structure
- `backend/` – FastAPI app (`main.py`) and Python deps (`requirements.txt`).
- `frontend/` – Single-page HTML/CSS/JS client (`index.html`).
- `data/` – `questions.json` (question bank) and `sessions.json` (saved sessions).
- `spec.md` – Original product spec for the MVP.

## Prerequisites
- Python 3.10+ recommended.
- Gemini API key with access to `gemini-1.5-pro` (or another configured model).
- Node is **not** required; the frontend is plain HTML + fetch.

## Setup
1) Clone the repo and move into it:
```bash
git clone https://github.com/avii2/Chatbot.git
cd Chatbot
```
2) Create and activate a virtual environment (optional but recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
```
3) Install backend dependencies:
```bash
pip install -r backend/requirements.txt
```
4) Provide your Gemini key (required for scoring):
```bash
export GEMINI_API_KEY="your-key-here"
# Optional: override the model (defaults to gemini-1.5-pro)
export GEMINI_MODEL="gemini-1.5-pro"
```

## Run the backend
```bash
uvicorn backend.main:app --reload --port 8000
```

## Run the frontend
Open `frontend/index.html` directly in the browser, or serve it from the repo root:
```bash
python -m http.server 8080
```
Then visit http://localhost:8080/frontend/index.html (frontend expects the API at `http://localhost:8000` by default).

## API quick tour
- `POST /start_session` → body: `{user_name, job_role, interview_type}` → returns `{session_id, question}`.
- `POST /answer` → body: `{session_id, question_id, user_answer_text}` → returns `{evaluation, next_question}`.
- `GET /summary/{session_id}` → returns averages, answers, and metadata for the session.

If Gemini fails (e.g., no key), the backend returns fallback neutral scores with guidance to set `GEMINI_API_KEY`.

## Data & persistence
- Question bank lives in `data/questions.json`; edit or expand to customize roles/categories.
- Sessions are stored in `data/sessions.json` so runs are stateful without a database.

## Development notes
- CORS is open (`allow_origins=["*"]`) for local testing.
- Scoring criteria are defined in `backend/main.py` under `evaluate_answer`.
- The frontend uses fetch against `API_BASE = "http://localhost:8000"`; change this constant if you deploy elsewhere.

## Troubleshooting
- `Missing GEMINI_API_KEY` → ensure the env var is set before starting uvicorn.
- Network errors from frontend → confirm backend is running on port 8000 and CORS remains open.
- Non-JSON LLM output → the backend raises HTTP 500; check Gemini key/model and logs.

## License
Not specified in this repo. Add your preferred license before publishing.
