from django.urls import path
from .controllers.trip_controller import (
    TripController,
    TripBudgetAnalysisController,
    TripConfirmController
)

app_name = 'trip_api'

urlpatterns = [
    # Trip CRUD operations
    path('trips/', TripController.as_view(), name='trip_create'),
    path('trips/<int:trip_id>/', TripController.as_view(), name='trip_detail'),
    path('trips/<int:trip_id>/regenerate/', TripController.as_view(), name='trip_regenerate'),

    # Budget analysis
    path('trips/<int:trip_id>/budget-analysis/', TripBudgetAnalysisController.as_view(), name='trip_budget_analysis'),

    # Trip confirmation
    path('trips/<int:trip_id>/confirm/', TripConfirmController.as_view(), name='trip_confirm'),
]
