import json
from utils.hf_key import CLIENT

class CommentSummarizer:
    def __init__(self, model="openai/gpt-oss-120b"):
        self.role = """
            You are an AI text summarizer for Persian content. 
            You read a list of comments and ratings about a media (image, video, etc.) 
            and generate a concise natural-language summary in Persian. 
            
            Your summary should include:
            1. Overall sentiment (positive, neutral, negative)
            2. Why people liked it (features praised)
            3. Why people disliked it (features criticized)

            Return the output strictly as a JSON dictionary in the format:
            {
                "overall_sentiment": "مثبت",
                "why_liked": "Persian text summary",
                "why_disliked": "Persian text summary",
            }
        """
        self.model = model

    def summarize(self, comments, ratings):
        """
        comments: list of strings (Persian comments)
        ratings: list of integers/floats (e.g., 1-5)
        """
        combined_text = "نظرات کاربران و امتیازات آنها:\n"
        for i, comment in enumerate(comments):
            rating = ratings[i] if i < len(ratings) else "بدون امتیاز"
            combined_text += f"{i+1}. ({rating}) {comment}\n"

        completion = CLIENT.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.role},
                {"role": "user", "content": combined_text},
            ],
        )

        raw_response = completion.choices[0].message["content"]

        try:
            summary_dict = json.loads(raw_response)
        except json.JSONDecodeError:
            summary_dict = {
                "overall_sentiment": None,
                "why_liked": "",
                "why_disliked": "",
            }

        return summary_dict
