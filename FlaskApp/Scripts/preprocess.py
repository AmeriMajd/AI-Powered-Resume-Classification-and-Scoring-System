import os
import re
import spacy
from pathlib import Path

# Load spaCy model for NLP tasks
nlp = spacy.load("en_core_web_sm")

# Define directories
RAW_RESUME_DIR = "../FlaskApp/data/resumes/"
CLEANED_RESUME_DIR = "../FlaskApp/data/cleaned_resumes/"
os.makedirs(CLEANED_RESUME_DIR, exist_ok=True)


def clean_resume(text):
    """
    Remove personal information (e.g., names, emails, phone numbers) from resume text.
    """
    # Remove emails
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    # Remove phone numbers (e.g., (123) 456-7890, 123-456-7890)
    text = re.sub(r'\b(\(\d{3}\)\s?|\d{3}-)\d{3}-\d{4}\b', '[PHONE]', text)
    # Remove names (simple heuristic: capitalized words at the start)
    text = re.sub(r'^\s*[A-Z][a-z]+ [A-Z][a-z]+\s*', '[NAME]\n', text, flags=re.MULTILINE)
    return text


def extract_sections(text):
    """
    Extract key sections (e.g., skills, experience) using spaCy.
    Returns a dictionary with sections.
    """
    doc = nlp(text)
    sections = {"skills": [], "experience": [], "other": []}

    # Simple heuristic: Look for keywords to identify sections
    current_section = "other"
    for sent in doc.sents:
        sent_text = sent.text.lower()
        if "skills" in sent_text:
            current_section = "skills"
        elif "experience" in sent_text or "work history" in sent_text:
            current_section = "experience"
        sections[current_section].append(sent.text.strip())

    return sections

def preprocess_resumes():
    """
    Process all raw resumes, clean them, and extract sections.
    """
    for resume_file in Path(RAW_RESUME_DIR).glob("*.txt"):
        with open(resume_file, "r", encoding="utf-8") as f:
            raw_text = f.read()

        # Clean the resume
        cleaned_text = clean_resume(raw_text)

        # Extract sections
        sections = extract_sections(cleaned_text)

        # Save cleaned and structured data
        output_file = Path(CLEANED_RESUME_DIR) / f"cleaned_{resume_file.name}"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("=== Cleaned Resume ===\n")
            f.write(cleaned_text + "\n\n")
            f.write("=== Structured Sections ===\n")
            for section, content in sections.items():
                f.write(f"{section.upper()}:\n")
                f.write("\n".join(content) + "\n\n")
        print(f"Processed {resume_file.name} -> {output_file}")


if __name__ == "__main__":
    print("Starting preprocessing...")
    preprocess_resumes()