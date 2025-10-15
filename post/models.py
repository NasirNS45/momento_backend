from django.db import models

from momento.core.models import BaseModel


class Post(BaseModel):
    class Type(models.TextChoices):
        POST = "post", "Post"
        REEL = "reel", "Reel"

    user = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name="posts"
    )
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.POST)
    caption = models.TextField(blank=True, null=True)
    hashtags = models.ManyToManyField("Hashtag", related_name="posts", blank=True)
    allow_comments = models.BooleanField(default=True)
    hide_likes_views_count = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.type}"


def media_upload_to(instance, filename):
    return f"{instance.post.id}/{filename}"


class Media(BaseModel):
    class Type(models.TextChoices):
        IMAGE = "image", "Image"
        VIDEO = "video", "Video"

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="media")
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.IMAGE)
    file = models.FileField(upload_to=media_upload_to)
    position = models.PositiveIntegerField(default=0)  # order in the carousel

    class Meta:
        ordering = ["position"]


class PostLike(BaseModel):
    user = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name="likes"
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user.username} - {self.post}"


class Comment(BaseModel):
    user = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name="comments"
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.post}"


class CommentLike(BaseModel):
    user = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name="comment_likes"
    )
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="comment_likes"
    )

    class Meta:
        unique_together = ("user", "comment")

    def __str__(self):
        return f"{self.user.username} - {self.comment}"


class Hashtag(BaseModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"#{self.name}"


class Mention(BaseModel):
    user = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name="mentions"
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, null=True, blank=True, related_name="mentions"
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="mentions",
    )

    def __str__(self):
        return f"{self.user.username} - {self.post}"


class View(BaseModel):
    user = models.ForeignKey(
        "user.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="views",
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="views")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user.username} - {self.post}"
