from django.urls import path
from crm.controllers import ui
from django.urls import include, path

urlpatterns = [
    # ...your existing UI routes...
    path("", include("crm.urls_ui_moderator")),
    path("target/<str:target_id>/user/<str:user_id>/", ui.target_interaction, name="ui_target"),
    path("moderation/<str:moderator_id>/", ui.moderation_home, name="ui_moderation"),
]
