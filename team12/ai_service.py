import os
import json
import google.generativeai as genai

# Setup API Key
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Safety settings to avoid filtering Iranian tourism content
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# Use the latest stable model
model = genai.GenerativeModel('gemini-flash-latest', safety_settings=safety_settings)


def generate_ai_metadata_for_place(place_id, wiki_summary, wiki_tags):
    # Enhanced Expert Prompt
    prompt = f"""
    You are an Expert Iranian Tourism Consultant. 
    Input Data:
    - Place ID/Name: {place_id}
    - Provided Summary: {wiki_summary if wiki_summary else "No data provided"}
    - Provided Tags: {wiki_tags if wiki_tags else "No tags provided"}

    Instructions:
    1. If the 'Provided Summary' is incomplete, vague, or missing, use your extensive internal knowledge of Iranian landmarks and geography to provide accurate details.
    2. Analyze the landmark's real-world characteristics to determine the best match for:
       - travel_style: [SOLO, COUPLE, FAMILY, FRIENDS, BUSINESS]
       - budget_level: [ECONOMY, MODERATE, LUXURY]
       - season: [SPRING, SUMMER, FALL, WINTER] (Use FALL, not Autumn)
    3. region_id: Determine the city or province (lowercase English, e.g., 'fars', 'kerman').
    4. region_name: Persian name (e.g., 'فارس', 'کرمان').
    5. duration: Estimated hours/days (Integer) for a meaningful visit.
    6. ai_reason: Write a compelling, unique Persian sentence explaining why a traveler with the chosen style/budget would love this place.

    Output MUST be a valid JSON object only:
    {{
      "region_id": "string",
      "region_name": "string",
      "budget_level": "string",
      "travel_style": "string",
      "duration": integer,
      "season": "string",
      "ai_reason": "Persian string"
    }}
    """

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Clean potential markdown formatting
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        print(f"DEBUG: AI processed {place_id} successfully.", flush=True)
        return json.loads(text)

    except Exception as e:
        print(f"ERROR: AI Service failed for {place_id}: {str(e)}", flush=True)
        # Safe fallback values
        return {
            "region_id": "unknown",
            "region_name": "Unknown",
            "budget_level": "MODERATE",
            "travel_style": "FAMILY",
            "duration": 2,
            "season": "SPRING",
            "ai_reason": "A beautiful destination worth visiting."
        }