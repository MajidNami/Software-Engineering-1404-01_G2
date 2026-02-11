"""Recommendation scoring for popular and personalized feeds."""

from collections import defaultdict
from uuid import UUID

from .contracts import (
    DEFAULT_LIMIT,
    PERSONALIZED_MIN_USER_RATE,
    POPULAR_MIN_OVERALL_RATE,
    POPULAR_MIN_VOTES,
    MediaRecord,
    PlaceRecord,
)
from .data_provider import DataProvider
from team5.models import Team5MediaRating
<<<<<<< Updated upstream
=======
try:
    from .ml.recommender_model import RecommenderModel
    from team5.exceptions.not_trained_yet_exception import NotTrainedYetException
except Exception:  # pragma: no cover - optional ML dependencies
    RecommenderModel = None

    class NotTrainedYetException(Exception):
        pass
>>>>>>> Stashed changes


class RecommendationService:
    def __init__(
        self,
        provider: DataProvider,
        *,
        popular_min_overall_rate: float = POPULAR_MIN_OVERALL_RATE,
        popular_min_votes: int = POPULAR_MIN_VOTES,
        personalized_min_user_rate: float = PERSONALIZED_MIN_USER_RATE,
    ):
        self.provider = provider
        self.popular_min_overall_rate = popular_min_overall_rate
        self.popular_min_votes = popular_min_votes
        self.personalized_min_user_rate = personalized_min_user_rate
<<<<<<< Updated upstream
=======
        self._ml_enabled = RecommenderModel is not None
        self.personalized_place_recommender_model = RecommenderModel((0, 5)) if self._ml_enabled else None
        self.personalized_media_recommender_model = RecommenderModel((0, 5)) if self._ml_enabled else None
        self._models_ready = False
>>>>>>> Stashed changes

    def get_popular(
        self,
        limit: int = DEFAULT_LIMIT,
        excluded_media_ids: set[str] | None = None,
    ) -> list[MediaRecord]:
        media = [dict(item) for item in self.provider.get_media()]
        excluded = excluded_media_ids or set()
        filtered = [
            item
            for item in media
            if item["mediaId"] not in excluded
            and float(item["overallRate"]) >= self.popular_min_overall_rate
            and int(item["ratingsCount"]) >= self.popular_min_votes
        ]
        filtered.sort(key=lambda item: (float(item["overallRate"]), int(item["ratingsCount"])), reverse=True)
        return filtered[:limit]

    def get_nearest_by_city(
        self,
        city_id: str,
        limit: int = DEFAULT_LIMIT,
<<<<<<< Updated upstream
=======
        user_id: str | None = None,
>>>>>>> Stashed changes
        excluded_media_ids: set[str] | None = None,
    ) -> list[MediaRecord]:
        place_by_id = {place["placeId"]: place for place in self.provider.get_all_places()}
        items: list[dict] = []
        excluded = excluded_media_ids or set()
<<<<<<< Updated upstream
=======
        user_key = str(user_id).strip() if user_id else ""
>>>>>>> Stashed changes

        for media in self.provider.get_media():
            if media["mediaId"] in excluded:
                continue
            place = place_by_id.get(media["placeId"])
            if not place or place["cityId"] != city_id:
                continue
            item = dict(media)
            item["matchReason"] = "your_nearest"
            items.append(item)

        # Re-rank nearest items by ML prediction score when user id is available.
        if items and user_key:
            ml_scores = self._get_ml_prediction_scores_for_media(
                user_id=user_key,
                media_ids=[item["mediaId"] for item in items],
            )
            for item in items:
                if item["mediaId"] in ml_scores:
                    item["mlScore"] = round(float(ml_scores[item["mediaId"]]), 3)
            items.sort(key=lambda item: (float(item["overallRate"]), int(item["ratingsCount"])), reverse=True)
            items.sort(key=lambda item: float(item.get("mlScore", -1)), reverse=True)
        else:
            items.sort(key=lambda item: (float(item["overallRate"]), int(item["ratingsCount"])), reverse=True)
        return items[:limit]

    def get_personalized(
        self,
        user_id: str,
        limit: int = DEFAULT_LIMIT,
        excluded_media_ids: set[str] | None = None,
    ) -> list[MediaRecord]:
        media = [dict(item) for item in self.provider.get_media()]
        media_by_id = {item["mediaId"]: item for item in media}
        scored: list[tuple[float, float, int, dict]] = []
        ratings_by_media = self._get_db_ratings_by_media(user_id)
<<<<<<< Updated upstream
        blocked = excluded_media_ids or set()

        for item in media_by_id.values():
            if item["mediaId"] in blocked:
=======
        excluded = excluded_media_ids or set()
        if not ratings_by_media:
            return []

        for item in media_by_id.values():
            if item["mediaId"] in excluded:
>>>>>>> Stashed changes
                continue
            user_rate = ratings_by_media.get(item["mediaId"])
            if user_rate is None or user_rate < self.personalized_min_user_rate:
                continue
            item["userRate"] = user_rate
            item["matchReason"] = "high_user_rating"
            scored.append((user_rate, float(item["overallRate"]), int(item["ratingsCount"]), item))

        scored.sort(key=lambda data: (data[0], data[1], data[2]), reverse=True)
        base_limit = max(1, int(limit * 0.6))
        base_items = [entry[3] for entry in scored[:base_limit]]

        similar_items = self.get_similar_items(
            user_id=user_id,
            based_on_items=base_items,
<<<<<<< Updated upstream
            excluded_media_ids={item["mediaId"] for item in base_items}.union(blocked),
=======
            excluded_media_ids={item["mediaId"] for item in base_items}.union(excluded),
>>>>>>> Stashed changes
            limit=max(1, min(limit, 10)),
        )

        ml_items = self._get_ml_personalized_items(
            user_id=user_id,
            media_by_id=media_by_id,
            excluded_media_ids={item["mediaId"] for item in base_items}.union(excluded),
            limit=max(1, min(limit - len(base_items), limit)),
        )

        merged = list(base_items)
        for item in ml_items:
            if len(merged) >= limit:
                break
            merged.append(item)
        for item in similar_items:
            if len(merged) >= limit:
                break
            merged.append(item)
        return merged[:limit]

    def get_user_interest_distribution(self, user_id: str) -> dict:
        place_by_id = {place["placeId"]: place for place in self.provider.get_all_places()}
        city_counts: dict[str, int] = defaultdict(int)
        place_counts: dict[str, int] = defaultdict(int)
        ratings_by_media = self._get_db_ratings_by_media(user_id)
        if not ratings_by_media:
            return {"userId": user_id, "cityInterests": [], "placeInterests": []}

        for item in self.provider.get_media():
            user_rate = ratings_by_media.get(item["mediaId"])
            if user_rate is None or user_rate < self.personalized_min_user_rate:
                continue
            place_id = item["placeId"]
            place_counts[place_id] += 1
            place = place_by_id.get(place_id)
            if place:
                city_counts[place["cityId"]] += 1

        return {
            "userId": user_id,
            "cityInterests": [
                {"cityId": city_id, "count": count}
                for city_id, count in sorted(city_counts.items(), key=lambda item: item[1], reverse=True)
            ],
            "placeInterests": [
                {"placeId": place_id, "count": count}
                for place_id, count in sorted(place_counts.items(), key=lambda item: item[1], reverse=True)
            ],
        }

    def get_place_lookup(self) -> dict[str, PlaceRecord]:
        return {place["placeId"]: place for place in self.provider.get_all_places()}

    def get_user_ratings(self, user_id: str) -> list[dict]:
        media_by_id = {item["mediaId"]: item for item in self.provider.get_media()}
        user_uuid = _parse_uuid(user_id)
        if user_uuid is None:
            return []

        ratings = Team5MediaRating.objects.filter(user_id=user_uuid).order_by("-rate", "-updated_at")
        return [
            {
                "userId": str(r.user_id),
                "userEmail": r.user_email,
                "mediaId": r.media_id,
                "rate": float(r.rate),
                "liked": bool(r.liked),
                "media": media_by_id.get(r.media_id),
                "updatedAt": r.updated_at.isoformat(),
            }
            for r in ratings
        ]

    def get_media_feed(self, user_id: str | None = None) -> dict:
        items = [dict(item) for item in self.provider.get_media()]

        rated_high: list[dict] = []
        rated_low: list[dict] = []
        user_ratings_map = self._get_db_ratings_by_media(user_id) if user_id else {}

        for item in items:
            user_rate = None
            if user_id:
                user_rate = user_ratings_map.get(item["mediaId"])
            if user_rate is not None:
                item["userRate"] = float(user_rate)
                item["liked"] = float(user_rate) >= self.personalized_min_user_rate
                if item["liked"]:
                    rated_high.append(item)
                else:
                    rated_low.append(item)

        items.sort(key=lambda data: (float(data["overallRate"]), int(data["ratingsCount"])), reverse=True)
        rated_high.sort(key=lambda data: float(data["userRate"]), reverse=True)
        rated_low.sort(key=lambda data: float(data["userRate"]))

        return {
            "userId": user_id,
            "count": len(items),
            "items": items,
            "ratedHigh": rated_high,
            "ratedLow": rated_low,
        }

    def get_similar_items(
        self,
        *,
        user_id: str,
        based_on_items: list[dict],
        excluded_media_ids: set[str],
        limit: int,
    ) -> list[dict]:
        if not based_on_items:
            return []

        all_items = [dict(item) for item in self.provider.get_media()]
        place_by_id = {place["placeId"]: place for place in self.provider.get_all_places()}
        scores: dict[str, float] = defaultdict(float)
        reasons: dict[str, str] = {}

        seed_keywords = set()
        seed_city_ids = set()
        for item in based_on_items:
            seed_keywords |= _extract_keywords(item["title"] + " " + item.get("caption", ""))
            place = place_by_id.get(item["placeId"])
            if place:
                seed_city_ids.add(place["cityId"])

        for candidate in all_items:
            media_id = candidate["mediaId"]
            if media_id in excluded_media_ids:
                continue
            place = place_by_id.get(candidate["placeId"])
            candidate_keywords = _extract_keywords(candidate["title"] + " " + candidate.get("caption", ""))
            overlap = seed_keywords.intersection(candidate_keywords)
            if overlap:
                scores[media_id] += 2.5
                reasons[media_id] = "similar_topic"
            if place and place["cityId"] in seed_city_ids:
                scores[media_id] += 1.5
                reasons[media_id] = reasons.get(media_id, "same_city")
            scores[media_id] += float(candidate.get("overallRate", 0)) / 10.0

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]
        media_by_id = {item["mediaId"]: item for item in all_items}
        output = []
        for media_id, _ in ranked:
            item = media_by_id[media_id]
            item["matchReason"] = reasons.get(media_id, "similar")
            output.append(item)
        return output

    def _get_db_ratings_by_media(self, user_id: str) -> dict[str, float]:
        user_uuid = _parse_uuid(user_id)
        if user_uuid is None:
            return {}
        return {
            item.media_id: float(item.rate)
            for item in Team5MediaRating.objects.filter(user_id=user_uuid)
        }
<<<<<<< Updated upstream
=======
    
    def train(self):
        if not self._ml_enabled:
            self._models_ready = False
            return False
        self._train_personalized_place_recommender_model()
        self._train_personalized_media_recommender_model()
        return self._models_ready

    def _train_personalized_place_recommender_model(self):
        if self.personalized_place_recommender_model is None:
            return
        try:
            user_place_ratings = self._to_training_triples(
                rows=self.provider.get_all_place_ratings(),
                user_key="userId",
                item_key="placeId",
                rating_key="rate",
            )
            if user_place_ratings:
                self.personalized_place_recommender_model.train(user_place_ratings)
        except Exception:
            # Place model is optional for now; keep service available.
            return

    def _train_personalized_media_recommender_model(self):
        if self.personalized_media_recommender_model is None:
            self._models_ready = False
            return
        user_media_ratings = self._to_training_triples(
            rows=self.provider.get_all_media_ratings(),
            user_key="userId",
            item_key="mediaId",
            rating_key="rate",
        )
        if user_media_ratings:
            self.personalized_media_recommender_model.train(user_media_ratings)
            self._models_ready = True
        else:
            self._models_ready = False

    def _ensure_models_ready(self) -> bool:
        if not self._ml_enabled or self.personalized_media_recommender_model is None:
            return False
        if self._models_ready:
            return True
        try:
            return bool(self.train())
        except Exception:
            self._models_ready = False
            return False

    def _get_ml_personalized_items(
        self,
        *,
        user_id: str,
        media_by_id: dict[str, dict],
        excluded_media_ids: set[str],
        limit: int,
    ) -> list[dict]:
        if limit <= 0:
            return []
        user_key = str(user_id).strip()
        if not user_key or not self._ensure_models_ready():
            return []

        try:
            predictions = self.personalized_media_recommender_model.recommend(
                user_key,
                top_n=max(limit * 3, limit),
                show_already_seen_items=False,
            )
        except NotTrainedYetException:
            return []
        except Exception:
            return []

        output: list[dict] = []
        for media_id, pred_score in predictions:
            media_key = str(media_id)
            if media_key in excluded_media_ids:
                continue
            media = media_by_id.get(media_key)
            if not media:
                continue
            item = dict(media)
            item["matchReason"] = "ml_personalized"
            item["mlScore"] = round(float(pred_score), 3)
            output.append(item)
            if len(output) >= limit:
                break
        return output

    def _get_ml_prediction_scores_for_media(
        self,
        *,
        user_id: str,
        media_ids: list[str],
    ) -> dict[str, float]:
        if not media_ids:
            return {}
        if not user_id or not self._ensure_models_ready():
            return {}
        if self.personalized_media_recommender_model is None:
            return {}

        scores: dict[str, float] = {}
        for media_id in media_ids:
            try:
                prediction = self.personalized_media_recommender_model.predict_rating(user_id, media_id)
                scores[media_id] = float(prediction.est)
            except NotTrainedYetException:
                return {}
            except Exception:
                continue
        return scores

    def _to_training_triples(
        self,
        *,
        rows: list[dict],
        user_key: str,
        item_key: str,
        rating_key: str,
    ) -> list[tuple[str, str, float]]:
        output: list[tuple[str, str, float]] = []
        for row in rows:
            user_id = str(row.get(user_key, "")).strip()
            item_id = str(row.get(item_key, "")).strip()
            if not user_id or not item_id:
                continue
            try:
                rating = float(row.get(rating_key))
            except (TypeError, ValueError):
                continue
            output.append((user_id, item_id, rating))
        return output

    def get_ml_status(self) -> dict:
        media_samples = 0
        place_samples = 0
        try:
            media_samples = len(self.provider.get_all_media_ratings())
        except Exception:
            media_samples = 0
        try:
            place_samples = len(self.provider.get_all_place_ratings())
        except Exception:
            place_samples = 0

        media_model_users = 0
        media_model_items = 0
        place_model_users = 0
        place_model_items = 0

        if self.personalized_media_recommender_model is not None:
            media_model_items = len(self.personalized_media_recommender_model.items)
            media_model_users = len(self.personalized_media_recommender_model.user_item_rating_matrix.index)
        if self.personalized_place_recommender_model is not None:
            place_model_items = len(self.personalized_place_recommender_model.items)
            place_model_users = len(self.personalized_place_recommender_model.user_item_rating_matrix.index)

        return {
            "mlEnabled": bool(self._ml_enabled),
            "modelsReady": bool(self._models_ready),
            "mediaRatingsSamples": media_samples,
            "placeRatingsSamples": place_samples,
            "mediaModelUsers": media_model_users,
            "mediaModelItems": media_model_items,
            "placeModelUsers": place_model_users,
            "placeModelItems": place_model_items,
        }
>>>>>>> Stashed changes


def _parse_uuid(value: str) -> UUID | None:
    try:
        return UUID(str(value))
    except (ValueError, TypeError):
        return None


def _extract_keywords(text: str) -> set[str]:
    text = text.lower()
    keywords = set()
    mapping = {
        "tower": ["tower", "برج"],
        "bridge": ["bridge", "پل"],
        "palace": ["palace", "کاخ"],
        "shrine": ["shrine", "حرم"],
        "square": ["square", "میدان"],
        "heritage": ["historical", "history", "ancient", "ruins", "historical site", "تاریخی"],
        "poetry": ["poetry", "verse", "hafez", "شعر"],
    }
    for canonical, tokens in mapping.items():
        if any(token in text for token in tokens):
            keywords.add(canonical)
    return keywords
