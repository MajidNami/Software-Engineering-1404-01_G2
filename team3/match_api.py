import requests
import sqlite3
import uuid
from datetime import datetime

def sync_from_team8(user_id):
    
    URL = f"http://127.0.0.1:8001/api/ratings/user={user_id}"
    
    try:
        response = requests.get(URL)
        if response.status_code == 200:
            data = response.json()
            
            conn = sqlite3.connect('team3.sqlite3')
            cursor = conn.cursor()
            
            for item in data:
                cursor.execute("""
                    INSERT OR REPLACE INTO user_interactions 
                    (interaction_id, user_id, item_id, item_type, interaction_type, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    str(uuid.uuid4()), 
                    user_id, 
                    item.get('placeId'),
                    'place', 
                    'rate', 
                    datetime.now().isoformat()
                ))
            
            conn.commit()
            conn.close()
            print(f"Successfully synced data for {user_id} from Team 8")
        else:
            print(f"Failed to fetch: Status {response.status_code}")
            
    except Exception as e:
        print(f"Error connecting to Team 8: {e}")
