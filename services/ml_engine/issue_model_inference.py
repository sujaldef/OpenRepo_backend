import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../ml_training/saved_models")
)

MODEL_PATH = os.path.join(BASE_DIR, "issue_model.pt")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class IssueModel:

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
        self.model = AutoModelForSequenceClassification.from_pretrained(
            "microsoft/codebert-base",
            num_labels=2
        )

        self.model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        self.model.to(DEVICE)
        self.model.eval()

    def predict(self, code_text: str):

        inputs = self.tokenizer(
            code_text,
            truncation=True,
            padding="max_length",
            max_length=256,
            return_tensors="pt"
        )

        inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=1)

        predicted_class = torch.argmax(probs, dim=1).item()
        confidence = probs[0][predicted_class].item()

        return {
            "label": predicted_class,
            "confidence": round(float(confidence), 4)
        }