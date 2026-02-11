try:
    from shekar import SentimentClassifier
except ImportError:  # pragma: no cover - optional dependency fallback
    SentimentClassifier = None

class TextSentiment:
    def __init__(self):
        self.classifier = SentimentClassifier() if SentimentClassifier is not None else None

    def sentiment(self, text):
        if self.classifier is None:
            # Neutral fallback when sentiment package is unavailable.
            return 1.0
        result = self.classifier(text)
        sentiment = result[1]
        if result[0] == "negative":
            sentiment = -sentiment

        return sentiment