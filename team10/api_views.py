import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from core.auth import api_login_required

from .application.services.trip_planning_service_impl import TripPlanningServiceImpl
from .infrastructure.clients.wiki_client import get_wiki_client
from .services import trip_planning_service

from .models import Trip


@require_http_methods(["POST"])
@csrf_exempt  # CSRF handled by central system
# @api_login_required  # Requires user authentication from central system
def create_trip_api(request):
    """API endpoint to create a new trip. Requires authentication."""
    try:
        # Parse JSON data
        data = json.loads(request.body)
        print(data)
        # Validate required fields
        required_fields = ['destination', 'start_date', 'end_date', 'budget_level']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'error': f'Missing required field: {field}'
                }, status=400)

        # Validate budget_level enum
        valid_budget_levels = ['ECONOMY', 'MODERATE', 'LUXURY']
        if data['budget_level'] not in valid_budget_levels:
            return JsonResponse({
                'error': f'Invalid budget_level. Must be one of: {", ".join(valid_budget_levels)}'
            }, status=400)

        # User is guaranteed to be authenticated by @api_login_required
        user = request.user

        # Extract user_id (hash string) from user object
        user_id = str(user.id) if hasattr(user, 'id') else None
        if not user_id:
            return JsonResponse({
                'error': 'User ID not found'
            }, status=401)

        # Create trip using shared service instance
        trip = trip_planning_service.create_initial_trip(data, user_id)

        # Return success response
        return JsonResponse({
            'success': True,
            'trip_id': trip.id,
            'status': trip.status,
            'message': 'Trip created successfully'
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@api_login_required  # Requires user authentication
def get_trip_api(request, trip_id):
    """API endpoint to get trip details. Requires authentication."""
    try:
        # Only allow users to view their own trips
        user_id = str(request.user.id) if hasattr(request.user, 'id') else None
        trip = Trip.objects.get(id=trip_id, user_id=user_id)
        wiki = get_wiki_client(use_mock=True)
        dest_info = wiki.get_destination_basic_info(trip.requirements.destination_name)


        # Prepare response data
        trip_data = {
            'id': trip.id,
            'status': trip.status,
            'destination': trip.requirements.destination_name,
            'start_date': trip.requirements.start_at.isoformat(),
            'end_date': trip.requirements.end_at.isoformat(),
            'budget_level': trip.requirements.budget_level,
            'travelers_count': trip.requirements.travelers_count,
            'total_cost': float(trip.calculate_total_cost()),
            'daily_plans': [
                {
                    'id': plan.id,
                    'start_at': plan.start_at.isoformat(),
                    'end_at': plan.end_at.isoformat(),
                    'activity_type': plan.activity_type,
                    'description': plan.description,
                    'cost': float(plan.cost)
                }
                for plan in trip.daily_plans.all()
            ],
            'hotel_schedules': [
                {
                    'id': schedule.id,
                    'start_at': schedule.start_at.isoformat(),
                    'end_at': schedule.end_at.isoformat(),
                    'rooms_count': schedule.rooms_count,
                    'cost': float(schedule.cost)
                }
                for schedule in trip.hotel_schedules.all()
            ],
            'preferences': [
                {'tag': c.tag, 'description': c.description}
                for c in trip.requirements.constraints.all()
            ],
            'destination_info': {
                'name': dest_info.name,
                'description': dest_info.description,
                'country': dest_info.country,
                'region': dest_info.region,
            },
        }

        return JsonResponse(trip_data)

    except Trip.DoesNotExist:
        return JsonResponse({
            'error': 'Trip not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@require_http_methods(["PUT"])
@csrf_exempt  # CSRF handled by central system
@api_login_required  # Requires user authentication
def regenerate_trip_api(request, trip_id):
    """API endpoint to regenerate trip with new styles. Requires authentication."""
    try:
        # Verify user owns this trip
        user_id = str(request.user.id) if hasattr(request.user, 'id') else None
        trip_check = Trip.objects.filter(id=trip_id, user_id=user_id).exists()
        if not trip_check:
            return JsonResponse({
                'error': 'Trip not found or access denied'
            }, status=404)

        data = json.loads(request.body)
        styles = data.get('styles', [])

        trip = trip_planning_service.regenerate_by_styles(trip_id, styles)

        return JsonResponse({
            'success': True,
            'trip_id': trip.id,
            'status': trip.status,
            'message': 'Trip regenerated successfully'
        })

    except Trip.DoesNotExist:
        return JsonResponse({
            'error': 'Trip not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt  # CSRF handled by central system
@api_login_required  # Requires user authentication
def analyze_budget_api(request, trip_id):
    """API endpoint to analyze trip budget. Requires authentication."""
    try:
        # Verify user owns this trip
        user_id = str(request.user.id) if hasattr(request.user, 'id') else None
        trip_check = Trip.objects.filter(id=trip_id, user_id=user_id).exists()
        if not trip_check:
            return JsonResponse({
                'error': 'Trip not found or access denied'
            }, status=404)

        data = json.loads(request.body)
        budget_limit = float(data.get('budget_limit', 0))

        result = trip_planning_service.analyze_costs_and_budget(trip_id, budget_limit)

        return JsonResponse({
            'total_cost': result.total_cost,
            'budget_limit': result.budget_limit,
            'is_within_budget': result.is_within_budget,
            'analysis': result.analysis,
            'percentage_of_budget': (result.total_cost / result.budget_limit * 100) if result.budget_limit > 0 else 0
        })

    except Trip.DoesNotExist:
        return JsonResponse({
            'error': 'Trip not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)
