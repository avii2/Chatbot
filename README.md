# Interview Coach (Text-Only MVP)

Practice interviews without the awkwardness. This FastAPI + Gemini-powered coach walks you through 10 curated questions, scores every answer, and shows you how to respond better next time. A single HTML page drives the flow—no build tools, just open and go.

## What you get
- 10-question sessions across behavioral and DSA/CS fundamentals.
- Instant scoring on relevance, structure, depth, and communication.
- Bulleted feedback plus a short, improved sample answer.
- JSON storage for questions and sessions—no database to set up.
- Friendly one-page frontend that talks to `http://localhost:8000`.

## Repo tour
- `backend/` – FastAPI app (`main.py`) and Python deps (`requirements.txt`).
- `frontend/` – Single-page HTML/CSS/JS client (`index.html`).
- `data/` – `questions.json` (question bank) and `sessions.json` (session store).
- `spec.md` – Original MVP spec and scope.

## Prereqs
- Python 3.10+ recommended.
- Gemini API key with access to `gemini-1.5-pro` (or another configured model).
- No Node build needed; the frontend uses plain fetch.

## Quick start
1) Clone and enter the repo
```bash
git clone https://github.com/avii2/Chatbot.git
cd Chatbot
```
2) (Optional) Create a virtualenv
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
```
3) Install backend deps
```bash
pip install -r backend/requirements.txt
```
4) Set your Gemini key (required)
```bash
export GEMINI_API_KEY="your-key-here"
# Optional: override the model
export GEMINI_MODEL="gemini-1.5-pro"
```

## Run it
- Backend
```bash
uvicorn backend.main:app --reload --port 8000
```
- Frontend: open `frontend/index.html` directly, or serve the repo root:
```bash
python -m http.server 8080
```
Then visit http://localhost:8080/frontend/index.html (expects the API at `http://localhost:8000`).

## API at a glance
- `POST /start_session` — `{user_name, job_role, interview_type}` → `{session_id, question}`
- `POST /answer` — `{session_id, question_id, user_answer_text}` → `{evaluation, next_question}`
- `GET /summary/{session_id}` — aggregates scores and answers for the session

If Gemini is unavailable, the backend returns neutral fallback scores and a reminder to set `GEMINI_API_KEY`.

## Customize and extend
- Add or tweak questions in `data/questions.json`.
- Update scoring criteria in `backend/main.py` (`evaluate_answer`).
- Point the frontend to a different API host by changing `API_BASE` in `frontend/index.html`.

## Troubleshooting
- `Missing GEMINI_API_KEY` → export the key before running uvicorn.
- Frontend cannot reach API → ensure backend runs on port 8000; CORS is open.
- LLM returns non-JSON → check the Gemini key/model and backend logs; the API responds 500 in that case.

## License
Not specified in this repo. Add your preferred license before publishing.
