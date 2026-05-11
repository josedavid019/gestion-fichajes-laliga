from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("me/", views.current_user, name="current_user"),
    path("check-auth/", views.check_auth, name="check_auth"),
    path("profile/", views.profile_detail, name="profile_detail"),
    path("audit-logs/", views.audit_logs, name="audit_logs"),
]
