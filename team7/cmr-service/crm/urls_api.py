from django.urls import path
from crm.controllers import api

urlpatterns = [
    path("comments/", api.comments, name="api_comments"),
    path("comments/<str:comment_id>/status/", api.comment_status, name="api_comment_status"),
    path("ratings/", api.post_rate, name="api_post_rate"),
    path("ratings/avg/", api.get_avg_rate, name="api_get_avg_rate"),
    path("ratings/my/", api.get_my_rate, name="api_get_my_rate"),
    path("reports/", api.report, name="api_report"),
    path("reports/pending/", api.pending_reports, name="api_pending_reports"),
    path("reports/<str:report_id>/status/", api.report_status, name="api_report_status"),
    path("targets/<str:target_id>/name/", api.target_name, name="api_target_name"),
    path("media/", api.media, name="api_media"),
    path("media/<str:media_id>/status/", api.media_status, name="api_media_status"),
]
