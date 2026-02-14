"""
Django views for Team 8
These are simple views for compatibility with the Core system
"""
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

TEAM_NAME = "team8"


def base(request):
    """Base view - serves the React frontend"""
    return render(request, f"{TEAM_NAME}/index.html")


@require_http_methods(["GET"])
def ping(request):
    """Simple ping endpoint to check if service is running"""
    return JsonResponse({
        "team": TEAM_NAME,
        "service": "Comments, Media & Ratings",
        "status": "ok",
        "version": "1.0.0"
    })


@require_http_methods(["GET"])
def health(request):
    """Health check endpoint for monitoring"""
    from django.db import connection
    
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            "status": "healthy",
            "database": "connected",
            "service": TEAM_NAME
        })
    except Exception as e:
        return JsonResponse({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }, status=503)

