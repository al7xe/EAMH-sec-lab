# EAMH Security Lab

**Software Security Course Project**  
**Tagline:** Build Secure. Think Smart.

EAMH Security Lab is a student team workspace for building a Flask web application while practicing secure software development.

## Team
- Elias
- Ahmed
- Mohammed
- Hussam

## Current milestone
The first repository version contains a responsive Arabic landing page and a minimal Flask application.

## Tech stack
- Python 3
- Flask
- HTML5
- CSS3

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux / macOS
   source .venv/bin/activate

   pip install -r requirements.txt
   ```

3. Start the app:

   ```bash
   python app.py
   ```

4. Open http://127.0.0.1:5000

Health check: http://127.0.0.1:5000/health

## Security notes
This is an educational starter, not a production-ready application. Future milestones will add authentication, authorization, CSRF protection, secure password hashing, input validation, and automated security tests. Never commit credentials, secret keys, or personal data.

## Repository structure

```text
EAMH-sec-lab/
├── app.py
├── requirements.txt
├── templates/
│   └── index.html
├── static/
│   └── css/
│       └── style.css
├── .gitignore
└── README.md
```
