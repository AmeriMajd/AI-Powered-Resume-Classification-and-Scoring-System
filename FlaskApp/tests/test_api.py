from io import BytesIO

from FlaskApp.main import app


def test_health_endpoint():
    client = app.test_client()
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_analyze_requires_a_pdf():
    client = app.test_client()
    response = client.post(
        "/api/analyze",
        data={
            "resume": (BytesIO(b"plain text"), "resume.txt"),
            "job_description": "Python developer",
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "Only PDF resumes are accepted."
