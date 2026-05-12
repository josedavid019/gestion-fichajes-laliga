from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("me/", views.current_user, name="current_user"),
    path("check-auth/", views.check_auth, name="check_auth"),
    path("profile/", views.profile_detail, name="profile_detail"),
    path("audit-logs/", views.audit_logs, name="audit_logs"),
    path("roles/", views.role_list_create, name="role_list_create"),
    path("roles/<int:pk>/", views.role_detail, name="role_detail"),
    path("users/", views.user_list_create, name="user_list_create"),
    path("users/<int:pk>/", views.user_detail, name="user_detail"),
]
