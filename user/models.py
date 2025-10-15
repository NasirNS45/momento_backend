import random

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils import timezone

from momento.core.models import BaseModel


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    date_of_birth = models.DateField(null=True, blank=True)
    is_public = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Profile(BaseModel):
    class Gender(models.TextChoices):
        MALE = "male"
        FEMALE = "female"
        PREFER_NOT_TO_SAY = "prefer_not_to_say"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField()
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", blank=True, null=True
    )
    cover_picture = models.ImageField(
        upload_to="cover_pictures/", blank=True, null=True
    )
    website = models.URLField(blank=True, null=True)
    gender = models.CharField(
        max_length=20, choices=Gender.choices, default=Gender.PREFER_NOT_TO_SAY
    )

    def __str__(self):
        return self.user.email


class OTP(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)

    def __str__(self):
        if self.is_expired():
            return f"{self.user} - {self.code} - Expired"
        return f"{self.user} - {self.code}"

    def is_expired(self):
        return self.created_at + timezone.timedelta(minutes=5) < timezone.now()

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = random.randint(100000, 999999)
        super().save(*args, **kwargs)


class Follow(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending"
        ACCEPTED = "accepted"

    followed = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followers",
        help_text="Person being followed",
    )
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        help_text="Person who follows",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["followed", "follower"], name="unique_follow"
            )
        ]
