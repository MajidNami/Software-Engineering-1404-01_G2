import json
from utils.hf_key import CLIENT

class CommentClassifier:
    def __init__(self, model="openai/gpt-oss-120b"):
        self.text_id2label = {
            0: "clean",
            1: "spam",
            2: "hate",
            3: "sexual",
            4: "violent",
            5: "insult",
        }

        self.role = """
            You are an AI text classifier for Persian content. 
            Your job is to detect whether a sentence belongs to the following categories: clean, spam, hate, sexual, violent, insult. 
            For each class, return a confidence score between 0 and 1. 
            Return the output strictly as a JSON dictionary in the format:
            {"clean": 0.0, "spam": 0.0, "hate": 0.0, "sexual": 0.0, "violent": 0.0, "insult": 0.0}
            """
        
        self.model = model

    def predict(self, text):
        completion = CLIENT.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.role},
                {"role": "user", "content": text},
            ],
        )

        raw_response = completion.choices[0].message.content
        
        try:
            confidence_dict = json.loads(raw_response)
        except json.JSONDecodeError:
            confidence_dict = {label: None for label in self.text_id2label.values()}
        
        return confidence_dict