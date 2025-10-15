from django.contrib import admin

from .models import Post, Comment, PostLike, CommentLike, Media


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "caption",
        "type",
        "allow_comments",
        "hide_likes_views_count",
    ]
    list_filter = ["user", "type", "allow_comments", "hide_likes_views_count"]
    search_fields = ["caption"]


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ["id", "post", "type", "position"]
    list_filter = ["post", "type", "position"]
    search_fields = ["post__caption"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "post", "content", "parent"]
    list_filter = ["user", "post", "parent__content"]
    search_fields = ["content", "user__email", "post__caption"]


@admin.register(PostLike)
class LikeAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "post"]
    list_filter = ["user", "post"]
    search_fields = ["user__email", "post__caption"]


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "comment"]
    list_filter = ["user", "comment"]
    search_fields = ["user__email", "comment__content"]
