

---

## 1. Create `workflow.md`

Copy the entire content below into a new file `workflow.md` in your project root (`~/smartform/workflow.md`).

```markdown
# SmartForm – Workflow & Project Master Document

> **Purpose:** Complete reference for the project: architecture, tech choices, branching strategy, development workflow, and troubleshooting.  
> **Goal:** Any developer or AI assistant can read this and immediately know how to work on the project.

---

## 1. Project Overview

**SmartForm** is an AI‑powered government form automation and validation system (portfolio v1).  
It simulates the CNIC Correction/Renewal form. Citizens upload a photo of their national ID card → data is extracted via Tesseract OCR → the form is auto‑filled → an AI assistant (local LLM) validates the form and answers questions → a completed PDF is generated for download.

Built entirely with Django, HTMX, and Python. No JavaScript frameworks.

---

## 2. Tech Stack & Rationale

| Component          | Technology                    | Why |
|--------------------|-------------------------------|-----|
| Backend            | Django 4.x / 6.x              | Full‑stack framework, great for forms, templates, ORM |
| Database           | SQLite (dev)                  | Simplicity; can switch to PostgreSQL later |
| Frontend           | Django Templates, Bootstrap 5, HTMX | Dynamic UI without writing JavaScript |
| AI Assistant       | Ollama `qwen3:1.7b`           | Lightweight (~1.2 GB), runs on CPU, good instruction‑following |
| OCR Engine         | Tesseract + OpenCV preprocessing | Free, offline, no GPU required |
| PDF Generation     | WeasyPrint                    | Converts HTML/CSS to PDF in pure Python |
| Environment        | pipenv                        | Reproducible builds; virtualenv inside project (`.venv/`) recommended |
| Async              | None (synchronous)            | All calls happen in‑request; acceptable for a demo |

---

## 3. System Architecture

```
Browser (HTMX)
      │
      ▼
Django Application
  ├── applications app   → form model, dashboard, views
  ├── assistant app      → chat endpoint, prompt builder
  └── ocr_engine app     → extraction pipeline
      │
      ├──▶ Tesseract OCR        (synchronous, ~2‑5s)
      ├──▶ Ollama LLM API       (localhost:11434, ~3‑7s)
      ├──▶ SQLite Database      (ORM)
      ├──▶ File Storage         (media/id_cards/)
      └──▶ WeasyPrint → PDF     (download)
```

All components are called directly from Django views (no background workers).

---

## 4. Project Directory Structure

```
smartform/
├── config/                 # Django project settings
├── applications/           # Core app (model, forms, views)
├── assistant/              # AI chat (views, prompts)
├── ocr_engine/             # OCR extraction (extractor.py, preprocessing.py)
├── templates/              # Global templates (base.html, partials)
├── static/css/             # Custom styles
├── media/id_cards/         # Uploaded CNIC images
├── system_prompt.txt       # System prompt for the LLM
├── workflow.md             # This file
└── README.md               # Project overview
```

---

## 5. Setup Instructions (after clone)

```bash
# 1. System dependencies (Ubuntu)
sudo apt install tesseract-ocr tesseract-ocr-eng libgl1 libgtk-3-0t64 \
                 libpango-1.0-0 libcairo2 libgdk-pixbuf2.0-0 \
                 libffi-dev libssl-dev python3-dev

# 2. Python environment
pipenv install

# 3. Pull the AI model
ollama pull qwen3:1.7b

# 4. Database
pipenv run python3 manage.py migrate
pipenv run python3 manage.py createsuperuser   # optional

# 5. Run server
pipenv run python3 manage.py runserver
```

---

## 6. Branching Strategy (Git Flow simplified)

- **`main`** – stable, deployable code.
- **`develop`** – integration branch where features are merged.
- **`feature/<feature-name>`** – each new feature/module branches from `develop`.

**Rules:**
- Never commit directly to `main` or `develop`.
- Create a feature branch from `develop`, work, then open a PR to merge back.
- When `develop` is stable, merge it into `main` and tag.

**Examples:**
- `feature/user-auth`
- `feature/ocr-pipeline`
- `feature/chat-assistant`
- `feature/pdf-generation`

---

## 7. Development Workflow

1. Pick a feature from the roadmap.
2. `git checkout -b feature/<name> develop`
3. Implement, commit often.
4. Push branch and create a pull request to `develop`.
5. After review, merge.

---

## 8. Key Design Decisions

- **Synchronous OCR & LLM calls** – Keeps architecture simple for v1. Later projects will add Celery + RabbitMQ.
- **HTMX over JavaScript** – The developer has no frontend experience; HTMX provides interactivity with pure HTML.
- **Tesseract instead of vision LLM** – Lightweight, no GPU needed, custom preprocessing improves accuracy on ID cards.
- **qwen3:1.7b** – Minimal RAM footprint (~2‑3 GB), yet capable enough for structured validation and chat.
- **Model registered in admin** – Allows easy inspection of data during development.

---

## 9. Roadmap (v1 features – build order)

1. ✅ Project scaffold, dependencies, branching, and this document
2. User authentication (Django built‑in login/logout/signup)
3. Dashboard (list user applications)
4. Application form (manual entry)
5. OCR extraction pipeline → auto‑fill form
6. AI assistant chat (HTMX)
7. Assistant‑based validation (ERROR_FIELD parsing)
8. Final submission & status tracking
9. PDF generation (WeasyPrint)
10. Polish & Docker

---

## 10. Troubleshooting & Common Pitfalls

| Issue | Solution |
|-------|----------|
| `tesseract: command not found` | Install Tesseract system‑wide (`sudo apt install tesseract-ocr`) |
| OpenCV `libGL.so.1` missing | Install `libgl1` (Ubuntu 24.04 uses `libgl1`, not `libgl1-mesa-glx`) |
| Ollama connection refused | Ensure service is running: `systemctl status ollama` |
| Model runs out of RAM | Use a smaller quantized model or reduce `num_predict` |
| HTMX not triggering | Check that the CDN script is loaded in `base.html` and the endpoint returns HTML, not a redirect |
| Migrations fail | Delete `db.sqlite3` and `migrations/` folders inside apps (except `__init__.py`), then `makemigrations` and `migrate` |
| Virtualenv in wrong location (Snap VS Code) | Run `pipenv install` inside project directory to create local `.venv` |

---

## 11. Future Upgrades (portfolio v2, v3)

- **v2:** Celery + RabbitMQ for background tasks, multiple form types
- **v3:** Vision LLM for OCR (e.g., `minicpm-v`), REST API, container orchestration

---


