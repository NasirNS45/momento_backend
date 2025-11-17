from typing import Dict, Any, List

import arrow
from rest_framework import serializers

from post.models import Post, Media, Comment, PostLike, Hashtag
from user.models import User
from user.serializers import UserSerializer
from utils.helpers import get_media_type


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ["id", "file", "type", "position"]

    def to_representation(self, instance: "Media") -> Dict[str, Any]:
        data = super().to_representation(instance)
        url: str = self.context["request"].build_absolute_uri(instance.file.url)
        if "media/media" in url:
            url = url.replace("/media", "", 1)
        data["file"] = url
        return data


class PostListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    created_ago = serializers.SerializerMethodField()
    media = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "user", "created_ago", "caption", "media", "likes", "comments"]

    @staticmethod
    def get_user(obj: "Post") -> UserSerializer:
        return UserSerializer(obj.user).data

    @staticmethod
    def get_created_ago(obj: "Post") -> str:
        return arrow.get(obj.created_at).humanize()

    def get_media(self, obj: "Post") -> List[MediaSerializer]:
        return MediaSerializer(
            obj.media.all(), many=True, context=self.context
        ).data

    @staticmethod
    def get_likes(obj: "Post") -> int:
        return getattr(obj, "likes_count", 0)

    @staticmethod
    def get_comments(obj: "Post") -> int:
        return getattr(obj, "comments_count", 0)


class CSVField(serializers.Field):
    def to_internal_value(self, data: str | list):
        return data.split(",") if isinstance(data, str) else data

    def to_representation(self, value: str | list):
        return value.split(",") if isinstance(value, str) else value


class PostCreateSerializer(serializers.Serializer):
    caption = serializers.CharField(max_length=255, allow_blank=True, allow_null=True, required=False)
    media = serializers.ListField(child=serializers.FileField(), write_only=True)
    hashtags = CSVField(
        required=False,
        allow_null=True,
        write_only=True
    )
    type = serializers.ChoiceField(choices=Post.Type.choices, required=False)
    allow_comments = serializers.BooleanField(default=True)
    hide_likes_views_count = serializers.BooleanField(default=False)

    def create(self, validated_data: Dict[str, Any]) -> Post:
        caption = validated_data.get("caption", "")
        media = validated_data.get("media", [])
        hashtags = validated_data.get("hashtags", [])
        post_type = validated_data.get("type", Post.Type.POST)
        allow_comments = validated_data.get("allow_comments", True)
        hide_likes_views_count = validated_data.get("hide_likes_views_count", False)
        if hashtags:
            names = [h.strip() for h in hashtags]
            hashtags = [Hashtag(name=name) for name in names]
            Hashtag.objects.bulk_create(hashtags, ignore_conflicts=True)
            hashtags = Hashtag.objects.filter(name__in=names)
        post = Post.objects.create(
            user=self.context["request"].user,
            caption=caption,
            type=post_type,
            allow_comments=allow_comments,
            hide_likes_views_count=hide_likes_views_count,
        )
        post.hashtags.set(hashtags)
        media_objs = []
        for index, file in enumerate(media):
            media_type = get_media_type(file)
            media_obj = Media(post=post, file=file, type=media_type, position=index)
            media_objs.append(media_obj)
        if media_objs:
            Media.objects.bulk_create(media_objs)
        return post


class CommentListSerializer(serializers.Serializer):
    user = serializers.SerializerMethodField()
    content = serializers.CharField()
    created_ago = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()

    @staticmethod
    def get_user(obj: "Comment") -> UserSerializer:
        return UserSerializer(obj.user).data

    @staticmethod
    def get_created_ago(obj: "Comment") -> str:
        return arrow.get(obj.created_at).humanize()

    @staticmethod
    def get_replies(obj: "Comment") -> int:
        return getattr(obj, "replies_count", 0)

    @staticmethod
    def get_likes(obj: "Comment") -> int:
        return getattr(obj, "comment_likes_count", 0)


class CommentCreateSerializer(serializers.Serializer):
    content = serializers.CharField()
    reply_to = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.all(), required=False, allow_null=True
    )

    def create(self, validated_data: Dict[str, Any]) -> Comment:
        user = self.context.get("user")
        post = self.context.get("post")
        content = validated_data.get("content", "")
        reply_to = validated_data.get("reply_to", None)
        return Comment.objects.create(
            user=user,
            content=content,
            parent=reply_to,
            post=post,
        )


class PostLikeListSerializer(serializers.Serializer):
    user = serializers.SerializerMethodField()
    created_ago = serializers.SerializerMethodField()

    @staticmethod
    def get_user(obj: "PostLike") -> UserSerializer:
        return UserSerializer(obj.user).data

    @staticmethod
    def get_created_ago(obj: "PostLike") -> str:
        return arrow.get(obj.created_at).humanize()
