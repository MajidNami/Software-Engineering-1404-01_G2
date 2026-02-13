import os
import json
import google.generativeai as genai

api_key = "AIzaSyDj6veF4073Tyz16phGyD7Ckp183jAIcpg"
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_ai_metadata_for_place(place_id, wiki_summary, wiki_tags):
    prompt = f"""
    You are an AI Travel Classifier for Iran tourism.
    Place ID/Name: {place_id}
    Summary: {wiki_summary}
    Tags: {wiki_tags}

    Task: Classify this place by choosing EXACTLY ONE dominant category for each field.
    - travel_style: ONE of [SOLO, COUPLE, FAMILY, FRIENDS, BUSINESS]
    - budget_level: ONE of [ECONOMY, MODERATE, LUXURY]
    - season: ONE of [SPRING, SUMMER, FALL, WINTER]
    - region_id: English string (e.g. "isfahan", "tehran")
    - region_name: Persian string (e.g. "اصفهان", "تهران")
    - duration: Integer (estimated hours/days to visit, e.g. 2)
    - ai_reason: One short attractive Persian sentence explaining why visit here.

    Respond ONLY with exact JSON format:
    {{
      "region_id": "isfahan",
      "region_name": "اصفهان",
      "budget_level": "MODERATE",
      "travel_style": "FAMILY",
      "duration": 3,
      "season": "SPRING",
      "ai_reason": "کاخی باشکوه با معماری بی‌نظیر که در فصل بهار تجربه‌ای عالی برای خانواده‌هاست."
    }}
    """

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
        return json.loads(text)
    except Exception:
        return {
            "region_id": "unknown",
            "region_name": "نامشخص",
            "budget_level": "MODERATE",
            "travel_style": "FAMILY",
            "duration": 2,
            "season": "SPRING",
            "ai_reason": "یک مقصد جذاب برای سفر."
        }