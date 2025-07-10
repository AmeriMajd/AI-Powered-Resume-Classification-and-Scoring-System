import os
from sentence_transformers import CrossEncoder, InputExample
from torch.utils.data import DataLoader
import torch

# Define directories
DATA_DIR = "data/cleaned_resumes/"
MODEL_DIR = "models/cross_encoder_model/"
os.makedirs(MODEL_DIR, exist_ok=True)

# Prepare training data (example pairs)
def load_training_data():
    # Synthetic dataset: pairs of (resume, job_description, score)
    train_examples = [
        InputExample(texts=["Software Engineer resume with Python experience...", "Job for Python Developer"], label=0.9),
        InputExample(texts=["Data Scientist resume with ML skills...", "Job for Data Analyst"], label=0.6),
        InputExample(texts=["Marketing Manager resume...", "Job for Software Engineer"], label=0.2),
        # Add more pairs from your data
    ]
    return train_examples

# Initialize and train Cross-Encoder
model_name = "cross-encoder/ms-marco-MiniLM-L-12-v2"
model = CrossEncoder(model_name, num_labels=1)

# Load and train
train_examples = load_training_data()
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=8)

# Fine-tune the model
model.fit(
    train_dataloader=train_dataloader,
    epochs=3,
    warmup_steps=100,
    output_path=MODEL_DIR,
)

print(f"Cross-Encoder model saved to {MODEL_DIR}")