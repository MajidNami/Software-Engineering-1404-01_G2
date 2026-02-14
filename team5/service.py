from .models import UserOfflineFeed, Place, RecommendationLog, Interaction


class RecommendationService:
    def get_recommendations(self, user, context_data):
        # 1. Context Analysis
        is_auth = user.is_authenticated

        # 2. Candidate Generation (Phase 6 Logic)
        if is_auth and hasattr(user, 'cluster'):
            try:
                feed = UserOfflineFeed.objects.get(cluster=user.cluster)
                candidates = feed.recommended_places
            except UserOfflineFeed.DoesNotExist:
                candidates = self._get_default_candidates()
        else:
            # Guest logic based on popular places nearby (Phase 3)
            candidates = self._get_default_candidates()

        # 3. Filtering, Ranking, and Explaining would follow here
        # Log the result for A/B Testing (Phase 5)
        return candidates

    def _get_default_candidates(self):
        return Place.objects.order_by('-total_score')[:20]