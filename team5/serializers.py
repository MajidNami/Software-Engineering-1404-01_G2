class Team5Serializer:
    """Handles data transformation for Team5 responses."""

    @staticmethod
    def serialize_user(user):
        return {
            "userId": str(user.id),
            "email": user.email,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "age": getattr(user, 'age', None),
            "dateJoined": user.date_joined.isoformat() if user.date_joined else None,
        }

    @staticmethod
    def serialize_nearest(items, resolved, client_ip, limit, user_id):
        city = resolved["city"]
        return {
            "kind": "nearest",
            "title": "your nearest",
            "source": resolved["source"],
            "userId": user_id,
            "clientIp": client_ip,
            "cityId": city["cityId"],
            "cityName": city["cityName"],
            "limit": limit,
            "count": len(items),
            "items": items,
        }

    @staticmethod
    def serialize_personalized(items, user_id, source, limit):
        # Filter items based on match reason
        direct = [i for i in items if i.get("matchReason") == "high_user_rating"]
        similar = [i for i in items if i.get("matchReason") != "high_user_rating"]

        return {
            "kind": "personalized",
            "source": source,
            "userId": user_id,
            "limit": limit,
            "count": len(items),
            "items": items,
            "highRatedItems": direct,
            "similarItems": similar,
        }