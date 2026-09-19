# SnapClass AI Attendance System

> A recruiter-ready, privacy-conscious attendance platform combining **face recognition**, **voice verification**, **QR-based enrollment**, role-based portals, and an auditable attendance ledger.

**Author:** Ayush Kumar Gupta · [GitHub](https://github.com/Blood79) · [LinkedIn](https://linkedin.com/in/ayush-kumar-gupta-43314b238)

[![CI](https://github.com/Blood79/SnapClass-AI-Attendance-System/actions/workflows/ci.yml/badge.svg)](https://github.com/Blood79/SnapClass-AI-Attendance-System/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)

## Why this project stands out

SnapClass is designed as an end-to-end engineering project rather than a single notebook. It separates biometric pipelines from attendance rules and persistence, includes tests and CI, exposes a lightweight Flask landing page, and keeps cloud credentials outside source control.

### Core capabilities

| Area | What is implemented |
|---|---|
| Face attendance | Face detection + 128-D face descriptors through the optional `face_recognition` backend |
| Voice attendance | Voice embeddings / feature vectors with cosine-similarity verification |
| QR workflow | Signed enrollment payloads that can be validated without exposing secrets |
| Roles | Teacher and student flows with clear authentication boundaries |
| Attendance | Explicit present/absent decisions, duplicate protection, timestamps and audit-friendly records |
| Data layer | Local demo repository plus Supabase-ready SQL schema |
| Engineering | Typed Python modules, unit tests, Docker, CI, security checks and docs |

## Architecture

```text
                 ┌─────────────────────────────┐
                 │       Streamlit UI          │
                 │ Teacher • Student • Admin   │
                 └──────────────┬──────────────┘
                                │
                 ┌──────────────▼──────────────┐
                 │    Application Services      │
                 │ Auth • QR • Attendance       │
                 └───────┬──────────┬───────────┘
                         │          │
              ┌──────────▼───┐  ┌───▼──────────┐
              │ Face Pipeline │  │ Voice Engine │
              │ detect/embed  │  │ embed/match  │
              └──────────┬────┘  └────┬─────────┘
                         │             │
                         └──────┬──────┘
                                ▼
                 ┌─────────────────────────────┐
                 │ Repository / Storage Layer  │
                 │ Demo JSON • Supabase schema │
                 └─────────────────────────────┘
```

The landing page is intentionally separate from the application UI so the project can be presented as a deployable product, not only as coursework.

## Project structure

```text
SnapClass-AI-Attendance-System/
├── app/
│   ├── streamlit_app.py        # Main application entry point
│   └── landing.py              # Flask landing page
├── src/
│   ├── attendance/service.py   # Attendance business rules
│   ├── authentication/auth.py  # Password hashing + roles
│   ├── computer_vision/face.py # Face embedding adapter
│   ├── database/repository.py  # Local repository for demo/dev
│   ├── qr/service.py            # Signed QR payloads
│   ├── voice/recognizer.py      # Voice verification adapter
│   └── config.py                # Environment-driven configuration
├── database/schema.sql
├── tests/
├── docs/
├── .github/workflows/
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements.txt
└── requirements-ci.txt
```

## Run locally

### 1. Create an environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

For the lightweight test suite:

```bash
pip install -r requirements-ci.txt
pytest
```

### 3. Start the app

```bash
streamlit run app/streamlit_app.py
```

Optional landing page:

```bash
python app/landing.py
```

## Demo mode

The repository includes a local JSON repository so the application can be evaluated without creating a Supabase project first. Biometric modules are adapters: the UI can display the feature set while the heavy face/voice dependencies are installed only when real biometric capture is needed.

For cloud mode, populate `.env` or Streamlit secrets with the variables described in [SETUP](docs/SETUP.md).

## Responsible biometric design

Biometric verification is inherently sensitive. SnapClass therefore keeps the biometric layer isolated, documents the verification thresholds as configurable parameters, and avoids putting raw biometric media into the repository.

**This project is a technical prototype, not an identity-proofing product.** Any real deployment should add explicit consent, retention/deletion policies, access controls, liveness/anti-spoofing, legal review, and monitoring for false matches.

See [Biometric Privacy](docs/BIOMETRIC_PRIVACY.md) and [Security](docs/SECURITY.md).

## Design decisions

- **Adapters over hard-coding:** face and voice implementations sit behind narrow interfaces.
- **Business logic is testable:** attendance decisions do not depend on Streamlit.
- **Deterministic QR tokens:** signed payloads make enrollment links tamper-evident.
- **No secrets in Git:** configuration is environment driven.
- **Demo-first, cloud-ready:** reviewers can run the project locally without a hosted database.

## Roadmap

- WebRTC-based browser capture
- Liveness / anti-spoofing research module
- Admin analytics dashboard
- Exportable CSV/PDF attendance reports
- Role-based Supabase RLS policies
- Model drift and threshold calibration reports

## Attribution

The project concept and feature direction were independently re-engineered after reviewing publicly available demonstrations of AI attendance workflows, including the SnapClass repositories by **Shradha Khapra**. This repository is a standalone implementation and is **not a fork** of those repositories.

## License

MIT © 2026 Ayush Kumar Gupta
