"""
URL configuration for app404 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from core.web_views import home
from core.web_auth_views import login_page, signup_page, logout_page

urlpatterns = [
    path("", home, name="home"),
    path("auth/", login_page, name="auth"),
    path("auth/signup/", signup_page, name="signup"),
    path("auth/logout/", logout_page, name="logout"),
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),
    
    path("team9/", include("team9.urls")),
    path("team4/", include("team4.urls")),

]
