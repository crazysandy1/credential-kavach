# Credential Kavach

**Academic credential verification platform with OCR and blockchain anchoring.** Built for Smart India Hackathon (SIH) 2025.

Students upload marks cards and certificates. OCR extracts the data. Colleges and government reviewers verify it. A cryptographic hash of each verified document is anchored on the IOTA Tangle, so employers can check a credential in seconds and detect tampering.

> **Status:** hackathon prototype. Not production-ready. See [Known limitations](#known-limitations).

Built as a team for SIH-2025 with [@DarshanCHMSR](https://github.com/DarshanCHMSR) (team lead) and teammates. I (@crazysandy1) was co-lead.

## The problem

Fake degrees cost candidates opportunities and employers money. Manual verification means phone calls, email and weeks of waiting. Credential Kavach digitizes, secures and verifies credentials in one flow. The full pitch is in [`docs/pitch.md`](docs/pitch.md).

## How it works

1. **Digitize.** A student uploads a marks card. PaddleOCR with OpenCV preprocessing extracts subjects, marks and student details into structured JSON.
2. **Review.** A college or government user verifies or rejects the document. All actions go to an audit log.
3. **Secure.** A hash of the verified file is anchored on the IOTA Tangle (testnet by default).
4. **Verify.** An employer checks a file or credential. The system compares its hash with the anchored record.

## Roles

| Role | What they do |
|---|---|
| Student | Register, upload documents, track verification status |
| College | Review and verify student documents, see institution stats |
| Government | Approve users, oversee the system, read audit logs and analytics |
| Employer | Verify credentials by file or hash |

## Repository layout

```
backend/         Flask API: auth, documents, admin, OCR pipeline (SQLite, JWT)
backend-block/   Django REST API: certificate hashing and IOTA blockchain anchoring (Docker)
frontend-sih/    React 18 web app (Create React App)
docs/            Pitch script, feature summaries, backend usage guide
```

The two backends are independent services. `backend/` handles users, documents and OCR. `backend-block/` handles certificate hashes and blockchain verification.

## Tech stack

- **Frontend:** React 18, React Router 6, Axios, react-dropzone, react-hot-toast, lucide-react.
- **Backend (Flask):** Flask 3, SQLAlchemy, Flask-JWT-Extended, Flask-CORS, bcrypt, SQLite.
- **OCR:** PaddleOCR 3, PaddlePaddle, OpenCV, Pillow, pandas.
- **Blockchain service:** Django 4.2 + Django REST Framework, IOTA testnet, Docker, Pipenv.

## Getting started

Requirements: Python 3.10+, Node.js 16+, and (optional) Docker for `backend-block`.

### 1. Flask backend (users, documents, OCR)

```bash
git clone https://github.com/crazysandy1/credential-kavach.git
cd credential-kavach/backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt    # PaddleOCR is a large download
cp .env.example .env               # edit SECRET_KEY and ADMIN_PASSWORD
python main.py                     # http://127.0.0.1:5001
```

On first run the app creates the SQLite database and a government admin account:

- Email: `admin@credentialkavach.gov.in`
- Password: the value of `ADMIN_PASSWORD` in your `.env` (defaults to `Admin@123` if unset. Always set your own.)

### 2. Frontend

```bash
cd frontend-sih
npm install
npm start                          # http://localhost:3000
```

Set `REACT_APP_API_URL` if the backend is not on `http://127.0.0.1:5001`.

### 3. Blockchain service (optional)

```bash
cd backend-block
cp .env.example .env
docker-compose up --build          # http://localhost:8000/api/health/
```

Or run locally with `pipenv install && pipenv run python manage.py migrate && pipenv run python manage.py runserver`.

## API overview

### Flask backend (`:5001`)

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/auth/signup`, `/api/auth/login` | POST | Register and sign in (JWT) |
| `/api/auth/profile` | GET | Current user |
| `/api/documents`, `/api/documents/upload` | GET, POST | List and upload (runs OCR) |
| `/api/documents/<id>`, `/api/documents/<id>/verify` | GET, POST | Detail and verify or reject |
| `/api/documents/<id>/download` | GET | Download file |
| `/api/admin/users`, `/api/admin/users/<id>/approve` | GET, POST | Manage and approve users |
| `/api/admin/audit-logs`, `/api/admin/stats/system` | GET | Audit trail and stats |

### Blockchain service (`:8000`)

| Endpoint | Purpose |
|---|---|
| `/api/health/`, `/api/info/` | Status and info |
| `/api/auth/register/`, `login/`, `logout/`, `profile/` | Accounts |
| `/api/certificates/`, `certificates/upload/`, `certificates/check-hash/` | Store and hash certificates |
| `/api/certificates/<id>/verify-iota/` | Check anchored record on IOTA |
| `/api/verification/verify/`, `verification/attempts/`, `verification/failed-attempts/` | Verification flow and history |
| `/api/dashboard/stats/` | Dashboard numbers |

More detail: [`docs/BACKEND_USAGE_GUIDE.md`](docs/BACKEND_USAGE_GUIDE.md), [`docs/OCR_IMPLEMENTATION_SUMMARY.md`](docs/OCR_IMPLEMENTATION_SUMMARY.md), [`docs/COLLEGE_DASHBOARD_ENHANCEMENT_SUMMARY.md`](docs/COLLEGE_DASHBOARD_ENHANCEMENT_SUMMARY.md), [`docs/GOVERNMENT_DASHBOARD_ENHANCEMENT_SUMMARY.md`](docs/GOVERNMENT_DASHBOARD_ENHANCEMENT_SUMMARY.md).

## Security notes

- Passwords hashed with bcrypt. JWT auth with role checks. Audit log for user actions.
- Secrets live in `.env` (git-ignored). Use `.env.example` as a template.
- Databases, uploads and sample student documents are git-ignored. Never commit real student documents.
- Change `SECRET_KEY`, `JWT` secrets and `ADMIN_PASSWORD` before any shared deployment.

## Known limitations

- Prototype quality. Few automated tests; `backend/test_*.py` are ad-hoc scripts.
- The two backends are not yet merged behind one API.
- OCR accuracy depends on scan quality (tuned on a few sample marks cards).
- Email verification and production database setup are not configured.
- Hardcoded default admin is for demo only.

## Roadmap

- Merge the two backends into one service with PostgreSQL.
- Real test suite and CI.
- Cloud file storage and email verification.
- Employer portal polish and public verification links.

## License

No license chosen yet (team project). All rights reserved by the authors until one is added.
