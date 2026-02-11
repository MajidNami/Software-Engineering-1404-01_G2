from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from typing import Optional

from ..serializers.trip_serializer import TripSerializer
from ..serializers.trip_create_serializer import TripCreateSerializer
from ..serializers.style_update_serializer import StyleUpdateSerializer
from ..serializers.cost_analysis_serializer import CostAnalysisSerializer
from ..serializers.budget_check_serializer import BudgetCheckSerializer
from ...application.services.trip_planning_service import TripPlanningService


class TripController(APIView):
    """REST API controller for trip operations."""

    def __init__(self, trip_planning_service: TripPlanningService, **kwargs):
        """Initialize controller with required services."""
        super().__init__(**kwargs)
        self.trip_planning_service = trip_planning_service

    def post(self, request):
        """Create a new trip."""
        serializer = TripCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Convert serializer data to domain objects
            # Call service to create trip
            # Return trip DTO
            return Response(
                {"message": "Trip creation endpoint"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, trip_id: int):
        """Get trip details."""
        user_id = request.user.id if request.user.is_authenticated else None
        if not user_id:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Call service to get trip
        # Return trip DTO
        return Response(
            {"message": f"Get trip {trip_id}"},
            status=status.HTTP_200_OK
        )

    def put(self, request, trip_id: int):
        """Regenerate trip by style."""
        serializer = StyleUpdateSerializer(data=request.data)
        if serializer.is_valid():
            # Call service to regenerate trip
            # Return updated trip DTO
            return Response(
                {"message": f"Regenerate trip {trip_id}"},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TripBudgetAnalysisController(APIView):
    """Controller for trip budget analysis."""

    def __init__(self, trip_planning_service: TripPlanningService, **kwargs):
        """Initialize controller with required services."""
        super().__init__(**kwargs)
        self.trip_planning_service = trip_planning_service

    def post(self, request, trip_id: int):
        """Analyze trip budget."""
        serializer = BudgetCheckSerializer(data=request.data)
        if serializer.is_valid():
            # Call service to analyze budget
            # Return cost analysis DTO
            return Response(
                {"message": f"Analyze budget for trip {trip_id}"},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TripConfirmController(APIView):
    """Controller for confirming a trip."""

    def post(self, request, trip_id: int):
        """Confirm a trip."""
        # Call service to confirm trip
        # Update trip status to CONFIRMED
        return Response(
            {"message": f"Confirm trip {trip_id}"},
            status=status.HTTP_200_OK
        )
