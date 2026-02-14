
import os
from pymongo import MongoClient
from django.conf import settings
from datetime import datetime, timedelta, timezone


def get_mongo_client():
    mongo_url = os.getenv(
        'TEAM11_MONGO_URL',
        'mongodb://team11_mongo:team11_mongo_pass@localhost:27018/team11_nosql?authSource=admin'
    )
    return MongoClient(mongo_url)


def get_mongo_db():
    client = get_mongo_client()
    db_name = os.getenv('TEAM11_MONGO_DB', 'team11_nosql')
    return client[db_name]


class MongoUserProfileService:

    def __init__(self):
        self.db = get_mongo_db()
        self.collection = self.db['user_semantic_profile']

    def get_user_profile(self, user_id):
        return self.collection.find_one({'user_id_ref': user_id})

    def save_user_profile(self, user_id, vector, interests):
        self.collection.update_one(
            {'user_id_ref': user_id},
            {
                '$set': {
                    'user_id_ref': user_id,
                    'semantic_vector': vector,
                    'explicit_interests': interests,
                    'last_updated': datetime.now(timezone.utc)
                }
            },
            upsert=True
        )


class MongoPlaceFeatureStore:

    def __init__(self):
        self.db = get_mongo_db()
        self.collection = self.db['place_feature_store']

    def get_place_features(self, place_id):
        return self.collection.find_one({'place_id': place_id})

    def search_similar_places(self, vector, limit=10):
        pass


class MongoAPICache:

    def __init__(self):
        self.db = get_mongo_db()
        self.collection = self.db['external_api_cache']

        # Create TTL Index for automatic expiration
        self.collection.create_index(
            'expires_at',
            expireAfterSeconds=0
        )

    def get_cached(self, cache_key):
        cached = self.collection.find_one({'cache_key': cache_key})

        if cached and not cached.get('is_stale'):
            return cached.get('payload')

        return None

    def set_cache(self, cache_key, payload, ttl_seconds=3600):

        self.collection.update_one(
            {'cache_key': cache_key},
            {
                '$set': {
                    'cache_key': cache_key,
                    'payload': payload,
                    'fetched_at': datetime.now(timezone.utc),
                    'expires_at': datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds),
                    'is_stale': False
                }
            },
            upsert=True
        )
