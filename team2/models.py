from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    creator_id = models.UUIDField()
    current_version = models.OneToOneField('Version', on_delete=models.SET_NULL, null=True, blank=True, related_name='current_of')
    score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class Version(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='versions')
    content = models.TextField(blank=True, default='')
    summary = models.TextField(blank=True, default='')
    editor_id = models.UUIDField()
    tags = models.ManyToManyField(Tag, blank=True, related_name='versions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class PublishRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    version = models.ForeignKey(Version, on_delete=models.CASCADE, related_name='publish_requests')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='publish_requests')
    requester_id = models.UUIDField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('version', 'requester_id')

    def __str__(self):
        return f"{self.requester_id} -> {self.version.name}: {self.status}"


class Vote(models.Model):
    user_id = models.UUIDField()
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='votes')
    value = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user_id', 'article')

    def __str__(self):
        return f"{self.user_id} -> {self.article_id}: {self.value}"
