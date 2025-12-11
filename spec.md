## Text-Only Interview Coach MVP

- Language: English
- Role focus: SDE intern / junior SDE
- Rounds:
  - Round 1: HR/behavioral
  - Round 2: DSA / CS fundamentals
- Session flow: 10 questions per session
- After each answer: short immediate feedback (scores + bullets + suggested answer)
- End of session: summary + score breakdown
- Storage: JSON on disk (per session)
- APIs: FastAPI
  - POST `/start_session` → `{session_id, first_question}`
  - POST `/answer` → `{evaluation, next_question}`
  - GET `/summary/{session_id}` → consolidated scores/feedback
- LLM: Gemini 2.5 Pro (evaluation prompt only; questions selected from JSON bank)
