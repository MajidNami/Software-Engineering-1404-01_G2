from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from surprise import Dataset, Reader, SVD


class NotTrainedYetException(Exception):
    pass


@dataclass
class _PredictionView:
    est: float


class RecommenderModel:
    def __init__(self, rating_scale: tuple[float, float] = (0, 5)):
        self.rating_scale = rating_scale
        self.algo = SVD(random_state=42)
        self.is_trained = False
        self.items: set[str] = set()
        self.user_item_rating_matrix = pd.DataFrame()
        self._seen_items_by_user: dict[str, set[str]] = {}

    def train(self, rows: list[tuple[str, str, float]]) -> None:
        if not rows:
            raise ValueError("rows must not be empty")

        df = pd.DataFrame(rows, columns=["user_id", "item_id", "rating"])
        df["user_id"] = df["user_id"].astype(str)
        df["item_id"] = df["item_id"].astype(str)
        df["rating"] = df["rating"].astype(float)

        reader = Reader(rating_scale=self.rating_scale)
        dataset = Dataset.load_from_df(df[["user_id", "item_id", "rating"]], reader)
        trainset = dataset.build_full_trainset()
        self.algo.fit(trainset)

        self.items = set(df["item_id"].unique().tolist())
        self.user_item_rating_matrix = df.pivot_table(
            index="user_id",
            columns="item_id",
            values="rating",
            aggfunc="mean",
        )
        self._seen_items_by_user = {
            user_id: set(group["item_id"].tolist())
            for user_id, group in df.groupby("user_id")
        }
        self.is_trained = True

    def recommend(
        self,
        user_id: str,
        *,
        top_n: int = 10,
        show_already_seen_items: bool = False,
    ) -> list[tuple[str, float]]:
        if not self.is_trained:
            raise NotTrainedYetException("Model has not been trained yet")

        user_key = str(user_id).strip()
        seen = self._seen_items_by_user.get(user_key, set())
        candidates = self.items if show_already_seen_items else [item for item in self.items if item not in seen]
        if not candidates:
            return []

        scored = []
        for item_id in candidates:
            pred = self.algo.predict(user_key, item_id)
            scored.append((str(item_id), float(pred.est)))
        scored.sort(key=lambda entry: entry[1], reverse=True)
        return scored[: max(1, int(top_n))]

    def predict_rating(self, user_id: str, item_id: str) -> _PredictionView:
        if not self.is_trained:
            raise NotTrainedYetException("Model has not been trained yet")
        pred = self.algo.predict(str(user_id).strip(), str(item_id).strip())
        return _PredictionView(est=float(pred.est))
