from django.http import JsonResponse, FileResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from typing import Optional

from business.services import (
    TripService, TripDayService, TripItemService,
    DependencyService, ShareService, VotingService,
    ReviewService, MediaService
)
from .serializers import (
    TripListSerializer, TripDetailSerializer, TripCreateUpdateSerializer,
    TripDaySerializer, TripItemSerializer, ItemDependencySerializer,
    ShareLinkSerializer, VoteSerializer, TripReviewSerializer,
    UserMediaSerializer
)
from .pdf_generator import generate_trip_pdf, get_filename_for_trip


def test(request):
    """Test endpoint for development"""
    trips = TripService.get_all_trips()
    return JsonResponse({
        "status": "ok",
        "count": len(trips),
        "trips": [
            {"id": str(t.trip_id), "title": t.title, "province": t.province}
            for t in trips
        ]
    })


def ok(request):
    """Health check endpoint"""
    return JsonResponse({
        "response": "ok and fine"
    })


class TripViewSet(viewsets.ViewSet):
    """API endpoints for Trip management"""

    def list(self, request):
        """GET /api/trips/ - List all trips"""
        user_id = request.query_params.get('user_id')
        status_filter = request.query_params.get('status')

        trips = TripService.get_all_trips(
            user_id=int(user_id) if user_id else None,
            status=status_filter
        )

        serializer = TripListSerializer(trips, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """GET /api/trips/{id}/ - Get trip details"""
        trip = TripService.get_trip_detail(int(pk))

        if not trip:
            return Response(
                {"error": "Trip not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TripDetailSerializer(trip)
        return Response(serializer.data)

    def create(self, request):
        """POST /api/trips/ - Create a new trip"""
        serializer = TripCreateUpdateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_id = request.data.get('user_id')
            trip = TripService.create_trip(
                user_id=int(user_id) if user_id else None,
                data=serializer.validated_data
            )

            return Response(
                TripDetailSerializer(trip).data,
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, pk=None):
        """PUT /api/trips/{id}/ - Update a trip"""
        serializer = TripCreateUpdateSerializer(
            data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        trip = TripService.update_trip(int(pk), serializer.validated_data)

        if not trip:
            return Response(
                {"error": "Trip not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(TripDetailSerializer(trip).data)

    def destroy(self, request, pk=None):
        """DELETE /api/trips/{id}/ - Delete a trip"""
        if TripService.delete_trip(int(pk)):
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {"error": "Trip not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=True, methods=['post'])
    def copy(self, request, pk=None):
        """POST /api/trips/{id}/copy/ - Copy an existing trip"""
        user_id = request.data.get('user_id')

        trip = TripService.copy_trip(
            int(pk),
            user_id=int(user_id) if user_id else None
        )

        if not trip:
            return Response(
                {"error": "Original trip not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            TripDetailSerializer(trip).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def finalize(self, request, pk=None):
        """POST /api/trips/{id}/finalize/ - Finalize a trip"""
        trip = TripService.finalize_trip(int(pk))

        if not trip:
            return Response(
                {"error": "Trip not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(TripDetailSerializer(trip).data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """GET /api/trips/search/?q=query - Search trips"""
        query = request.query_params.get('q', '')

        if not query:
            return Response(
                {"error": "Search query required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        trips = TripService.search_trips(query)
        serializer = TripListSerializer(trips, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def history(self, request):
        """
        GET /api/trips/history/ - Get trip history for logged-in user

        Returns all trips for the authenticated user, sorted by date.
        Past trips are marked with is_past flag for UI styling.
        Requires authentication via JWT token.
        """
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Get trips for authenticated user
        trips = TripService.get_all_trips(user_id=request.user.id)
        serializer = TripListSerializer(trips, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def claim(self, request, pk=None):
        """
        POST /api/trips/{id}/claim/ - Claim a guest trip as logged-in user

        Converts a guest trip (user_id=null) to a user trip.
        Use case: User creates trip without login, then logs in and claims it.
        Requires authentication via JWT token.
        """
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Get the trip
        trip = TripService.get_trip_detail(int(pk))

        if not trip:
            return Response(
                {"error": "Trip not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if already claimed
        if trip.user_id is not None:
            return Response(
                {"error": "Trip is already claimed by another user"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Claim the trip for authenticated user
        updated_trip = TripService.update_trip(
            int(pk), {'user_id': request.user.id})

        return Response(
            TripDetailSerializer(updated_trip).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'])
    def export_pdf(self, request, pk=None):
        """
        GET /api/trips/{id}/export/pdf/ - Export trip to PDF

        Generates a PDF file with trip timeline, items, and cost breakdown.
        Suitable for printing or sharing offline.

        Returns: PDF file as attachment
        """
        trip = TripService.get_trip_detail(int(pk))

        if not trip:
            return Response(
                {"error": "Trip not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            # Generate PDF
            pdf_buffer = generate_trip_pdf(trip)
            filename = get_filename_for_trip(trip)

            # Return as downloadable file
            response = FileResponse(
                pdf_buffer,
                content_type='application/pdf',
                as_attachment=True,
                filename=filename
            )

            return response

        except Exception as e:
            return Response(
                {"error": f"PDF generation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def cost_breakdown(self, request, pk=None):
        """
        GET /api/trips/{id}/cost_breakdown/ - Get cost breakdown

        Returns detailed cost analysis:
        - Total estimated cost
        - Breakdown by category (DINING, STAY, etc.)
        - Breakdown by day
        - Category percentages

        Example response:
        {
            "total_estimated_cost": 2500000.00,
            "breakdown_by_category": {
                "DINING": {"amount": 800000, "percentage": 32.0, "count": 5},
                "STAY": {"amount": 1500000, "percentage": 60.0, "count": 3},
                "HISTORICAL": {"amount": 200000, "percentage": 8.0, "count": 4}
            },
            "breakdown_by_day": [
                {"day_index": 1, "date": "2026-05-01", "cost": 850000},
                {"day_index": 2, "date": "2026-05-02", "cost": 1650000}
            ]
        }
        """
        breakdown = TripService.calculate_trip_cost_breakdown(int(pk))

        if not breakdown:
            return Response(
                {"error": "Trip not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(breakdown)

    @action(detail=True, methods=['post'], url_path='days')
    def create_day(self, request, pk=None):
        """
        POST /api/trips/{id}/days/ - Create a new day for a trip

        Used by Trip Generation Service (Mohammad Hossein) to add days
        to a generated trip.

        Request body: {
            "day_index": 1,
            "specific_date": "2026-03-10",
            "start_geo_location": "اصفهان" (optional)
        }

        Returns: {
            "day_id": 123,
            "trip": 456,
            "day_index": 1,
            "specific_date": "2026-03-10",
            "start_geo_location": "اصفهان",
            "items": []
        }
        """
        # Verify trip exists
        trip = TripService.get_trip_detail(int(pk))
        if not trip:
            return Response(
                {"error": "Trip not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Validate input
        serializer = TripDaySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Create day
            day = TripDayService.create_day(
                int(pk),
                serializer.validated_data
            )
            return Response(
                TripDaySerializer(day).data,
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class TripDayViewSet(viewsets.ViewSet):
    """API endpoints for TripDay management"""

    def list(self, request):
        """GET /api/trip-days/?trip_id=X - List days for a trip"""
        trip_id = request.query_params.get('trip_id')

        if not trip_id:
            return Response(
                {"error": "trip_id parameter required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        days = TripDayService.get_days_for_trip(int(trip_id))
        serializer = TripDaySerializer(days, many=True)
        return Response(serializer.data)

    def create(self, request):
        """POST /api/trip-days/ - Create a new day"""
        serializer = TripDaySerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        trip_id = request.data.get('trip_id')
        if not trip_id:
            return Response(
                {"error": "trip_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        day = TripDayService.create_day(
            int(trip_id), serializer.validated_data)
        return Response(
            TripDaySerializer(day).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        """PUT /api/trip-days/{id}/ - Update a day"""
        serializer = TripDaySerializer(data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        day = TripDayService.update_day(int(pk), serializer.validated_data)

        if not day:
            return Response(
                {"error": "Day not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(TripDaySerializer(day).data)

    def destroy(self, request, pk=None):
        """DELETE /api/trip-days/{id}/ - Delete a day"""
        if TripDayService.delete_day(int(pk)):
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {"error": "Day not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=True, methods=['post'], url_path='items/bulk')
    def create_items_bulk(self, request, pk=None):
        """
        POST /api/trip-days/{id}/items/bulk/ - Bulk create items for a day

        Used by Trip Generation Service (Mohammad Hossein) to add multiple
        items to a day in a single request.

        Request body: {
            "items": [
                {
                    "item_type": "VISIT",
                    "place_ref_id": "place_123",
                    "title": "میدان نقش جهان",
                    "category": "HISTORICAL",
                    "address_summary": "اصفهان، میدان نقش جهان",
                    "lat": 32.6546,
                    "lng": 51.6777,
                    "start_time": "09:00:00",
                    "end_time": "11:00:00",
                    "duration_minutes": 120,
                    "estimated_cost": "200000.00",
                    "sort_order": 1
                },
                // ... more items
            ]
        }

        Returns: {
            "created_count": 3,
            "items": [ /* array of created items */ ]
        }
        """
        # Verify day exists
        day = TripDayService.get_day_by_id(int(pk))
        if not day:
            return Response(
                {"error": "Day not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get items array from request
        items_data = request.data.get('items', [])

        if not items_data:
            return Response(
                {"error": "items array required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(items_data, list):
            return Response(
                {"error": "items must be an array"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create items
        created_items = []
        errors = []

        for idx, item_data in enumerate(items_data):
            # Validate each item
            serializer = TripItemSerializer(data=item_data)

            if not serializer.is_valid():
                errors.append({
                    "index": idx,
                    "errors": serializer.errors
                })
                continue

            try:
                # Create item
                item = TripItemService.create_item(
                    int(pk),
                    serializer.validated_data
                )
                created_items.append(item)
            except ValueError as e:
                errors.append({
                    "index": idx,
                    "error": str(e)
                })

        # Return response
        response_data = {
            "created_count": len(created_items),
            "items": TripItemSerializer(created_items, many=True).data
        }

        if errors:
            response_data["errors"] = errors
            return Response(
                response_data,
                status=status.HTTP_207_MULTI_STATUS
            )

        return Response(
            response_data,
            status=status.HTTP_201_CREATED
        )


class TripItemViewSet(viewsets.ViewSet):
    """API endpoints for TripItem management"""

    def list(self, request):
        """GET /api/items/?day_id=X - List items for a day"""
        day_id = request.query_params.get('day_id')

        if not day_id:
            return Response(
                {"error": "day_id parameter required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        items = TripItemService.get_items_for_day(int(day_id))
        serializer = TripItemSerializer(items, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """GET /api/items/{id}/ - Get a single item"""
        item = TripItemService.get_item_by_id(int(pk))

        if not item:
            return Response(
                {"error": "Item not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TripItemSerializer(item)
        return Response(serializer.data)

    def create(self, request):
        """POST /api/items/ - Create a new item"""
        serializer = TripItemSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        day_id = request.data.get('day_id')
        if not day_id:
            return Response(
                {"error": "day_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            item = TripItemService.create_item(
                int(day_id), serializer.validated_data)
            return Response(
                TripItemSerializer(item).data,
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def partial_update(self, request, pk=None):
        """PATCH /api/items/{id}/ - Update an item (API #6)"""
        serializer = TripItemSerializer(data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            item = TripItemService.update_item(
                int(pk), serializer.validated_data)

            if not item:
                return Response(
                    {"error": "Item not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(TripItemSerializer(item).data)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, pk=None):
        """DELETE /api/items/{id}/ - Delete an item (API #7)"""
        if TripItemService.delete_item(int(pk)):
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {"error": "Item not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=True, methods=['post'])
    def lock(self, request, pk=None):
        """POST /api/items/{id}/lock/ - Lock an item"""
        item = TripItemService.lock_item(int(pk))

        if not item:
            return Response(
                {"error": "Item not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(TripItemSerializer(item).data)

    @action(detail=True, methods=['post'])
    def unlock(self, request, pk=None):
        """POST /api/items/{id}/unlock/ - Unlock an item"""
        item = TripItemService.unlock_item(int(pk))

        if not item:
            return Response(
                {"error": "Item not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(TripItemSerializer(item).data)

    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """POST /api/items/reorder/ - Reorder items in a day"""
        day_id = request.data.get('day_id')
        item_order = request.data.get('item_order', [])

        if not day_id or not item_order:
            return Response(
                {"error": "day_id and item_order required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        TripItemService.reorder_items(int(day_id), item_order)
        return Response({"success": True})

    @action(detail=True, methods=['post'])
    def replace(self, request, pk=None):
        """
        POST /api/items/{id}/replace/ - Replace item with alternative (API #8)

        Replaces current item with a new place from alternatives list.
        The new item will keep the same time slot as the replaced item.

        Future Integration: Should call Mohammad Hossein's Facility Service 
        to get place details automatically from place_id.

        Request body: {
            "new_place_id": "string",        # Required
            "new_place_data": {              # Optional - will come from Facility Service
                "title": "string",
                "category": "string",
                "address": "string",
                "lat": float,
                "lng": float,
                "estimated_cost": float
            }
        }
        """
        new_place_id = request.data.get('new_place_id')
        new_place_data = request.data.get('new_place_data', {})

        if not new_place_id:
            return Response(
                {"error": "new_place_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get current item
        item = TripItemService.get_item_by_id(int(pk))

        if not item:
            return Response(
                {"error": "Item not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # TODO: Integration with Facility Service
        # from externalServices.grpc.services.facility_client import FacilityClient
        # facility_client = FacilityClient()
        # new_place_data = facility_client.get_place_by_id(new_place_id)
        # if not new_place_data:
        #     return Response({"error": "Place not found in Facility Service"}, 404)

        # Prepare update data - keep same time, update place details
        update_data = {
            'place_ref_id': new_place_id,
            'title': new_place_data.get('title', item.title),
            'category': new_place_data.get('category', item.category),
            'address_summary': new_place_data.get('address', item.address_summary),
            'estimated_cost': new_place_data.get('estimated_cost', item.estimated_cost)
        }

        if 'lat' in new_place_data:
            update_data['lat'] = new_place_data['lat']
        if 'lng' in new_place_data:
            update_data['lng'] = new_place_data['lng']

        try:
            updated_item = TripItemService.update_item(int(pk), update_data)

            return Response(
                TripItemSerializer(updated_item).data,
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
