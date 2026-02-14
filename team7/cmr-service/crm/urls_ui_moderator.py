from django.urls import path
from crm.controllers import moderator_ui

urlpatterns = [
    path("moderator/", moderator_ui.moderator_dashboard, name="ui_moderator_dashboard"),
]
