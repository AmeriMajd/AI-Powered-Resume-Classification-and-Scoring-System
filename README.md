# Resume Match Lab

An explainable resume-analysis web app that compares a PDF resume with a job
description. It predicts the closest technical role, calculates a directional
match score, identifies matching and missing skills, and produces practical
recommendations.

[![Deploy on Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/AmeriMajd/AI-Powered-Resume-Classification-and-Scoring-System)

> **Portfolio demo:** this project supports career exploration and resume
> tailoring. It is not intended to make or automate hiring decisions.

## What the demo shows

- PDF text extraction with input validation and in-memory processing
- Explainable TF-IDF role classification and resume/job similarity
- Canonical technical-skill extraction and gap analysis
- A responsive React interface served by the Flask backend
- Production serving with Gunicorn and a multi-stage Docker build
- Health checks, error handling, API tests, and analyzer tests

## Architecture

    Browser
      └── React interface
            └── POST /api/analyze (PDF + job description)
                  └── Flask API
                        ├── PDF text extraction
                        ├── TF-IDF role and text similarity
                        ├── skill taxonomy matching
                        └── explainable JSON report

The repository originally referenced local Transformer and CrossEncoder
checkpoints that were not committed. The public demo therefore uses a
lightweight, deterministic NLP engine that fits comfortably on a small CPU
instance. The experimental training scripts remain in FlaskApp/Models for
reference, but they are not loaded by the deployed app.

## Run with Docker

    docker build -t resume-match-lab .
    docker run --rm -p 10000:10000 resume-match-lab

Open http://localhost:10000.

## Run locally for development

Backend:

    python -m venv .venv
    source .venv/bin/activate
    pip install -r FlaskApp/requirements-dev.txt
    python FlaskApp/main.py

Frontend, in another terminal:

    cd frontapp
    npm ci
    npm start

The React development server proxies /api requests to Flask on port 5000.

## Tests

    pytest FlaskApp/tests
    cd frontapp && CI=true npm test -- --watchAll=false

## Deploy to Render

The included render.yaml and Dockerfile define the whole deployment.

1. Push the deployment files to the GitHub repository.
2. Sign in to [Render](https://dashboard.render.com/).
3. Choose **New → Blueprint** and connect this repository.
4. Approve the resume-match-lab free web service.
5. Wait for the image to build, then open the assigned onrender.com URL.

Free Render services can take time to wake after inactivity. Use a paid
instance if consistent response time is required.

## API

### GET /api/health

Returns service readiness.

### POST /api/analyze

Multipart form fields:

- resume: text-based PDF, maximum 6 MB and 30 pages
- job_description: required text, maximum 20,000 characters

Uploaded files are processed in memory and are not intentionally persisted.

## Technology

React 19 · Material UI · Flask · scikit-learn · pypdf · Gunicorn · Docker

## Limitations

- Scanned PDFs need OCR and are not currently supported.
- Skill detection uses an explicit software/data skill taxonomy.
- Scores measure textual and skill overlap; they are not calibrated employment
  probabilities.
- The public demo does not use the absent private trained checkpoints.
