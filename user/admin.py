from django.contrib import admin

from .models import User, Profile, OTP, Follow


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "is_staff", "is_active", "is_superuser"]
    list_filter = ["is_staff", "is_active", "is_superuser"]
    search_fields = ["email"]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "bio",
        "profile_picture",
        "cover_picture",
        "website",
        "gender",
    ]
    list_filter = ["gender"]
    search_fields = ["bio"]


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ["user", "code", "is_expired"]
    search_fields = ["code"]


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ["followed", "follower", "status"]
    list_filter = ["status"]
    search_fields = ["followed__email", "follower__email"]
