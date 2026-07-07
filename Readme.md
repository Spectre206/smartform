

```markdown
# SmartForm - AI-Powered Form Automation & Validation
> 📘 Full project documentation: [workflow.md](workflow.md)

A web application that automates the completion of government forms (CNIC correction/renewal) by extracting data from uploaded ID cards using **Tesseract OCR**, auto‑filling forms, and providing an **AI assistant** (powered by a local LLM via Ollama) that validates entries, answers questions, and detects errors. Built entirely with Django, HTMX, and Python—no JavaScript required.

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![Django](https://img.shields.io/badge/django-4.x-green.svg)
![HTMX](https://img.shields.io/badge/HTMX-2.0-orange.svg)
![Ollama](https://img.shields.io/badge/Ollama-llama3-yellow.svg)
![Tesseract](https://img.shields.io/badge/Tesseract-OCR-9cf)

---

## Table of Contents
- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [System Architecture](#system-architecture)
- [Features](#features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview
Government forms are tedious—citizens retype the same personal information from their ID cards over and over. **SmartForm** solves this by:

1. **Upload** a photo of your CNIC (National ID card).
2. **Extract** name, father’s name, CNIC number, date of birth using custom OCR (Tesseract + OpenCV).
3. **Auto‑fill** the application form.
4. **Chat** with an AI assistant that explains fields, checks for missing data, and highlights errors.
5. **Download** a ready‑to‑submit PDF.

Everything runs locally—no cloud services, no JavaScript frameworks—making it a great full‑stack portfolio project.

---

## Tech Stack
| Component          | Technology |
|--------------------|-------------|
| Backend            | Django 4.x + Django REST Framework (optional) |
| Database           | SQLite (dev) / PostgreSQL (prod) |
| Frontend           | Django Templates + Bootstrap 5 + HTMX |
| AI Assistant       | Ollama running `llama3` (local, CPU‑only) |
| OCR Engine         | Tesseract via `pytesseract`, image preprocessing with OpenCV |
| PDF Generation     | WeasyPrint |
| Environment        | pipenv |

---

## System Architecture
```
┌─────────────┐      HTTP requests       ┌──────────────────┐
│   Browser   │◄─────────────────────────│   Django App     │
│  (HTMX UI)  │─────────────────────────►│                  │
└──────┬──────┘   HTML partials + HTMX    │ • Views          │
       │                                 │ • Forms          │
       │ File upload (CNIC image)        │ • Templates      │
       │                                 │ • OCR call        │
       │                                 │ • LLM call        │
       │                                 │ • PDF gen         │
       │                                 └──┬────┬────┬────┬──┘
       │                                    │    │    │    │
       │                    ┌───────────────┘    │    │    └──────────────┐
       │                    │                    │    │                   │
       ▼                    ▼                    ▼    ▼                   ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐  ┌──────────┐  ┌─────────┐
│ File Storage│   │ Tesseract   │   │  Ollama     │  │ Database │  │  PDF    │
│ (media/)    │   │ OCR Engine  │   │  (llama3)   │  │ (ORM)    │  │ Output  │
│             │   │ + OpenCV    │   │             │  │          │  │(download)│
└─────────────┘   └─────────────┘   └─────────────┘  └──────────┘  └─────────┘
```

*All components run synchronously within the Django request‑response cycle (OCR ~2‑5s, LLM ~3‑7s).*

---

## Features
- **User Authentication** – sign up, log in, dashboard with application history.
- **ID Card OCR** – extract personal information from CNIC images using a custom Tesseract pipeline.
- **Auto‑fill Form** – data from OCR automatically populates the application.
- **AI Assistant (Chat)** – interactive chat widget (HTMX) that:
  - Explains form fields & required documents.
  - Checks form for errors and missing data.
  - Returns structured error messages to highlight specific fields.
- **Real‑time Validation** – inline field validation powered by Django forms + HTMX.
- **Consistency Checks** – cross‑field validation (e.g., date of birth vs. age, CNIC format).
- **PDF Generation** – generates a filled, official‑looking application form for download.
- **Status Tracking** – visual progress: Draft → Extracted → Validated → PDF Ready.

---

## Project Structure
```
smartform/
├── manage.py
├── Pipfile
├── Pipfile.lock
├── system_prompt.txt
├── config/                  # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── applications/            # Core app: form model, views, dashboards
├── assistant/               # AI chat assistant
├── ocr_engine/              # Tesseract pipeline
├── templates/
│   ├── base.html
│   └── partials/
└── static/
```

---

## Getting Started

### Prerequisites
- **Python 3.12+** (tested on Ubuntu 24.04)
- **Tesseract OCR** installed system‑wide
- **Ollama** installed and a model pulled (e.g., `llama3`)
- **pipenv** for virtual environments

### System Dependencies (Ubuntu)
```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-eng libgl1 libgtk-3-0t64 \
                 libpango-1.0-0 libcairo2 libgdk-pixbuf2.0-0 \
                 libffi-dev libssl-dev python3-dev -y
```

### Install Ollama & Pull Model
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3
```

### Clone & Setup Environment
```bash
git clone <your-repo-url> smartform
cd smartform
pipenv install
```

### Apply Migrations & Create Superuser
```bash
pipenv run python3 manage.py migrate
pipenv run python3 manage.py createsuperuser
```

### Run Development Server
```bash
pipenv run python3 manage.py runserver
```
Visit http://localhost:8000

---

## Roadmap
This project is the first of three planned portfolio pieces, progressively increasing complexity:

1. **SmartForm (v1)** – current: synchronous OCR + text‑based AI assistant, simple form.
2. **Next project** – add Celery + RabbitMQ for background processing, support multiple form types.
3. **Final project** – replace Tesseract with a vision‑language model (Ollama vision), add API endpoints, container orchestration.

---

## Contributing
This is a personal portfolio project, but suggestions are welcome! Feel free to open an issue or submit a pull request.

---

## License
This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
```

---

Just save it as `README.md` in your `smartform/` folder. Once you start pushing to GitHub, this will be the first thing people see—clean, professional, and ready for your portfolio.
