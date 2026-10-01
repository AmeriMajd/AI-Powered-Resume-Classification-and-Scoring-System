from FlaskApp.analyzer import analyze_text, classify_role, extract_skills


def test_extract_skills_uses_canonical_names():
    skills = extract_skills("Built Python REST APIs with FastAPI, PostgreSQL, and Docker.")
    assert skills == ["Python", "FastAPI", "REST APIs", "PostgreSQL", "Docker"]


def test_backend_resume_classification():
    result = classify_role(
        "Python backend engineer building FastAPI REST APIs with PostgreSQL, Redis and Docker"
    )
    assert result.role == "Backend Engineer"
    assert 0 <= result.confidence <= 1


def test_analysis_returns_explainable_breakdown():
    result = analyze_text(
        "Python developer. Built FastAPI services using PostgreSQL and Docker for 4M records.",
        "We need a Python backend developer with FastAPI, PostgreSQL, Docker and AWS.",
    )
    assert 0 <= result["match_score"] <= 100
    assert "FastAPI" in result["matching_skills"]
    assert "AWS" in result["missing_skills"]
    assert result["recommendations"]
