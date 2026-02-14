import os
import requests
from typing import List
import re
from collections import Counter

class FreeAIService:
    """سرویس تولید خلاصه و تگ با Hugging Face"""
    def __init__(self):
        # کلید API از متغیر محیطی خوانده می‌شود تا در ریپو/کد هاردکد نشود.
        self.api_key = os.environ.get("HF_API_KEY")
        self.base_url = "https://router.huggingface.co/hf-inference/models/csebuetnlp/mT5_multilingual_XLSum"

    def _call_api(self, text: str) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        prompt = (
            "Please summarize the given text in Persian, "
            "keeping the main points and important details, and removing any unnecessary information:\n\n"
            f"{text}"
        )
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 150,
                "min_length": 40,
                "do_sample": False,
                "num_beams": 4,
                "early_stopping": True
            }
        }
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            if response.status_code != 200:
                print("HF Error:", response.text)
                return None
            data = response.json()
            if isinstance(data, list) and 'summary_text' in data[0]:
                return data[0]['summary_text']
            elif isinstance(data, dict) and 'summary_text' in data:
                return data['summary_text']
            else:
                return None
        except Exception as e:
            print("HF Exception:", e)
            return None

    def generate_summary(self, text: str) -> str:
        if len(text) < 50:
            sentences = [s.strip() for s in text.split(".") if s.strip()]
            return ". ".join(sentences[:2]) + "..." if len(sentences) > 1 else text
        # برای جلوگیری از کندی/خطای سرویس، متن ورودی به طول محدودتری برش داده می‌شود.
        result = self._call_api(text[:2000])
        if result:
            return result.strip()
        sentences = [s.strip() for s in text.split(".") if s.strip()]
        return ". ".join(sentences[:3]) + "..." if len(sentences) > 2 else text[:200] + "..."

    def extract_tags(self, text: str, title: str = "") -> List[str]:
        combined = title + " " + text
        words = re.findall(r'[\u0600-\u06FF]{3,}', combined)
        stopwords = [
            # افعال ساده و رایج
            "است", "بوده","بود", "شود","کنید","اید","شد", "شده", "می‌کند", "می‌شود", "دارند", "داشت", "داشتند", "کند", "کنند", "کرد", "کرده", "خواهد", "باشد",
            "می‌باشد", "شاید", "خواهد شد", "می‌کرد", "می‌کردند",
            
            # حروف اضافه و ربط
            "و", "یا", "به", "از", "در", "با", "برای", "تا", "که", "اما", "اگر", "چون", "نیز", "ولی", "هر", "این", "آن", "آنکه", "اگرچه","هایی","دیگر",
            
            # پسوندها و پیشوندهای رایج
            "ها", "های", "ترین", "تر", "ی", "ای", "ایم", "اند", "تان", "شان", "ام", "ات", "اش","هایی"
            
            # ضمایر و کلمات کوتاه
            "من", "تو", "او", "ما", "شما", "آنها", "خود", "هم", "اینها", "کسی", "هیچ", "همه", "چنین", "چطور", "چه", "چرا", "چقدر",
            
            # کلمات کم‌ارزش دیگر
            "بر", "را", "همچنین", "بعد", "قبل", "چیز", "مثلا", "مثل", "یکی", "بسیار", "کم", "زیاد","سوال","سال"
        ]
        words = [w for w in words if w not in stopwords]
        counter = Counter(words)
        return [w for w, _ in counter.most_common(15)]