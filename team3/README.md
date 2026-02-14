# Team 3 - Recommendation Service

This app implements a Recommendation Service for `US-01` to `US-07`.

## Endpoints

- `GET /team3/health/`
- `POST /team3/api/interests/`
- `POST /team3/api/recommendations/personalized/`
- `POST /team3/api/recommendations/contextual/`
- `POST /team3/api/recommendations/location/`
- `POST /team3/api/recommendations/score-candidates/`
- `POST /team3/api/recommendations/suggest-destinations/`
- `POST /team3/api/recommendations/suggest-by-region/`
- `GET /team3/api/recommendations/<user_id>/`
- `GET /team3/api/recommendations/reason/<recommendation_id>/`
- `POST /team3/api/interactions/`
- `POST /team3/api/feedback/`

## Quick Local Run

From repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r team3/requirements.txt
python manage.py migrate
python manage.py runserver
```

## Example Requests

```bash
curl -X POST http://127.0.0.1:8000/team3/api/recommendations/personalized/ \
  -H "Content-Type: application/json" \
  -d '{"userId":"u100","destination":"tehran","season":"SPRING","limit":5}'
```

```bash
curl -X POST http://127.0.0.1:8000/team3/api/recommendations/location/ \
  -H "Content-Type: application/json" \
  -d '{"latitude":35.6892,"longitude":51.3890,"radius_km":50,"limit":5}'
```
