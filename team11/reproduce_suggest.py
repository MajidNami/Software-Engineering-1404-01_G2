
def _generate_destination_suggestions_mock(season, budget_level, travel_style, interests, region=None):
    destinations_db = [
        {
            "city": "اصفهان",
            "province": "اصفهان",
            "region": "CENTRAL",
            "best_seasons": ["spring", "fall"],
            "budget_min": "ECONOMY",
            "categories": ["تاریخی", "فرهنگی", "معماری"],
            "suitable_for": ["COUPLE", "FAMILY", "FRIENDS"],
            "highlights": ["میدان نقش جهان", "سی‌وسه‌پل", "مسجد شیخ لطف‌الله"],
            "description": "اصفهان نصف جهان...",
        },
        {
            "city": "شیراز",
            "province": "فارس",
            "region": "SOUTH",
            "best_seasons": ["spring", "winter"],
            "budget_min": "ECONOMY",
            "categories": ["تاریخی", "فرهنگی", "باغ"],
            "suitable_for": ["COUPLE", "FAMILY", "FRIENDS", "SOLO"],
            "highlights": ["تخت جمشید", "حافظیه", "باغ ارم"],
            "description": "شیراز شهر شعر...",
        },
        {
            "city": "مشهد",
            "province": "خراسان رضوی",
            "region": "EAST",
            "best_seasons": ["spring", "summer", "fall"],
            "budget_min": "ECONOMY",
            "categories": ["مذهبی", "زیارتی", "فرهنگی"],
            "suitable_for": ["FAMILY", "COUPLE", "FRIENDS"],
            "highlights": ["حرم امام رضا", "بازار رضا"],
            "description": "مشهد شهر مقدس...",
        },
        {
            "city": "تهران",
            "province": "تهران",
            "region": "CENTRAL",
            "best_seasons": ["spring", "fall"],
            "budget_min": "MEDIUM",
            "categories": ["شهری", "فرهنگی", "خرید"],
            "suitable_for": ["BUSINESS", "SOLO", "FRIENDS"],
            "highlights": ["برج میلاد", "کاخ گلستان"],
            "description": "تهران پایتخت...",
        },
        {
            "city": "رامسر",
            "province": "مازندران",
            "region": "NORTH",
            "best_seasons": ["summer", "spring"],
            "budget_min": "MEDIUM",
            "categories": ["طبیعت", "ساحل", "خانوادگی"],
            "suitable_for": ["FAMILY", "COUPLE"],
            "highlights": ["جنگل‌های شمال", "ساحل خزر"],
            "description": "رامسر جزیره سبز...",
        },
        {
            "city": "یزد",
            "province": "یزد",
            "region": "CENTRAL",
            "best_seasons": ["spring", "fall", "winter"],
            "budget_min": "ECONOMY",
            "categories": ["تاریخی", "معماری", "کویری"],
            "suitable_for": ["COUPLE", "FRIENDS", "SOLO"],
            "highlights": ["شهر بادگیرها", "آتشکده"],
            "description": "یزد شهر کویری...",
        }
    ]

    scored_destinations = []

    for dest in destinations_db:
        score = 0
        reasons = []
        
        # Region Filter (Binary)
        if region and dest.get("region") != region:
             continue

        # 1. Season (+30)
        if season in dest["best_seasons"]:
            score += 30
            reasons.append(f"Season match")

        # 2. Style (+25)
        if travel_style in dest["suitable_for"]:
            score += 25
            reasons.append(f"Style match")

        # 3. Interests (+15 each)
        matches = 0
        for interest in interests:
            if interest in dest["categories"]:
                matches += 1
                score += 15
        
        # 4. Budget
        # ... simplified for mock
        score += 10 # Base

        if score > 0:
            scored_destinations.append({
                "city": dest["city"],
                "score": score,
                "region": dest["region"]
            })

    scored_destinations.sort(key=lambda x: x["score"], reverse=True)
    return scored_destinations

# Test Case
print("Winter, South:")
print(_generate_destination_suggestions_mock("winter", "MEDIUM", "FAMILY", [], "SOUTH"))

print("\nSummer, North:")
print(_generate_destination_suggestions_mock("summer", "MEDIUM", "FAMILY", [], "NORTH"))
