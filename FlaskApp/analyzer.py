"""Lightweight, explainable NLP engine for the public portfolio demo.

The original repository referenced private model checkpoints that were not
committed. This module keeps the demo deployable on a small CPU instance by
using TF-IDF similarity and an explicit skills taxonomy. It is intentionally
described as a demo engine, not as a replacement for a trained hiring model.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


ROLE_PROFILES = {
    "Machine Learning Engineer": (
        "python machine learning deep learning model training inference mlops "
        "tensorflow pytorch scikit-learn feature engineering model deployment"
    ),
    "Data Scientist": (
        "python statistics data analysis pandas numpy sql experimentation "
        "visualization machine learning forecasting business insights"
    ),
    "Data Engineer": (
        "python sql etl data pipelines airflow spark kafka warehouse dbt cloud "
        "data modeling batch streaming"
    ),
    "Backend Engineer": (
        "python java node backend rest api fastapi flask django databases sql "
        "postgresql redis microservices docker authentication"
    ),
    "Frontend Engineer": (
        "javascript typescript react angular vue html css frontend responsive "
        "accessibility user interface web performance"
    ),
    "Full-Stack Engineer": (
        "javascript typescript react python node full stack frontend backend api "
        "database sql web application docker"
    ),
    "DevOps Engineer": (
        "aws azure cloud docker kubernetes terraform ci cd github actions linux "
        "monitoring infrastructure deployment automation"
    ),
    "Mobile Engineer": (
        "flutter dart android ios kotlin swift react native mobile application "
        "firebase app store"
    ),
    "Cybersecurity Analyst": (
        "security cybersecurity vulnerability penetration testing network siem "
        "incident response risk compliance linux"
    ),
}


SKILL_ALIASES = {
    "Python": ("python",),
    "Java": ("java",),
    "C++": ("c++", "cpp"),
    "JavaScript": ("javascript",),
    "TypeScript": ("typescript",),
    "React": ("react", "react.js", "reactjs"),
    "Angular": ("angular",),
    "Vue": ("vue", "vue.js"),
    "Node.js": ("node.js", "nodejs"),
    "FastAPI": ("fastapi",),
    "Flask": ("flask",),
    "Django": ("django",),
    "REST APIs": ("rest api", "rest apis", "restful api", "restful apis"),
    "GraphQL": ("graphql",),
    "SQL": ("sql",),
    "PostgreSQL": ("postgresql", "postgres"),
    "MySQL": ("mysql",),
    "MongoDB": ("mongodb",),
    "Redis": ("redis",),
    "Pandas": ("pandas",),
    "NumPy": ("numpy",),
    "Scikit-learn": ("scikit-learn", "sklearn"),
    "TensorFlow": ("tensorflow",),
    "PyTorch": ("pytorch",),
    "NLP": ("natural language processing", "nlp"),
    "Machine Learning": ("machine learning",),
    "Deep Learning": ("deep learning",),
    "Data Visualization": ("data visualization",),
    "Power BI": ("power bi", "powerbi"),
    "Tableau": ("tableau",),
    "Docker": ("docker",),
    "Kubernetes": ("kubernetes", "k8s"),
    "AWS": ("aws", "amazon web services"),
    "Azure": ("azure",),
    "Google Cloud": ("google cloud", "gcp"),
    "Git": ("git", "github", "gitlab"),
    "CI/CD": ("ci/cd", "continuous integration", "continuous delivery"),
    "Linux": ("linux",),
    "Airflow": ("airflow",),
    "Spark": ("apache spark", "spark"),
    "Kafka": ("kafka",),
    "Flutter": ("flutter",),
}


@dataclass(frozen=True)
class Classification:
    role: str
    confidence: float


def _normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold()).strip()


def extract_skills(text: str) -> list[str]:
    """Return canonical skill names found as complete terms in text."""
    normalized = _normalized(text)
    found: list[str] = []
    for skill, aliases in SKILL_ALIASES.items():
        for alias in aliases:
            pattern = rf"(?<![\w+]){re.escape(alias.casefold())}(?![\w+])"
            if re.search(pattern, normalized):
                found.append(skill)
                break
    return found


def classify_role(resume_text: str) -> Classification:
    labels = list(ROLE_PROFILES)
    documents = [resume_text, *ROLE_PROFILES.values()]
    vectors = TfidfVectorizer(stop_words="english", ngram_range=(1, 2)).fit_transform(documents)
    similarities = cosine_similarity(vectors[0:1], vectors[1:]).ravel()
    best_index = int(np.argmax(similarities))

    # This is relative similarity, not a calibrated hiring probability.
    positive = np.clip(similarities, 0, None)
    relative = float(positive[best_index] / positive.sum()) if positive.sum() else 0.0
    confidence = min(0.99, max(0.25, relative + float(positive[best_index]) * 0.5))
    return Classification(labels[best_index], round(confidence, 4))


def _top_job_terms(resume_text: str, job_description: str, limit: int = 10) -> list[str]:
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=800,
        token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z+#.\-/]{1,}\b",
    )
    matrix = vectorizer.fit_transform([resume_text, job_description])
    terms = vectorizer.get_feature_names_out()
    job_weights = matrix[1].toarray().ravel()
    ranked = np.argsort(job_weights)[::-1]
    return [str(terms[index]) for index in ranked if job_weights[index] > 0][:limit]


def analyze_text(resume_text: str, job_description: str) -> dict:
    classification = classify_role(resume_text)
    resume_skills = extract_skills(resume_text)
    requested_skills = extract_skills(job_description)
    resume_skill_set = set(resume_skills)
    matching_skills = [skill for skill in requested_skills if skill in resume_skill_set]
    missing_skills = [skill for skill in requested_skills if skill not in resume_skill_set]

    pair_vectors = TfidfVectorizer(stop_words="english", ngram_range=(1, 2)).fit_transform(
        [resume_text, job_description]
    )
    text_similarity = float(cosine_similarity(pair_vectors[0:1], pair_vectors[1:2])[0, 0])
    if requested_skills:
        skill_coverage = len(matching_skills) / len(requested_skills)
        # Named skill coverage is more actionable than raw wording overlap, so
        # it carries the larger share of the directional match score.
        match_score = (0.40 * text_similarity) + (0.60 * skill_coverage)
    else:
        skill_coverage = None
        match_score = text_similarity

    top_terms = _top_job_terms(resume_text, job_description)
    normalized_resume = _normalized(resume_text)
    matched_terms = [term for term in top_terms if term.casefold() in normalized_resume]

    recommendations = []
    if missing_skills:
        recommendations.append(
            "If they reflect your real experience, add evidence for: " + ", ".join(missing_skills[:5]) + "."
        )
    if len(resume_text.split()) < 250:
        recommendations.append("Add more achievement-focused detail; the extracted resume text is quite short.")
    if not re.search(r"\b\d+(?:\.\d+)?%|\b\d+[kKmM+]\b", resume_text):
        recommendations.append("Quantify impact with metrics such as time saved, accuracy, scale, or revenue.")
    if not recommendations:
        recommendations.append("Tailor your strongest achievements to the role's first three requirements.")

    return {
        "predicted_role": classification.role,
        "role_confidence": classification.confidence,
        "match_score": round(match_score * 100, 1),
        "text_similarity": round(text_similarity * 100, 1),
        "skill_coverage": round(skill_coverage * 100, 1) if skill_coverage is not None else None,
        "resume_skills": resume_skills,
        "requested_skills": requested_skills,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "matched_keywords": matched_terms,
        "recommendations": recommendations,
    }
