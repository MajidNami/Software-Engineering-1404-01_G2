from django.urls import path, re_path
from . import views
from .views import error_404, error_500, error_403, error_400 # ایمپورت ویوهای خطا
app_name = "team6"
from django.views.decorators.cache import never_cache
from .views import (
    follow_article, toggle_notification, notifications_list,
    mark_notification_read, archive_notification, mark_all_read,
    archive_all_notifications
)

urlpatterns = [
    # صفحه اصلی تیم 6 (لیست مقالات)
    path("", never_cache(views.ArticleListView.as_view()), name="index"),
    
    # ویو پایه / API پایه
    path("ping/", views.ping, name="ping"),
    
    # اضافه کردن مقاله
    path("create/", views.ArticleCreateView.as_view(), name="article_add"),
    
    # جزئیات مقاله با slug
    re_path(r'^article/(?P<slug>[^/]+)/$', views.article_detail, name='article_detail'),
    
    # ویرایش مقاله
    re_path(r'^article/(?P<slug>[^/]+)/edit/$', views.edit_article, name="article_edit"),
    
    #حذف مقاله
    re_path(r'^article/(?P<slug>[^/]+)/delete/$', views.delete_article, name="article_delete"),
    
    # نمایش نسخه‌ها
    re_path(r'^article/(?P<slug>[^/]+)/revisions/$', views.article_revisions, name="article_revisions"),
    
    # گزارش مقاله با slug (ساده‌ترین راه)
    re_path(r'^article/(?P<slug>[^/]+)/report/$', views.report_article, name="article_report"),
    
    # API خارجی برای محتوا
    path("api/wiki/content", views.get_wiki_content, name="external_api"),

    
    re_path(
        r'^article/(?P<slug>[^/]+)/revisions/(?P<revision_no>\d+)/$',
        views.article_revision_detail,
        name="article_revision_detail"
    ),
    path("api/preview-ai/", views.preview_ai_content, name='preview_ai'),
    re_path(r'^article/(?P<slug>[^/]+)/follow/$', follow_article, name="article_follow"),
    re_path(r'^article/(?P<slug>[^/]+)/toggle-notify/$', toggle_notification, name="toggle_notify"),
    path("notifications/", notifications_list, name="notifications_list"),
    path("notifications/<uuid:notification_id>/read/", mark_notification_read, name="mark_notification_read"),
    path("notifications/<uuid:notification_id>/archive/", archive_notification, name="archive_notification"),
    path("notifications/mark-all-read/", mark_all_read, name="mark_all_read"),
    path("notifications/archive-all/", archive_all_notifications, name="archive_all_notifications"),
    path('drafts/', views.draft_list, name='draft_list'),
    re_path(r'^article/(?P<slug>[^/]+)/rollback/(?P<revision_no>\d+)/$', views.rollback_revision, name='rollback'),
]


handler404 = 'team6.views.error_404'
handler500 = 'team6.views.error_500'
handler403 = 'team6.views.error_403'
handler400 = 'team6.views.error_400'