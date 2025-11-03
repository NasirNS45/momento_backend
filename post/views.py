from django.db.models import Q
from django.db.models.aggregates import Count
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema_view, extend_schema

from post.models import Post, Comment, PostLike, CommentLike
from post.serializers import (
    PostListSerializer,
    PostCreateSerializer,
    CommentListSerializer,
    CommentCreateSerializer,
    PostLikeListSerializer,
)
from user.models import Follow


@extend_schema_view(
    list=extend_schema(tags=["posts"], description="List all posts"),
    retrieve=extend_schema(tags=["posts"], description="Retrieve a single post"),
    create=extend_schema(tags=["posts"], description="Create a new post"),
    like=extend_schema(tags=["posts"], description="Like a post"),
    comment=extend_schema(tags=["posts"], description="Comment on a post"),
    comments=extend_schema(tags=["posts"], description="List all comments on a post"),
    likes=extend_schema(tags=["posts"], description="List all likes on a post"),
    destroy=extend_schema(tags=["posts"], description="Delete a post"),
    partial_update=extend_schema(tags=["posts"], description="Update a post"),
)
class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        # Get all follow relationships involving the current user (accepted only)
        relations = Follow.objects.filter(
            Q(follower=self.request.user) | Q(followed=self.request.user),
            status=Follow.Status.ACCEPTED
        ).values_list("followed_id", "follower_id")

        # Build a set of user IDs (you follow OR who follow you)
        user_ids = {uid for pair in relations for uid in pair}

        # Return posts of those users
        return (
            self.queryset.select_related("user")
            .prefetch_related("media", "likes", "comments")
            .filter(user_id__in=user_ids)
            .annotate(
                likes_count=Count("likes", distinct=True),
                comments_count=Count("comments", distinct=True),
            )
        )

    def get_serializer_class(self):
        action_mapping = {
            "list": PostListSerializer,
            "retrieve": PostListSerializer,
            "create": PostCreateSerializer,
        }
        return action_mapping.get(self.action, self.serializer_class)

    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        post = self.get_object()
        PostLike.objects.get_or_create(user=request.user, post=post)
        return Response({"message": "Post liked successfully"})

    @action(detail=True, methods=["post"], serializer_class=CommentCreateSerializer)
    def comment(self, request, pk=None):
        post = self.get_object()
        serializer = CommentCreateSerializer(
            data=request.data, context={"user": request.user, "post": post}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Comment posted successfully"})

    @action(detail=True, methods=["get"])
    def comments(self, request, pk=None):
        post = self.get_object()
        comments = (
            post.comments.select_related("user")
            .prefetch_related("replies", "comment_likes")
            .all().annotate(replies_count=Count("replies"), comment_likes_count=Count("comment_likes"))
        )
        return Response(CommentListSerializer(comments, many=True).data)

    @action(detail=True, methods=["get"])
    def likes(self, request, pk=None):
        post = self.get_object()
        likes = post.post_likes.select_related("user").all()
        return Response(PostLikeListSerializer(likes, many=True).data)


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    http_method_names = ["get", "post"]

    def get_serializer_class(self):
        action_mapping = {
            "list": CommentListSerializer,
            "retrieve": CommentListSerializer,
        }
        return action_mapping.get(self.action, self.serializer_class)

    @action(detail=True, methods=["post"])
    def replies(self, request, pk=None):
        comment = self.get_object()
        replies = comment.replies.all()
        return Response(CommentListSerializer(replies, many=True).data)

    @action(detail=True, methods=["post"])
    def likes(self, request, pk=None):
        comment = self.get_object()
        likes = comment.comment_likes.all()
        return Response(CommentListSerializer(likes, many=True).data)

    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        comment = self.get_object()
        CommentLike.objects.get_or_create(user=request.user, comment=comment)
        return Response({"message": "Comment liked successfully"})
