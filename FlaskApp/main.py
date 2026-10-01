from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from pypdf import PdfReader
from werkzeug.exceptions import RequestEntityTooLarge

try:
    from .analyzer import analyze_text
except ImportError:  # Allows `python FlaskApp/main.py` in local development.
    from analyzer import analyze_text


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_BUILD_DIR = BASE_DIR.parent / "frontapp" / "build"
MAX_PDF_BYTES = 6 * 1024 * 1024
MAX_PAGES = 30
MAX_JOB_DESCRIPTION_CHARS = 20_000


def extract_text_from_pdf(pdf_file) -> tuple[str, int]:
    reader = PdfReader(pdf_file)
    if len(reader.pages) > MAX_PAGES:
        raise ValueError(f"Please upload a PDF with no more than {MAX_PAGES} pages.")

    pages = [(page.extract_text() or "").strip() for page in reader.pages]
    text = "\n".join(page for page in pages if page).strip()
    if not text:
        raise ValueError("No selectable text was found. Scanned PDFs are not supported yet.")
    return text, len(reader.pages)


def create_app() -> Flask:
    app = Flask(__name__, static_folder=str(FRONTEND_BUILD_DIR), static_url_path="")
    app.config["MAX_CONTENT_LENGTH"] = MAX_PDF_BYTES

    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    @app.errorhandler(RequestEntityTooLarge)
    def file_too_large(_error):
        return jsonify({"error": "The PDF is too large. Maximum size is 6 MB."}), 413

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "engine": "tfidf-demo"})

    @app.post("/api/analyze")
    def analyze_resume():
        resume_file = request.files.get("resume")
        job_description = request.form.get("job_description", "").strip()

        if resume_file is None or not resume_file.filename:
            return jsonify({"error": "Please choose a resume PDF."}), 400
        if not resume_file.filename.casefold().endswith(".pdf"):
            return jsonify({"error": "Only PDF resumes are accepted."}), 400
        if not job_description:
            return jsonify({"error": "Please paste a job description."}), 400
        if len(job_description) > MAX_JOB_DESCRIPTION_CHARS:
            return jsonify({"error": "The job description is too long."}), 400

        try:
            resume_text, page_count = extract_text_from_pdf(resume_file.stream)
            result = analyze_text(resume_text, job_description)
        except (ValueError, TypeError) as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            app.logger.exception("Resume analysis failed")
            return jsonify({"error": "The PDF could not be analyzed. Please try another file."}), 422

        result["document"] = {
            "filename": Path(resume_file.filename).name,
            "pages": page_count,
            "word_count": len(resume_text.split()),
        }
        return jsonify(result)

    @app.get("/")
    def index():
        if not (FRONTEND_BUILD_DIR / "index.html").exists():
            return jsonify(
                {
                    "name": "Resume Match Lab API",
                    "status": "ready",
                    "hint": "Build the React app to serve the web interface.",
                }
            )
        return send_from_directory(app.static_folder, "index.html")

    @app.get("/<path:path>")
    def frontend(path: str):
        candidate = FRONTEND_BUILD_DIR / path
        if candidate.is_file():
            return send_from_directory(app.static_folder, path)
        if (FRONTEND_BUILD_DIR / "index.html").exists():
            return send_from_directory(app.static_folder, "index.html")
        return jsonify({"error": "Not found"}), 404

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG") == "1")
