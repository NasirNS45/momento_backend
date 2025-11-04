from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from user.views import (
    RegisterView,
    VerifyOTPView,
    LoginView,
    MeView,
    UserListView,
    FollowRequestView,
    FollowRequestActionView,
    SuggestedUserListView,
    OverviewView
)

urlpatterns = [
    path("token/", LoginView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify_otp"),
    path("me/", MeView.as_view(), name="me"),
    path("overview/", OverviewView.as_view(), name="overview"),
    path("suggested-users/", SuggestedUserListView.as_view(), name="suggested_users"),
    path("users/", UserListView.as_view(), name="users"),
    path("follow-request/", FollowRequestView.as_view(), name="follow_request"),
    path(
        "follow-request-action/<int:follow_id>/",
        FollowRequestActionView.as_view(),
        name="follow_request_action",
    ),
]
