# =======================================================================================
# COMPLETE API IMPLEMENTATION - api/views.py
# =======================================================================================
from _decimal import Decimal

from django.contrib.auth.models import User
from django.http import JsonResponse, FileResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from typing import Optional, List, Dict
from datetime import date, datetime

from business.services import (
    TripService, TripDayService, TripItemService,
    DependencyService, ShareService, VotingService,
    ReviewService, MediaService,SuggestionService
)
from business.generators import TripGenerator
from business.helpers import AlternativesProvider

from .serializers import (
    TripListSerializer, TripDetailSerializer, TripCreateUpdateSerializer,
    TripDaySerializer, TripItemSerializer, TripItemCreateSerializer,
    ItemDependencySerializer, ShareLinkSerializer, VoteSerializer,
    TripReviewSerializer, UserMediaSerializer
)
from .pdf_generator import generate_trip_pdf, get_filename_for_trip


def _safe_int(value, field_name='id'):
    """Safely convert value to int, raising ValueError with a clear message."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


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


def _check_trip_ownership(request, trip) -> bool:
    """
    Check if the current user owns the trip.
    Returns True if the trip has no owner (guest trip) or if the user is the owner.
    """
    if trip.user_id is None:
        return True  # Guest trip, anyone can modify
    user_id = getattr(request, 'jwt_user_id', None)
    if user_id is None:
        return True  # No auth middleware, allow (development mode)
    return trip.user_id == user_id


class TripViewSet(viewsets.ViewSet):
    """API endpoints for Trip management"""

    def list(self, request):
        """GET /api/trips/ - List all trips"""
        user_id = request.query_params.get('user_id')
        status_filter = request.query_params.get('status')

        # If user_id is not provided in query params, try to get it from JWT for "my trips"
        if not user_id:
            user_id = getattr(request, 'jwt_user_id', None)

        trips = TripService.get_all_trips(
            user_id=user_id,
            status=status_filter
        )

        serializer = TripListSerializer(trips, many=True)
        return Response({
            "count": len(trips),
            "results": serializer.data
        })

    def retrieve(self, request, pk=None):
        """GET /api/trips/{id}/ - Get trip details"""
        trip = TripService.get_trip_detail(pk)

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
            # Inject user_id from JWT if available
            user_id = getattr(request, 'jwt_user_id', None)
            
            # Use serializer.save() which calls create()
            # Pass user_id explicitly to save method (serializer needs to handle it or we pass it to perform_create equivalent)
            # Since TripCreateUpdateSerializer.create doesn't accept user_id in validated_data by default,
            # we need to pass it as an additional argument or add it to validated_data
            
            # Actually, serializer.save(**kwargs) passes kwargs to create()
            trip = serializer.save(user_id=user_id)

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
        return self._update_trip(request, pk, partial=False)

    def partial_update(self, request, pk=None):
        """PATCH /api/trips/{id}/ - Partial update a trip"""
        return self._update_trip(request, pk, partial=True)

    def _update_trip(self, request, pk, partial=False):
        """Helper method for update and partial_update"""
        # Ownership check
        trip = TripService.get_trip_detail(pk)
        if not trip:
            return Response(
                {"error": "Trip not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        if not _check_trip_ownership(request, trip):
            return Response(
                {"error": "You do not have permission to modify this trip",
                 "error_fa": "شما اجازه ویرایش این سفر را ندارید"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = TripCreateUpdateSerializer(
            trip, data=request.data, partial=partial)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        updated_trip = TripService.update_trip(int(pk), serializer.validated_data)
        return Response(TripDetailSerializer(updated_trip).data)

    def destroy(self, request, pk=None):
        """DELETE /api/trips/{id}/ - Delete a trip"""
        # Ownership check
        trip = TripService.get_trip_detail(int(pk))
        if not trip:
            return Response(
                {"error": "Trip not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        if not _check_trip_ownership(request, trip):
            return Response(
                {"error": "You do not have permission to delete this trip",
                 "error_fa": "شما اجازه حذف این سفر را ندارید"},
                status=status.HTTP_403_FORBIDDEN
            )

        TripService.delete_trip(int(pk))
        return Response(status=status.HTTP_204_NO_CONTENT)


    @action(detail=False, methods=['post'], url_path='generate')
    def generate_trip(self, request):
        """
        POST /api/trips/generate/

        موتور تولید سفر - الگوریتم اصلی ساخت برنامه سفر

        ورودی:
        {
            "province": "اصفهان",                  // شهر/استان (اجباری)
            "city": "اصفهان",                      // شهر دقیق (اختیاری)
            "start_date": "2026-03-15",            // تاریخ شروع (اجباری)
            "end_date": "2026-03-17",              // تاریخ پایان (اختیاری)
            "interests": ["تاریخی", "فرهنگی"],     // علایق (اختیاری)
            "budget_level": "MEDIUM",              // بودجه: ECONOMY/MEDIUM/LUXURY/UNLIMITED
            "daily_available_hours": 12,           // تراکم/ساعات روزانه (اختیاری)
            "travel_style": "COUPLE",              // سبک سفر (اختیاری)
            "user_id": 123                         // کاربر (اختیاری)
        }

        خروجی:
        - JSON کامل Trip با Days و Items
        - محاسبه خودکار هزینه
        - وضعیت FINALIZED

        وابستگی:
        - Facility Service (محمدحسین): لیست مکان‌ها
        - Recommendation Service (محمدحسین): رتبه‌بندی
        """

        # 1. اعتبارسنجی ورودی‌های اجباری
        province = request.data.get('province')
        budget_level = request.data.get('budget_level')
        start_date_str = request.data.get('start_date')

        if not province:
            return Response(
                {
                    "error": "province is required",
                    "error_fa": "استان الزامی است"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not budget_level:
            return Response(
                {
                    "error": "budget_level is required",
                    "error_fa": "سطح بودجه الزامی است"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. اعتبارسنجی budget_level
        valid_budgets = ['ECONOMY', 'MEDIUM', 'LUXURY', 'UNLIMITED']
        if budget_level not in valid_budgets:
            return Response(
                {
                    "error": f"budget_level must be one of: {', '.join(valid_budgets)}",
                    "error_fa": "سطح بودجه نامعتبر است"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not start_date_str:
            return Response(
                {
                    "error": "start_date is required",
                    "error_fa": "تاریخ شروع الزامی است"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. پردازش تاریخ‌ها
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {
                    "error": "start_date must be in YYYY-MM-DD format",
                    "error_fa": "فرمت تاریخ شروع نامعتبر است"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # بررسی تاریخ گذشته
        if start_date < date.today():
            return Response(
                {
                    "error": "start_date cannot be in the past",
                    "error_fa": "تاریخ شروع نمی‌تواند در گذشته باشد"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        end_date = None
        end_date_str = request.data.get('end_date')
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                if end_date < start_date:
                    return Response(
                        {
                            "error": "end_date must be after start_date",
                            "error_fa": "تاریخ پایان باید بعد از تاریخ شروع باشد"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # حداکثر 30 روز
                duration = (end_date - start_date).days + 1
                if duration > 30:
                    return Response(
                        {
                            "error": "Trip duration cannot exceed 30 days",
                            "error_fa": "مدت سفر نمی‌تواند بیش از 30 روز باشد"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

            except ValueError:
                return Response(
                    {
                        "error": "end_date must be in YYYY-MM-DD format",
                        "error_fa": "فرمت تاریخ پایان نامعتبر است"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 4. دریافت پارامترهای اختیاری
        city = request.data.get('city')
        interests = request.data.get('interests', [])
        daily_available_hours = request.data.get('daily_available_hours', 12)
        travel_style = request.data.get('travel_style', 'SOLO')

        # Bug 9 fix: استفاده از JWT بجای request body برای شناسایی کاربر
        user_id = getattr(request, 'jwt_user_id', None)

        # اعتبارسنجی daily_available_hours
        if not isinstance(daily_available_hours, int) or daily_available_hours < 1 or daily_available_hours > 24:
            daily_available_hours = 12

        # اعتبارسنجی travel_style
        valid_styles = ['SOLO', 'COUPLE', 'FAMILY', 'FRIENDS', 'BUSINESS']
        if travel_style not in valid_styles:
            travel_style = 'SOLO'

        try:
            # 5. تولید سفر با TripGenerator
            generator = TripGenerator()

            trip = generator.generate(
                user_id=user_id,
                province=province,
                city=city,
                interests=interests,
                budget_level=budget_level,
                start_date=start_date,
                end_date=end_date,
                daily_available_hours=daily_available_hours,
                travel_style=travel_style
            )

            # 6. user قبلاً در TripGenerator.generate() اختصاص داده شده

            # 7. برگرداندن نتیجه
            serializer = TripDetailSerializer(trip)

            return Response(
                {
                    "success": True,
                    "message": "Trip generated successfully",
                    "message_fa": "برنامه سفر با موفقیت ایجاد شد",
                    "trip": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        except ValueError as e:
            return Response(
                {
                    "error": str(e),
                    "error_fa": "خطا در تولید برنامه سفر"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {
                    "error": f"Trip generation failed: {str(e)}",
                    "error_fa": "خطای سیستمی در تولید سفر"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
        return Response({
            "count": len(trips),
            "results": serializer.data
        })

    @action(detail=False, methods=['get'])
    def history(self, request):
        """
        GET /api/trips/history/ - Get trip history for logged-in user

        Returns all trips for the authenticated user, sorted by date.
        Past trips are marked with is_past flag for UI styling.
        Requires authentication via JWT token.
        """
        # Check if user is authenticated via JWT middleware
        user_id = getattr(request, 'jwt_user_id', None)
        if user_id is None:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Get trips for authenticated user
        trips = TripService.get_all_trips(user_id=user_id)
        serializer = TripListSerializer(trips, many=True)
        return Response({
            "count": len(trips),
            "results": serializer.data
        })

    @action(detail=True, methods=['post'])
    def claim(self, request, pk=None):
        """
        POST /api/trips/{id}/claim/

        اتصال مهمان به کاربر - تبدیل Trip مهمان به Trip کاربر

        Use Case:
        - کاربر بدون لاگین Trip ساخته (user_id = null)
        - بعد لاگین می‌کنه
        - با این API می‌تونه Trip رو claim کنه (user_id = logged_in_user)

        ورودی:
        - Token/Session کاربر لاگین شده
        - Trip ID در URL

        خروجی:
        {
            "success": true,
            "message": "Trip claimed successfully",
            "trip": { ... }  // Trip با user_id آپدیت شده
        }

        منطق:
        1. بررسی لاگین بودن کاربر
        2. بررسی trip وجود داشته باشه
        3. بررسی trip قبلاً claim نشده باشه (user_id == null)
        4. آپدیت user_id به کاربر فعلی
        5. برگرداندن Trip آپدیت شده

        وابستگی:
        - صفر (فقط آپدیت database)
        """
        # Check if user is authenticated via JWT middleware
        user_id = getattr(request, 'jwt_user_id', None)
        if user_id is None:
            return Response(
                {
                    "error": "Authentication required",
                    "error_fa": "لاگین الزامی است"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 2. دریافت Trip
        trip = TripService.get_trip_detail(int(pk))

        if not trip:
            return Response(
                {
                    "error": "Trip not found",
                    "error_fa": "سفر یافت نشد"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # 3. بررسی claim نشده بودن
        if trip.user_id is not None:
            # اگر قبلاً claim شده
            if trip.user_id == user_id:
                # همین کاربر claim کرده
                return Response(
                    {
                        "success": False,
                        "message": "You have already claimed this trip",
                        "message_fa": "شما قبلاً این سفر را ثبت کرده‌اید"
                    },
                    status=status.HTTP_200_OK
                )
            else:
                # کاربر دیگه claim کرده
                return Response(
                    {
                        "error": "Trip is already claimed by another user",
                        "error_fa": "این سفر قبلاً توسط کاربر دیگری ثبت شده"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 4. Claim کردن Trip
        try:
            updated_trip = TripService.update_trip(
                int(pk),
                {'user_id': user_id}
            )

            if not updated_trip:
                raise Exception("Failed to update trip")

            # 5. برگرداندن نتیجه
            serializer = TripDetailSerializer(updated_trip)

            return Response(
                {
                    "success": True,
                    "message": "Trip claimed successfully",
                    "message_fa": "سفر با موفقیت به حساب شما منتقل شد",
                    "trip": serializer.data
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {
                    "error": f"Failed to claim trip: {str(e)}",
                    "error_fa": "خطا در انتقال سفر"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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

        Request body: Empty (day_index and specific_date are auto-generated)

        Returns: {
            "day_id": 123,
            "trip_id": 456,
            "day_index": 1,
            "specific_date": "2026-03-10",
            "created_at": "..."
        }
        """
        # Verify trip exists
        trip = TripService.get_trip_detail(int(pk))
        if not trip:
            return Response(
                {"error": "Trip not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            # Create day (auto-calculates day_index and specific_date)
            day = TripDayService.create_day(int(pk))

            return Response(
                {
                    'day_id': day.day_id,
                    'trip_id': day.trip.trip_id,
                    'day_index': day.day_index,
                    'specific_date': day.specific_date.isoformat(),
                    'created_at': day.trip.created_at.isoformat() if hasattr(day.trip, 'created_at') else None
                },
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
        trip_id = request.data.get('trip_id')
        if not trip_id:
            return Response(
                {"error": "trip_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            day = TripDayService.create_day(int(trip_id))
            return Response(
                TripDaySerializer(day).data,
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
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
        # Support both {"items": [...]} and direct array [...]
        if isinstance(request.data, list):
            items_data = request.data
        else:
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
            serializer = TripItemCreateSerializer(data=item_data)

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
        serializer = TripItemCreateSerializer(data=request.data)

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

    @action(detail=True, methods=['get'], url_path='alternatives')
    def get_alternatives(self, request, pk=None):
        """
        GET /api/items/{id}/alternatives/

        پیشنهاد جایگزین - لیست مکان‌های مشابه برای جایگزینی

        Query Parameters:
        - max_results: تعداد نتایج (پیش‌فرض: 5، حداکثر: 20)

        خروجی:
        {
            "item_id": 123,
            "current_place": {
                "place_id": "place_001",
                "title": "میدان نقش جهان",
                "category": "HISTORICAL",
                "lat": 32.6546,
                "lng": 51.6777
            },
            "alternatives": [
                {
                    "id": "place_005",
                    "title": "باغ چهلستون",
                    "category": "HISTORICAL",
                    "address": "اصفهان، خیابان استانداری",
                    "lat": 32.6612,
                    "lng": 51.6697,
                    "entry_fee": 150000,
                    "price_tier": "BUDGET",
                    "rating": 4.6,
                    "distance": 1.2,
                    "recommendation_reason": "نزدیک‌ترین جاذبه مشابه"
                }
            ],
            "count": 5
        }

        منطق:
        - فیلتر بر اساس category
        - مرتب‌سازی بر اساس distance
        - فیلتر بر اساس price_tier (در محدوده بودجه Trip)

        وابستگی:
        - Facility Service (MongoDB geo-search)
        """

        # 1. دریافت item
        item = TripItemService.get_item_by_id(int(pk))

        if not item:
            return Response(
                {
                    "error": "Item not found",
                    "error_fa": "آیتم یافت نشد"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. دریافت اطلاعات trip برای location
        trip = item.day.trip

        # 3. دریافت max_results از query params
        try:
            max_results = int(request.query_params.get('max_results', 5))
            max_results = max(1, min(max_results, 20))  # محدود به 1-20
        except (ValueError, TypeError):
            max_results = 5

        try:
            # 4. دریافت alternatives با AlternativesProvider
            provider = AlternativesProvider()
            alternatives = provider.get_alternatives(
                original_place_id=item.place_ref_id,
                province=trip.province,
                city=trip.city,
                category=item.category,
                max_results=max_results
            )

            # 5. افزودن دلیل پیشنهاد به هر alternative
            for i, alt in enumerate(alternatives):
                if i == 0:
                    alt['recommendation_reason'] = "نزدیک‌ترین جاذبه مشابه"
                elif alt.get('rating', 0) > 4.5:
                    alt['recommendation_reason'] = "بالاترین امتیاز کاربران"
                elif alt.get('price_tier') == 'FREE':
                    alt['recommendation_reason'] = "بازدید رایگان"
                elif alt.get('price_tier') == 'BUDGET':
                    alt['recommendation_reason'] = "مقرون‌به‌صرفه"
                else:
                    alt['recommendation_reason'] = f"در فاصله {alt.get('distance', 0):.1f} کیلومتری"

            # 6. ساخت response
            response_data = {
                "success": True,
                "item_id": item.item_id,
                "current_place": {
                    "place_id": item.place_ref_id,
                    "title": item.title,
                    "category": item.category,
                    "lat": float(item.lat) if item.lat else None,
                    "lng": float(item.lng) if item.lng else None,
                    "estimated_cost": float(item.estimated_cost)
                },
                "alternatives": alternatives,
                "count": len(alternatives)
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {
                    "error": f"Failed to get alternatives: {str(e)}",
                    "error_fa": "خطا در دریافت پیشنهادات"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



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

        try:
            # Get new place details from Facility Service
            from externalServices.grpc.services.facility_client import FacilityClient

            facility_client = FacilityClient()
            new_place_data = facility_client.get_place_by_id(new_place_id)

            if not new_place_data:
                return Response(
                    {"error": "Place not found in Facility Service"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Prepare update data - keep same time, update place details
            update_data = {
                'place_ref_id': new_place_id,
                'title': new_place_data.get('title', item.title),
                'category': new_place_data.get('category', item.category),
                'address_summary': new_place_data.get('address', item.address_summary),
                'estimated_cost': new_place_data.get('entry_fee', item.estimated_cost),
                'price_tier': new_place_data.get('price_tier', item.price_tier),
                'main_image_url': new_place_data.get('images', [''])[0] if new_place_data.get(
                    'images') else item.main_image_url
            }

            if 'lat' in new_place_data:
                update_data['lat'] = new_place_data['lat']
            if 'lng' in new_place_data:
                update_data['lng'] = new_place_data['lng']

            # Update item
            updated_item = TripItemService.update_item(int(pk), update_data)

            # Recalculate trip cost
            trip = item.day.trip
            from business.generators import TripGenerator
            generator = TripGenerator()
            generator._calculate_trip_cost(trip)

            return Response(
                TripItemSerializer(updated_item).data,
                status=status.HTTP_200_OK
            )

        except ImportError:
            # Fallback if Facility Service not available
            return Response(
                {"error": "Facility Service integration not available. Please provide new_place_data."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Replacement failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['POST'])
def suggest_destinations(request):
    """
    POST /api/destinations/suggest/

    پیشنهاد مقصد - پیشنهاد 3 شهر بر اساس فصل، بودجه، سبک سفر و منطقه

    ورودی:
    {
        "season": "spring",                    // فصل: spring/summer/fall/winter
        "budget_level": "MEDIUM",              // بودجه: ECONOMY/MEDIUM/LUXURY/UNLIMITED
        "travel_style": "COUPLE",              // سبک: SOLO/COUPLE/FAMILY/FRIENDS/BUSINESS
        "interests": ["تاریخی", "طبیعت"],      // علایق (اختیاری)
        "region": "NORTH"                      // منطقه (اختیاری): NORTH/SOUTH/EAST/WEST/CENTRAL
    }

    خروجی:
    {
        "suggestions": [
            {
                "city": "اصفهان",
                "province": "اصفهان",
                "score": 95,
                "reason": "بهترین شهر برای علاقه‌مندان به تاریخ و فرهنگ",
                "highlights": ["میدان نقش جهان", "سی‌وسه‌پل"],
                "best_season": "spring",
                "estimated_cost": "2500000",
                "duration_days": 3,
                "description": "اصفهان با آب و هوای معتدل در بهار...",
                "images": ["url1", "url2"]
            }
        ]
    }
    """

    # 1. اعتبارسنجی ورودی
    season = request.data.get('season', 'spring')
    budget_level = request.data.get('budget_level')
    travel_style = request.data.get('travel_style', 'SOLO')
    interests = request.data.get('interests', [])
    region = request.data.get('region')

    # اعتبارسنجی budget_level (اختیاری کردن برای فرم، اگر نال بود دیفالت MEDIUM)
    # اما طبق فرانت فعلی ممکنه نال بیاد اگر سلکتور نباشه.
    if not budget_level:
         budget_level = 'MEDIUM'

    # Map English season to Persian
    season_map = {
        'spring': 'بهار',
        'summer': 'تابستان',
        'fall': 'پاییز',
        'autumn': 'پاییز',
        'winter': 'زمستان'
    }

    season_persian = season_map.get(season.lower(), 'بهار')
    valid_seasons = ['spring', 'summer', 'fall', 'autumn', 'winter']
    if season.lower() not in valid_seasons:
        season = 'spring'
        season_persian = 'بهار'

    # اعتبارسنجی budget_level
    valid_budgets = ['ECONOMY', 'MEDIUM', 'LUXURY', 'UNLIMITED']
    if budget_level not in valid_budgets:
        budget_level = 'MEDIUM'

    # اعتبارسنجی travel_style
    valid_styles = ['SOLO', 'COUPLE', 'FAMILY', 'FRIENDS', 'BUSINESS']
    if travel_style not in valid_styles:
        travel_style = 'SOLO'

    try:
        # 2. پیشنهاد مقصدها بر اساس پارامترها
        suggestions = SuggestionService.generate_destination_suggestions(
            season=season_persian,
            budget_level=budget_level,
            travel_style=travel_style,
            interests=interests,
            region=region
        )

        return Response(
            {
                "success": True,
                "count": len(suggestions),
                "suggestions": suggestions,
                "filters": {
                    "season": season,
                    "budget_level": budget_level,
                    "travel_style": travel_style,
                    "interests": interests,
                    "region": region
                }
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {
                "error": f"Failed to generate suggestions: {str(e)}",
                "error_fa": "خطا در تولید پیشنهادات"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _generate_destination_suggestions(
        season: str,
        budget_level: str,
        travel_style: str,
        interests: List[str],
        region: Optional[str] = None
) -> List[Dict]:
    """
    منطق اصلی پیشنهاد مقصد
    """

    # دیتابیس مقصدهای محبوب (توسعه یافته با Region و Image)
    destinations_db = [
        # --- CENTER ---
        {
            "city": "اصفهان",
            "province": "اصفهان",
            "region": "CENTRAL",
            "best_seasons": ["spring", "fall"],
            "budget_min": "ECONOMY",
            "categories": ["تاریخی", "فرهنگی", "معماری", "خرید", "غذا"],
            "suitable_for": ["COUPLE", "FAMILY", "FRIENDS"],
            "highlights": ["میدان نقش جهان", "سی‌وسه‌پل", "مسجد شیخ لطف‌الله"],
            "description": "اصفهان نصف جهان با جاذبه‌های تاریخی بی‌نظیر و آب و هوای معتدل، مهد هنر و معماری ایرانیست.",
            "estimated_cost_3days": {"ECONOMY": 1500000, "MEDIUM": 2500000, "LUXURY": 5000000},
            "images": ["https://images.unsplash.com/photo-1594895689718-d7482811a221?q=80&w=2600&auto=format&fit=crop"]
        },
        {
            "city": "تهران",
            "province": "تهران",
            "region": "CENTRAL",
            "best_seasons": ["spring", "fall"],
            "budget_min": "MEDIUM",
            "categories": ["شهری", "فرهنگی", "خرید", "موزه‌گردی", "شبگردی"],
            "suitable_for": ["BUSINESS", "SOLO", "FRIENDS"],
            "highlights": ["برج میلاد", "کاخ گلستان", "پل طبیعت"],
            "description": "تهران پایتخت مدرن و پرجنب‌وجوش ایران، ترکیبی از تاریخ قاجار و زندگی مدرن شهری.",
            "estimated_cost_3days": {"ECONOMY": 2000000, "MEDIUM": 3500000, "LUXURY": 7000000},
            "images": ["https://images.unsplash.com/photo-1569420650949-65391c49b6b7?q=80&w=2574&auto=format&fit=crop"]
        },
        {
            "city": "یزد",
            "province": "یزد",
            "region": "CENTRAL",
            "best_seasons": ["spring", "fall", "winter"],
            "budget_min": "ECONOMY",
            "categories": ["تاریخی", "معماری", "کویری", "آرامش"],
            "suitable_for": ["COUPLE", "FRIENDS", "SOLO"],
            "highlights": ["باغ دولت‌آباد", "مسجد جامع", "کویر کاراکال"],
            "description": "یزد، شهر بادگیرها و اولین شهر خشتی ثبت شده جهان، با آرامشی عجیب و کویرهای پرستاره.",
            "estimated_cost_3days": {"ECONOMY": 1300000, "MEDIUM": 2200000, "LUXURY": 4200000},
            "images": ["https://images.unsplash.com/photo-1628172909968-3d1425114440?q=80&w=2670&auto=format&fit=crop"]
        },
        {
            "city": "کاشان",
            "province": "اصفهان",
            "region": "CENTRAL",
            "best_seasons": ["spring", "fall"],
            "budget_min": "ECONOMY",
            "categories": ["تاریخی", "فرهنگی", "گلاب‌گیری"],
            "suitable_for": ["FAMILY", "COUPLE"],
            "highlights": ["خانه طباطبایی‌ها", "باغ فین", "تپه سیلک"],
            "description": "کاشان شهر گل و گلاب و خانه‌های تاریخی باشکوه، نگین کویر مرکزی ایران.",
            "estimated_cost_3days": {"ECONOMY": 1200000, "MEDIUM": 2000000, "LUXURY": 3500000},
            "images": ["https://images.unsplash.com/photo-1605634261778-5e5803274291?q=80&w=2670&auto=format&fit=crop"]
        },

        # --- SOUTH ---
        {
            "city": "شیراز",
            "province": "فارس",
            "region": "SOUTH",
            "best_seasons": ["spring", "winter"],
            "budget_min": "ECONOMY",
            "categories": ["تاریخی", "فرهنگی", "باغ", "ادبی"],
            "suitable_for": ["COUPLE", "FAMILY", "FRIENDS", "SOLO"],
            "highlights": ["تخت جمشید", "حافظیه", "نصیرالملک"],
            "description": "شیراز شهر شعر و ادب و بهارنارنج، پایتخت فرهنگی ایران با مردمی خونگرم.",
            "estimated_cost_3days": {"ECONOMY": 1400000, "MEDIUM": 2300000, "LUXURY": 4500000},
            "images": ["https://images.unsplash.com/photo-1596700085468-2b0475308643?q=80&w=2670&auto=format&fit=crop"]
        },
        {
            "city": "کیش",
            "province": "هرمزگان",
            "region": "SOUTH",
            "best_seasons": ["winter", "spring", "fall"],
            "budget_min": "MEDIUM",
            "categories": ["تفریحی", "ساحل", "خرید", "لوکس"],
            "suitable_for": ["COUPLE", "FRIENDS", "FAMILY"],
            "highlights": ["ساحل مرجان", "کشتی یونانی", "تفریحات آبی"],
            "description": "جزیره کیش، مروارید خلیج فارس، مدرن‌ترین مقصد گردشگری ایران با تفریحات آبی هیجان‌انگیز.",
            "estimated_cost_3days": {"ECONOMY": 3000000, "MEDIUM": 6000000, "LUXURY": 15000000},
            "images": []
        },
        {
            "city": "قشم",
            "province": "هرمزگان",
            "region": "SOUTH",
            "best_seasons": ["winter", "fall", "spring"],
            "budget_min": "ECONOMY",
            "categories": ["طبیعت", "خرید", "ماجراجویی"],
            "suitable_for": ["FRIENDS", "FAMILY", "SOLO"],
            "highlights": ["دره ستارگان", "جزایر ناز", "جنگل حرا"],
            "description": "قشم، بزرگترین جزیره خلیج فارس با عجایب هفتگانه طبیعی و بازارهای ارزان قیمت.",
            "estimated_cost_3days": {"ECONOMY": 2000000, "MEDIUM": 3500000, "LUXURY": 6000000},
            "images": []
        },
        {
            "city": "اهواز",
            "province": "خوزستان",
            "region": "SOUTH",
            "best_seasons": ["winter", "spring"],
            "budget_min": "ECONOMY",
            "categories": ["غذا", "شبگردی", "رودخانه"],
            "suitable_for": ["FRIENDS", "FAMILY"],
            "highlights": ["پل سفید", "لشکرآباد", "کارون"],
            "description": "اهواز شهر پل‌ها و فلافل، با شب‌های زنده در کنار رود همیشه خروشان کارون.",
            "estimated_cost_3days": {"ECONOMY": 1500000, "MEDIUM": 2500000, "LUXURY": 4000000},
            "images": []
        },

        # --- NORTH ---
        {
            "city": "رامسر",
            "province": "مازندران",
            "region": "NORTH",
            "best_seasons": ["summer", "spring", "fall"],
            "budget_min": "MEDIUM",
            "categories": ["طبیعت", "ساحل", "خانوادگی", "جنگل"],
            "suitable_for": ["FAMILY", "COUPLE"],
            "highlights": ["جواهرده", "تله‌کابین", "کاخ مرمر"],
            "description": "رامسر عروس شهرهای ایران، جایی که جنگل و دریا به هم می‌رسند.",
            "estimated_cost_3days": {"ECONOMY": 1800000, "MEDIUM": 3000000, "LUXURY": 6000000},
            "images": []
        },
        {
            "city": "رشت",
            "province": "گیلان",
            "region": "NORTH",
            "best_seasons": ["spring", "fall", "summer"],
            "budget_min": "ECONOMY",
            "categories": ["غذا", "فرهنگی", "طبیعت", "باران"],
            "suitable_for": ["FRIENDS", "FAMILY", "COUPLE"],
            "highlights": ["میدان شهرداری", "بازار بزرگ", "موزه میراث روستایی"],
            "description": "رشت شهر خلاق خوراک‌شناسی یونسکو، با باران‌های نقره‌ای و فرهنگ غنی گیلکی.",
            "estimated_cost_3days": {"ECONOMY": 1500000, "MEDIUM": 2500000, "LUXURY": 4500000},
            "images": []
        },
        {
            "city": "تبریز",
            "province": "آذربایجان شرقی",
            "region": "NORTH", # Geographically NW, putting in North bucket or needs WEST? Let's keep NORTH or create WEST.
            # Using WEST for Tabriz usually better, but if UI has only 5 regions. Assuming Tabriz is WEST.
            # Let's check available regions in Frontend: NORTH, SOUTH, EAST, WEST, CENTRAL.
            # So Tabriz -> WEST.
            # Wait, moving Tabriz to WEST section below.
            "city": "ماسوله",
            "province": "گیلان",
            "region": "NORTH",
            "best_seasons": ["spring", "summer"],
            "budget_min": "MEDIUM",
            "categories": ["طبیعت", "معماری", "روستایی"],
            "suitable_for": ["COUPLE", "FAMILY", "pHOTOGRAPHY"],
            "highlights": ["معماری پلکانی", "بازار سنتی", "آبشار"],
            "description": "ماسوله، شهرک تاریخی پلکانی در دل جنگل‌های مه آلود گیلان.",
            "estimated_cost_3days": {"ECONOMY": 1600000, "MEDIUM": 2800000, "LUXURY": 5000000},
            "images": []
        },


        # --- WEST ---
        {
            "city": "تبریز",
            "province": "آذربایجان شرقی",
            "region": "WEST",
            "best_seasons": ["summer", "spring"],
            "budget_min": "ECONOMY",
            "categories": ["تاریخی", "خرید", "فرهنگی", "شیرینی"],
            "suitable_for": ["FAMILY", "FRIENDS", "BUSINESS"],
            "highlights": ["بازار تبریز", "ایل‌گلی", "موزه آذربایجان"],
            "description": "تبریز شهر اولین‌ها، با بزرگترین بازار سرپوشیده جهان و شیرینی‌های بی‌نظیر.",
            "estimated_cost_3days": {"ECONOMY": 1400000, "MEDIUM": 2400000, "LUXURY": 4500000},
            "images": []
        },
        {
            "city": "همدان",
            "province": "همدان",
            "region": "WEST",
            "best_seasons": ["summer", "spring"],
            "budget_min": "ECONOMY",
            "categories": ["تاریخی", "طبیعت", "غار"],
            "suitable_for": ["FAMILY", "FRIENDS"],
            "highlights": ["غار علیصدر", "گنجنامه", "آرامگاه بوعلی"],
            "description": "همدان پایتخت تاریخ و تمدن ایران، با غارهای شگفت‌انگیز و کتیبه‌های باستانی.",
            "estimated_cost_3days": {"ECONOMY": 1300000, "MEDIUM": 2200000, "LUXURY": 4000000},
            "images": []
        },
        {
            "city": "کرمانشاه",
            "province": "کرمانشاه",
            "region": "WEST",
            "best_seasons": ["spring", "summer"],
            "budget_min": "ECONOMY",
            "categories": ["تاریخی", "طبیعت", "غذا"],
            "suitable_for": ["FRIENDS", "FAMILY", "SOLO"],
            "highlights": ["طاق بستان", "بیستون", "تکیه معاون‌الملک"],
            "description": "کرمانشاه گهواره تمدن، با آثار سنگی باشکوه و دنده کباب‌های معروف.",
            "estimated_cost_3days": {"ECONOMY": 1200000, "MEDIUM": 2000000, "LUXURY": 3500000},
            "images": []
        },

        # --- EAST ---
        {
            "city": "مشهد",
            "province": "خراسان رضوی",
            "region": "EAST",
            "best_seasons": ["spring", "summer", "fall"],
            "budget_min": "ECONOMY",
            "categories": ["مذهبی", "زیارتی", "خرید", "تفریحی"],
            "suitable_for": ["FAMILY", "COUPLE", "FRIENDS"],
            "highlights": ["حرم امام رضا", "شاندیز", "پارک آبی"],
            "description": "مشهد مقدس، پایتخت معنوی ایران با امکانات اقامتی و تفریحی بی‌نظیر.",
            "estimated_cost_3days": {"ECONOMY": 1200000, "MEDIUM": 2000000, "LUXURY": 4000000},
            "images": []
        },
        {
            "city": "کرمان",
            "province": "کرمان",
            "region": "EAST", # or SOUTH EAST, putting in EAST for simplicity
            "best_seasons": ["spring", "fall", "winter"],
            "budget_min": "ECONOMY",
            "categories": ["تاریخی", "کویری", "طبیعت"],
            "suitable_for": ["SOLO", "FRIENDS", "COUPLE"],
            "highlights": ["باغ شازده", "کویر لوت", "مجموعه گنجعلی‌خان"],
            "description": "کرمان دیار کریمان، با گرمترین نقطه زمین و باغ‌های جادویی در دل کویر.",
            "estimated_cost_3days": {"ECONOMY": 1300000, "MEDIUM": 2100000, "LUXURY": 3800000},
            "images": []
        }
    ]

    # امتیازدهی به هر مقصد
    scored_destinations = []

    for dest in destinations_db:
        score = 0
        reasons = []

        # 0. فیلتر منطقه (اگر مشخص شده باشد) - Hard Filter
        if region and region != dest.get("region"):
            continue

        # 1. فصل مناسب (+30)
        if season in dest["best_seasons"]:
            score += 30
            season_names = {
                "spring": "بهار",
                "summer": "تابستان",
                "fall": "پاییز",
                "winter": "زمستان"
            }
            reasons.append(f"هوابی عالی در {season_names[season]}")

        # 2. سبک سفر (+25)
        if travel_style in dest["suitable_for"]:
            score += 25
            style_names = {
                "SOLO": "تنها",
                "COUPLE": "زوج",
                "FAMILY": "خانوادگی",
                "FRIENDS": "با دوستان",
                "BUSINESS": "کاری"
            }
            reasons.append(f"مناسب سفر {style_names[travel_style]}")

        # 3. تطبیق علایق (+15 برای هر تطبیق)
        interest_matches = 0
        for interest in interests:
            # Simple substring checking or exact match
            if any(interest in cat for cat in dest["categories"]):
                interest_matches += 1
                score += 15

        if interest_matches > 0:
            reasons.append(f"{interest_matches} مورد جاذبه‌های مورد علاقه")

        # 4. بودجه (+20 اگر مناسب باشد)
        budget_order = ["ECONOMY", "MEDIUM", "LUXURY", "UNLIMITED"]
        try:
            dest_budget_idx = budget_order.index(dest["budget_min"])
            user_budget_idx = budget_order.index(budget_level)

            if user_budget_idx >= dest_budget_idx:
                score += 20
                if user_budget_idx == dest_budget_idx:
                    reasons.append("کاملاً متناسب با بودجه شما")
            else:
                score -= 30  # جریمه برای گران‌تر بودن
        except ValueError:
             score += 10 # Default behavior if budget data invalid

        # 5. امتیاز پایه (+10)
        score += 10

        # ساخت نتیجه
        if score > 0:  # فقط مقاصد با امتیاز مثبت
            scored_destinations.append({
                "city": dest["city"],
                "province": dest["province"],
                "score": score,
                "reason": " | ".join(reasons[:2]),  # 2 دلیل اصلی
                "highlights": dest["highlights"],
                "best_season": dest["best_seasons"][0],
                "estimated_cost": str(dest["estimated_cost_3days"].get(budget_level, dest["estimated_cost_3days"]["MEDIUM"])),
                "duration_days": 3,
                "description": dest["description"],
                "images": dest["images"],
                "categories": dest["categories"],
                "region": dest["region"]
            })

    # مرتب‌سازی بر اساس امتیاز
    scored_destinations.sort(key=lambda x: x["score"], reverse=True)

    # برگرداندن 3 مقصد برتر (یا کمتر اگر پیدا نشد)
    return scored_destinations[:3]


# =======================================================================================
# API 4: محاسبه هزینه (Cost Calculation Service)
# =======================================================================================

def calculate_trip_cost(trip_id: int) -> Dict:
    """
    Service Function: calculate_trip_cost(trip_id)

    محاسبه هزینه - محاسبه و آپدیت هزینه کل Trip

    منطق:
    1. جمع estimated_cost تمام Items در Trip
    2. آپدیت فیلد total_estimated_cost در Trip
    3. برگرداندن breakdown به تفکیک:
       - Category (DINING, STAY, HISTORICAL, ...)
       - Day (روز به روز)

    ورودی:
    - trip_id: شناسه Trip

    خروجی:
    {
        "trip_id": 123,
        "total_cost": 2500000.00,
        "breakdown_by_category": {
            "DINING": {
                "amount": 800000,
                "percentage": 32.0,
                "count": 5
            },
            "STAY": {
                "amount": 1500000,
                "percentage": 60.0,
                "count": 3
            }
        },
        "breakdown_by_day": [
            {
                "day_index": 1,
                "date": "2026-03-15",
                "cost": 850000
            }
        ]
    }

    وابستگی:
    - خوانده می‌شود توسی APIهای سیدعلی (cost_breakdown endpoint)
    - خوانده می‌شود بعد از replace item
    """
    from django.db.models import Sum, Count
    from data.models import Trip, TripDay, TripItem

    # 1. دریافت Trip
    try:
        trip = Trip.objects.get(trip_id=trip_id)
    except Trip.DoesNotExist:
        return {
            "error": "Trip not found",
            "error_fa": "سفر یافت نشد"
        }

    # 2. محاسبه هزینه کل
    items = TripItem.objects.filter(day__trip=trip)
    total_cost = items.aggregate(
        total=Sum('estimated_cost')
    )['total'] or Decimal('0.00')

    # 3. آپدیت Trip
    trip.total_estimated_cost = total_cost
    trip.save(update_fields=['total_estimated_cost'])

    # 4. Breakdown by category
    category_breakdown = items.values('category').annotate(
        amount=Sum('estimated_cost'),
        count=Count('item_id')
    )

    breakdown_by_category = {}
    for item in category_breakdown:
        category = item['category'] or 'OTHER'
        amount = item['amount'] or Decimal('0.00')
        percentage = float((amount / total_cost * 100) if total_cost > 0 else 0)

        breakdown_by_category[category] = {
            "amount": float(amount),
            "percentage": round(percentage, 2),
            "count": item['count']
        }

    # 5. Breakdown by day
    days = TripDay.objects.filter(trip=trip).order_by('day_index')
    breakdown_by_day = []

    for day in days:
        day_items = items.filter(day=day)
        day_cost = day_items.aggregate(
            total=Sum('estimated_cost')
        )['total'] or Decimal('0.00')

        breakdown_by_day.append({
            "day_index": day.day_index,
            "date": day.specific_date.isoformat(),
            "cost": float(day_cost),
            "items_count": day_items.count()
        })

    # 6. برگرداندن نتیجه
    return {
        "trip_id": trip_id,
        "total_cost": float(total_cost),
        "breakdown_by_category": breakdown_by_category,
        "breakdown_by_day": breakdown_by_day,
        "items_count": items.count()
    }


# API endpoint wrapper for calculate_trip_cost
@api_view(['GET'])
def get_trip_cost_breakdown(request, trip_id):
    """
    GET /api/trips/{trip_id}/cost/

    API endpoint برای دریافت breakdown هزینه Trip
    """
    try:
        result = calculate_trip_cost(int(trip_id))

        if "error" in result:
            return Response(result, status=status.HTTP_404_NOT_FOUND)

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {
                "error": f"Failed to calculate cost: {str(e)}",
                "error_fa": "خطا در محاسبه هزینه"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
