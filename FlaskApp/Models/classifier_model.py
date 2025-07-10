import os
import json
from pathlib import Path
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
import torch

# Define directories
DATA_DIR = "data/cleaned_resumes/"
MODEL_DIR = "Models/classifier_model/"
os.makedirs(MODEL_DIR, exist_ok=True)

# Load and prepare data
def load_data():
    data = {"text": [], "label": []}
    label_map = {}  # To map job roles to integers
    for i, file_path in enumerate(Path(DATA_DIR).glob("cleaned_*.txt")):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Extract label (assume it's in the filename or add a labels file)
        job_role = file_path.name.split("_")[1]  # Example: cleaned_SoftwareEngineer_resume.txt
        if job_role not in label_map:
            label_map[job_role] = len(label_map)
        data["text"].append(content)
        data["label"].append(label_map[job_role])
    return Dataset.from_dict(data), label_map

# Load and tokenize data
dataset, label_map = load_data()

# Initialize model and tokenizer (after label_map is defined)
model_name = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=len(label_map))

# Tokenize dataset
def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=512)

tokenized_dataset = dataset.map(tokenize_function, batched=True)

# Split dataset
train_test_split = tokenized_dataset.train_test_split(test_size=0.2)
train_dataset = train_test_split["train"]
eval_dataset = train_test_split["test"]

# Define training arguments
training_args = TrainingArguments(
    output_dir=MODEL_DIR,
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    push_to_hub=False,
)

# Define Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
)

# Train and save model
print("Training classifier model...")
trainer.train()
model.save_pretrained(MODEL_DIR)
tokenizer.save_pretrained(MODEL_DIR)
with open(os.path.join(MODEL_DIR, "label_map.json"), "w") as f:
    json.dump(label_map, f)
print(f"Model saved to {MODEL_DIR}")