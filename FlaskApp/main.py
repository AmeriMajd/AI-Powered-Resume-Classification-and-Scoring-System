from flask import Flask, request, jsonify
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from sentence_transformers import CrossEncoder
import PyPDF2


app = Flask(__name__)

# Load models
classifier_dir = "models/classifier_model/"
classifier = pipeline("text-classification", model=classifier_dir)
tokenizer = AutoTokenizer.from_pretrained(classifier_dir)
model = AutoModelForSequenceClassification.from_pretrained(classifier_dir)
cross_encoder = CrossEncoder("models/cross_encoder_model/")

def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

@app.route("/classify", methods=["POST"])
def classify_resume():
    if "resume" not in request.files:
        return jsonify({"error": "No resume uploaded"}), 400
    resume_file = request.files["resume"]
    resume_text = extract_text_from_pdf(resume_file)
    result = classifier(resume_text)
    return jsonify({"job_role": result[0]["label"], "confidence": result[0]["score"]})

@app.route("/score", methods=["POST"])
def score_resume():
    if "resume" not in request.files or "job_desc" not in request.form:
        return jsonify({"error": "Missing resume or job description"}), 400
    resume_file = request.files["resume"]
    job_desc = request.form["job_desc"]
    resume_text = extract_text_from_pdf(resume_file)
    score = cross_encoder.predict([(resume_text, job_desc)])[0]
    return jsonify({"score": float(score)})

if __name__ == "__main__":
    app.run(debug=True)