from django.urls import path
from .views import test,ok

urlpatterns = [
    path("test/", test),
    path("trip-plan/trips",ok)
]
