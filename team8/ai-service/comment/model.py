import json
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class CommentClassifier:
    def __init__(self, model_name="HooshvareLab/bert-base-parsbert-uncasedو", model_path="comment_model.pt"):
        self.text_id2label = {
            0: "clean",
            1: "spam",
            2: "obscene",
            3: "spamobscene",
            4: "hate",
            5: "hateobscene"
        }

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=6).to(self.device)
        
        if torch.cuda.is_available():
            self.model.load_state_dict(torch.load(model_path))
        else:
            self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        self.model.eval()
    @torch.no_grad()
    def predict(self, comment):
        inputs = self.tokenizer(comment, return_tensors="pt", truncation=True, padding='max_length', max_length=128).to(self.device)
        logits = self.model(**inputs)
        return {"prediction":torch.argmax(logits['logits'], dim=1).item()}
