# TALENTIQ 🧠
### AI-Powered Adaptive Interview & Talent Assessment Platform

TalentIQ is a production-grade, full-stack talent simulation platform designed for candidates and hiring teams. Unlike static interview questionnaires, TalentIQ features an **adaptive question engine** that evaluates candidate answers in real time, adjusts question difficulty dynamically, analyzes spoken audio transcripts for verbal fillers and pacing, and delivers an executive-level performance readiness report.

---

## 📸 Screenshots & Previews

| Screen | Preview / Description |
| :--- | :--- |
| **Interactive Landing Page** | Clean presentation of platform capabilities, live metrics, and instant demo access |
| **Executive Dashboard** | Candidate progress tracking, average readiness scores, and quick interview launches |
| **Resume & JD Matcher** | PDF/DOCX parsing, entity extraction, match percentage, and detected skill gaps |
| **Adaptive Interview Room** | Real-time question sequence, audio recorder, filler word tracking, and dynamic difficulty adjustments |
| **Comprehensive Report** | Multi-dimensional scoring radar, question-by-question review, strengths, and study plans |

*(Screenshots can be captured directly from your local deployment at `http://localhost:5173`)*

---

## 🚀 Key Highlights & Features

1. **Adaptive Interview Sequencing**:
   - Evaluates each answer before sequencing the next question.
   - Dynamically elevates difficulty upon mastery or explores weak skills with targeted follow-up prompts.
2. **Speech & Communication Analysis**:
   - Native browser audio recording via the **MediaRecorder API**.
   - Speech-to-text pipeline with verbal filler detection (`um`, `uh`, `like`, `basically`, `actually`, `you know`, `so`).
   - Pace assessment (words per minute) and qualitative communication indicators.
3. **Resume & Job Description Parsing**:
   - Parses **PDF** and **DOCX** formats with structural entity extraction (skills, experience, projects, education).
   - Path-traversal-proof secure storage with UUID-based filenames in `backend/uploads/resumes/`.
   - Semantic matching against target Job Descriptions with percentage fit, matched skills, and detected skill gaps.
4. **Email OTP Authentication**:
   - Two-factor OTP email verification for secure account creation and password resets.
   - Configurable resend cooldowns, attempt limits, and developer mock mode.
5. **Comprehensive Assessment Reports**:
   - Multi-dimensional scoring across Technical Accuracy, Communication Clarity, Problem Solving, and Behavioral fit.
   - Interactive radar visualizer, strengths, weaknesses, question-by-question review, and personalized preparation plan.
6. **Deterministic Mock Mode Out-of-the-Box**:
   - Operates 100% locally without requiring paid third-party API keys (`AI_MOCK_MODE=true`).
   - Seamless plug-in for OpenAI (`gpt-4o`, `gpt-4o-mini`) and Whisper STT.

---

## 🏗 Project Architecture

```mermaid
graph TD
    Client["React 18 + Vite Frontend\n(Tailwind CSS, Lucide Icons, Recharts)"]
    API["FastAPI Backend\n(REST API & WebSockets)"]
    Auth["JWT Auth & Bcrypt Hashing\nEmail OTP Verification"]
    Parser["Resume & JD Parser\n(pypdf & Word OpenXML)"]
    Adaptive["Adaptive Engine &\nAI Provider Abstraction"]
    DB[(PostgreSQL / SQLite\nSQLAlchemy 2.0)]
    Cache[(Redis 7\nPubSub & Caching)]
    OpenAI["OpenAI GPT-4o / Whisper\nor Deterministic Mock Engine"]

    Client -->|HTTP / JSON & Multipart| API
    Client -->|WebSocket| API
    API --> Auth
    API --> Parser
    API --> Adaptive
    API --> DB
    API --> Cache
    Adaptive --> OpenAI
```

---

## 🛠 Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, React Router v6, Recharts, Lucide Icons, MediaRecorder API |
| **Backend** | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0, PyJWT, Native Bcrypt, WebSockets |
| **Database** | PostgreSQL 15 (Docker) / SQLite (Zero-config instant local fallback) |
| **Caching & Queues** | Redis 7, Celery background worker support |
| **AI Abstraction** | OpenAI GPT-4o, OpenAI Whisper STT, High-Fidelity Deterministic Mock Engine |
| **DevOps** | Docker, Docker Compose, Multi-stage builds, NGINX |

---

## 📁 Repository Structure

```
talentiq/
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI app initialization, CORS & WebSockets
│   │   ├── config.py              # Pydantic BaseSettings configuration
│   │   ├── database.py            # SQLAlchemy engine, session & init_db
│   │   ├── models/                # User, Resume, JobDescription, Interview, Evaluation
│   │   ├── schemas/               # Pydantic request/response validation schemas
│   │   ├── api/                   # REST routers: auth, resumes, jobs, interviews, analytics, voice
│   │   ├── services/              # Resume parser, JD parser, matcher, speech analyzer, adaptive engine
│   │   ├── ai/                    # Abstract AI provider, Mock provider, OpenAI provider, STT provider
│   │   ├── auth/                  # Bcrypt hashing & PyJWT token utilities
│   │   ├── websocket/             # WebSocket room manager
│   │   └── utils/                 # String sanitization & text helpers
│   ├── tests/
│   │   ├── test_talentiq_api.py   # Comprehensive Pytest test suite (10/10 passed)
│   │   ├── sample_resume.pdf      # Test fixture for PDF parsing
│   │   └── sample_resume.docx     # Test fixture for Word OpenXML parsing
│   ├── requirements.txt
│   ├── Dockerfile
│   └── pytest.ini
├── frontend/
│   ├── src/
│   │   ├── api/                   # Axios client & typed endpoint services
│   │   ├── components/            # Design system (Button, Input, Card, Badge, ScoreRing, Modal, Avatar)
│   │   ├── context/               # AuthContext & ToastContext
│   │   ├── pages/                 # Landing, Login, Register, Dashboard, Resume, Matching, Room, Report
│   │   ├── types/                 # TypeScript interfaces
│   │   ├── App.tsx                # Client-side routes & ProtectedRoute guards
│   │   ├── main.tsx
│   │   └── index.css              # Modern dark Tailwind design system
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   └── Dockerfile
├── docker-compose.yml             # Postgres, Redis, Backend, Frontend
├── .env.example                   # Environment variable template
├── .gitignore                     # Git exclusion rules
└── README.md                      # Complete documentation
```

---

## ⚡ Quick Start (Local Development)

### 1. Prerequisites
- **Node.js** v18+ (tested on Node v20/v26)
- **Python** 3.11+ (tested on Python 3.12)
- **Git**

### 2. Backend Setup
```bash
cd talentiq/backend

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On macOS / Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI backend server
uvicorn app.main:app --reload --port 8000
```
- Backend API live at: **http://localhost:8000**
- Interactive Swagger UI Docs: **http://localhost:8000/docs**
- ReDoc Documentation: **http://localhost:8000/redoc**

### 3. Frontend Setup
In a new terminal window:
```bash
cd talentiq/frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
- Frontend live at: **http://localhost:5173**

---

## 🗄 Database Configuration

TalentIQ supports two database modes:
1. **SQLite (Zero-Config Default)**:
   ```env
   DATABASE_URL=sqlite:///./talentiq.db
   ```
   Requires zero installation or setup. Automatically created and migrated on startup.
2. **PostgreSQL (Production / Docker)**:
   ```env
   DATABASE_URL=postgresql://talentiq_user:talentiq_password@localhost:5432/talentiq_db
   ```

---

## 📧 Email & OTP Configuration

TalentIQ includes two-factor OTP email verification for secure registrations and password resets:
- **Mock Mode (Default for Development)**:
  ```env
  EMAIL_PROVIDER=smtp
  EMAIL_MOCK_MODE=true
  ```
  OTPs are logged to the backend terminal without requiring an external SMTP relay.
- **Production SMTP**:
  ```env
  EMAIL_MOCK_MODE=false
  SMTP_HOST=smtp.sendgrid.net
  SMTP_PORT=587
  SMTP_USERNAME=apikey
  SMTP_PASSWORD=your_sendgrid_api_key
  SMTP_USE_TLS=true
  EMAIL_FROM=noreply@talentiq.dev
  EMAIL_FROM_NAME=TalentIQ
  ```

---

## 🤖 AI Provider & Mock Mode Configuration

TalentIQ includes a pluggable provider abstraction for LLMs and speech transcription:

- **Zero-Cost Local Mock Mode (Default)**:
  ```env
  AI_MOCK_MODE=true
  AI_PROVIDER=mock
  STT_PROVIDER=mock
  ```
  Generates contextual technical questions and speech assessments locally. No API keys required.

- **OpenAI GPT-4o Integration**:
  ```env
  AI_MOCK_MODE=false
  AI_PROVIDER=openai
  AI_API_KEY=sk-proj-your-openai-api-key
  AI_MODEL=gpt-4o-mini
  STT_PROVIDER=openai_whisper
  STT_API_KEY=sk-proj-your-openai-api-key
  ```

---

## 🐳 Running with Docker Compose

To start the complete production stack (PostgreSQL, Redis, FastAPI, and React Nginx frontend) with one command:

```bash
cd talentiq
docker compose up --build
```

Services will be mapped to:
- **Frontend App**: http://localhost:3000
- **FastAPI API**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

To stop containers:
```bash
docker compose down
```

---

## 🧪 Running Automated Tests

Run the backend Pytest suite verifying health, authentication, resume upload & parsing, job matching, speech filler detection, interview lifecycle, and report generation:

```bash
cd talentiq/backend
PYTHONPATH=. .venv/bin/pytest -v
```

10 comprehensive test suites run with a **100% pass rate**.

---

## ⚙️ Environment Variables Reference

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

| Variable | Default | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `sqlite:///./talentiq.db` | SQLAlchemy database connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis caching & broker URL |
| `JWT_SECRET` | `secret` | Secret key for JWT signing |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Token expiration duration (24 hours) |
| `AI_MOCK_MODE` | `true` | When true, enables zero-cost deterministic mock AI |
| `AI_PROVIDER` | `mock` | `mock` or `openai` |
| `AI_API_KEY` | `""` | OpenAI API key (optional if Mock Mode enabled) |
| `AI_MODEL` | `gpt-4o-mini` | LLM model identifier |
| `STT_PROVIDER` | `mock` | `mock` or `openai_whisper` |
| `STT_API_KEY` | `""` | OpenAI Whisper STT API key |
| `MAX_UPLOAD_SIZE_MB` | `10` | Maximum allowed resume file size in megabytes |
| `EMAIL_PROVIDER` | `smtp` | Email delivery provider |
| `EMAIL_MOCK_MODE` | `true` | When true, logs OTP codes to terminal |
| `SMTP_HOST` | `""` | Outgoing SMTP server hostname |
| `SMTP_PORT` | `587` | SMTP server port |
| `SMTP_USERNAME` | `""` | SMTP username |
| `SMTP_PASSWORD` | `""` | SMTP password |
| `SMTP_USE_TLS` | `true` | Enable TLS security for email delivery |
| `EMAIL_FROM` | `noreply@talentiq.dev` | From email address |
| `OTP_EXPIRE_MINUTES` | `10` | OTP validity duration |
| `OTP_RESEND_COOLDOWN_SECONDS` | `60` | Cooldown period before resending OTP |
| `OTP_MAX_ATTEMPTS` | `5` | Maximum failed verification attempts before invalidation |
| `CORS_ORIGINS` | `localhost urls` | Comma-separated list of allowed frontend origins |

---

## 🔒 Security Best Practices

- **Bcrypt Password Hashing**: Passwords hashed using standard native **bcrypt** with dynamic salting.
- **Stateless Bearer JWTs**: Fast, cryptographically signed tokens with expiration checks.
- **Strict File Upload Validation**: Enforces `.pdf` and `.docx` extensions and MIME types with a 10MB payload ceiling.
- **Path Traversal Protection**: Uploaded files stored with sanitized names and UUID prefixes in an isolated uploads directory.
- **Safe SQL Operations**: 100% parameterized queries via SQLAlchemy ORM.
- **Credential Hygiene**: Sensitive secrets, credentials, and virtual environments are excluded from Git via `.gitignore`.

---

## 🔮 Future Enhancements

- [ ] Video interview recording and non-verbal posture / eye contact analysis.
- [ ] Collaborative interview rooms with human panelist scoring alongside AI.
- [ ] Direct ATS (Applicant Tracking System) webhook integrations (Greenhouse, Lever).
- [ ] Fine-tuned domain-specific interview models for medical, finance, and legal talent.

---

## 📄 License

MIT License. Designed and engineered for candidates and high-performance talent acquisition teams.
