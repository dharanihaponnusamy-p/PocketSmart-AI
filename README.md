# PocketSmart AI — Complete FastAPI Project

This implementation follows the supplied documentation's later FastAPI milestones. The source document mentions Flask in an early architecture paragraph, but later milestones explicitly define FastAPI routes, Uvicorn, Jinja2, JWT, session endpoints, and `main.py`; this project uses FastAPI consistently.

## What is included
- FastAPI backend + Uvicorn
- Jinja2 HTML frontend + responsive CSS + JavaScript
- SQLite database with SQLAlchemy
- Registration, login, logout, JWT cookie authentication
- `/api/session-info`, `/api/session-data`, `/api/history`
- `/api/generate-home`, `/api/generate-party`, `/api/generate-jewelry`
- Gemini multimodal service with optional outfit image input
- Local fallback recommendations if Gemini is unavailable
- Marketplace search links for Amazon, Flipkart, IKEA, Swiggy, Zomato and OYO
- Recommendation history
- Input validation and image validation
- Automated pytest tests

## VS Code — Windows
Open this folder in VS Code, then open Terminal.

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and add your Gemini API key:

```env
SECRET_KEY=replace-with-a-long-random-secret
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
```

You can leave `GEMINI_API_KEY` empty while learning; the app still runs with fallback recommendations.

Run:

```powershell
python run.py
```

Open `http://127.0.0.1:8000`.

API docs: `http://127.0.0.1:8000/docs`

Tests:

```powershell
pytest -q
```

## Flow
1. Register.
2. Login.
3. Choose Home, Party or Jewelry planner.
4. Submit budget and preferences.
5. Backend validates input.
6. Gemini generates structured JSON when configured.
7. Backend normalizes recommendations and enforces budget bounds.
8. Fallback recommendations are used when AI is unavailable.
9. Result is stored in history.
10. Frontend displays recommendations and marketplace search links.

## Gemini note
The supplied document specifies Gemini 1.5 Flash Pro. Model availability changes over time, so this project makes the model configurable and defaults to `gemini-2.5-flash`. If your account exposes another supported Flash model, set `GEMINI_MODEL` in `.env` without changing application code.

## Database
SQLite is the default so no MySQL installation is needed. If you later need MySQL, install `pymysql`, create a database, and set `DATABASE_URL` to a SQLAlchemy MySQL URL.

## Security
Never commit `.env`. The Gemini key stays on the backend. Passwords are hashed. JWT is stored in an HttpOnly cookie. For production, add HTTPS, CSRF protection, rate limiting, object storage, stronger upload isolation, migrations, and production secrets management.
