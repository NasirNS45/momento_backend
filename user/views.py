from rest_framework import generics, status, permissions
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import User, OTP, Follow
from user.serializers import (
    RegisterSerializer,
    LoginSerializer,
    VerifyOTPSerializer,
    FollowRequestSerializer,
    FollowRequestActionSerializer,
    UserSerializer,
)
from utils.helpers import send_mail


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    http_method_names = ["post"]
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.create(**serializer.validated_data, is_active=False)
        user.set_password(serializer.validated_data["password"])
        user.save()

        otp = OTP.objects.create(user=user)
        send_mail(user.email, "OTP", f"Your OTP is {otp.code}")

        return Response(
            {"message": "An OTP has been sent to your email."},
            status=status.HTTP_201_CREATED,
        )


class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    http_method_names = ["post"]
    serializer_class = VerifyOTPSerializer

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"message": "No account found"}, status=404)
        if user.is_active:
            return Response({"message": "Account already verified"}, status=400)

        otp = OTP.objects.filter(user=user, code=code).first()
        if not otp:
            return Response({"message": "Invalid OTP"}, status=400)
        if otp.is_expired():
            return Response({"message": "OTP has expired"}, status=400)

        user.is_active = True
        user.save()
        otp.delete()

        return Response({"message": "OTP verified successfully"})


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    http_method_names = ["post"]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(**serializer.validated_data)
        if not user:
            raise AuthenticationFailed(
                detail="Invalid credentials", code="authentication_failed"
            )

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return Response(
            {
                "access": str(access),
                "refresh": str(refresh),
            }
        )


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get"]
    serializer_class = UserSerializer

    def get(self, request):
        user = request.user
        return Response(UserSerializer(user).data)


class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(
            ~Q(id=self.request.user.id), ~Q(is_staff=True)
        ).order_by("-id")


class SuggestedUserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        follower = Follow.objects.filter(
            Q(followed=self.request.user) | Q(follower=self.request.user)
        ).only("followed_id", "follower_id")
        user_ids = set()
        for follow in follower:
            user_ids.add(follow.followed_id)
            user_ids.add(follow.follower_id)
        return User.objects.filter(
            ~Q(id=self.request.user.id), ~Q(is_staff=True), ~Q(id__in=user_ids)
        ).order_by("-id")


class FollowRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["post"]
    serializer_class = FollowRequestSerializer

    def post(self, request):
        serializer = FollowRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        followed_user = User.objects.filter(
            id=serializer.validated_data["followed_id"].id
        ).first()
        if not followed_user:
            return Response({"message": "User not found"}, status=404)

        status_choice = (
            Follow.Status.ACCEPTED if followed_user.is_public else Follow.Status.PENDING
        )

        Follow.objects.create(
            followed=followed_user,
            follower=request.user,
            status=status_choice,
        )

        return Response({"message": "Followed successfully"})


# Accept/Reject Follow Request
class FollowRequestActionView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["post"]
    serializer_class = FollowRequestActionSerializer

    def post(self, request, follow_id):
        serializer = FollowRequestActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        follow = Follow.objects.filter(id=follow_id).first()
        if not follow:
            return Response({"message": "Follow request not found"}, status=404)

        if request.user != follow.followed:
            return Response(
                {
                    "message": "You are not authorized to accept/reject this follow request"
                },
                status=401,
            )

        action = serializer.validated_data["action"]
        if action == "accept":
            follow.status = Follow.Status.ACCEPTED
            follow.save()
        else:
            follow.delete()

        return Response({"message": "Follow request status updated successfully"})
