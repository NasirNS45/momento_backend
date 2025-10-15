from rest_framework import serializers
from user.models import User, Profile


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    name = serializers.CharField()
    username = serializers.CharField()
    date_of_birth = serializers.DateField()

    @staticmethod
    def validate_email(value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    @staticmethod
    def validate_username(value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.IntegerField()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UpdateUserSerializer(serializers.Serializer):
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    cover_picture = serializers.ImageField(required=False, allow_null=True)
    bio = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    website = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    gender = serializers.ChoiceField(
        choices=Profile.Gender.choices, required=False, allow_null=True
    )


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    name = serializers.CharField()
    profile_picture = serializers.SerializerMethodField()

    @staticmethod
    def get_profile_picture(obj):
        profile = getattr(obj, "profile", None)
        return (
            obj.profile.profile_picture.url
            if profile and profile.profile_picture
            else None
        )


class FollowRequestSerializer(serializers.Serializer):
    followed_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())


class FollowRequestActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["accept", "reject"])
