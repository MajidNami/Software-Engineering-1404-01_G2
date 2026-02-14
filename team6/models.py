from django.db import models
import uuid

# Create your models here.

class WikiCategory(models.Model):
    id_category = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True)
    title_fa = models.TextField()
    title_en = models.TextField(null=True, blank=True)

    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'wiki_categories'


class WikiTag(models.Model):
    id_tag = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField()
    title_fa = models.TextField()
    title_en = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    related_tags = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True
    )

    class Meta:
        db_table = 'wiki_tags'
# مدل اصلی مقاله؛ شامل وضعیت انتشار، نسخه‌بندی (revision) و شاخص‌های کیفیت/بازدید برای رتبه‌بندی و نمایش.
class WikiArticle(models.Model):
    id_article = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    place_name = models.CharField(null=True,max_length=255, blank = True)

    slug = models.SlugField(null=True,unique=True)  # مثلا: si-o-se-pol

    title_fa = models.TextField()
    title_en = models.TextField(null=True, blank=True)

    body_fa = models.TextField()
    body_en = models.TextField(null=True, blank=True)

    summary = models.TextField(null=True, blank=True)

    featured_image_url = models.URLField(null=True, blank=True)
    url = models.URLField(unique=True)

    category = models.ForeignKey(WikiCategory, on_delete=models.PROTECT)

    tags = models.ManyToManyField(WikiTag, related_name='articles', blank=True)

    # شناسه کاربر از سرویس احراز هویت می‌آید (ForeignKey نیست تا وابستگی مستقیم بین سرویس‌ها ایجاد نشود).
    author_user_id = models.UUIDField(null=True)
    last_editor_user_id = models.UUIDField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True)

    status = models.CharField(max_length=20, default='draft')

    quality_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    quality_count = models.IntegerField(default=0)

    # شماره نسخه فعلی برای دسترسی سریع؛ جزئیات هر نسخه در جدول WikiArticleRevision ذخیره می‌شود.
    current_revision_no = models.IntegerField(default=1)
    view_count = models.IntegerField(default=0)
    class Meta:
        db_table = 'wiki_articles'


class WikiArticleLink(models.Model):
    id_link = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    from_article = models.ForeignKey(WikiArticle, related_name='outgoing_links', on_delete=models.CASCADE)
    to_article = models.ForeignKey(WikiArticle, related_name='incoming_links', on_delete=models.CASCADE)
    anchor_text = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'wiki_article_links'
        # جلوگیری از ثبت لینک تکراری بین دو مقاله (from -> to).
        unique_together = ('from_article', 'to_article')


class WikiArticleRef(models.Model):
    id_ref = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey(WikiArticle, on_delete=models.CASCADE)

    title = models.TextField(null=True)
    url = models.URLField() 
    publisher = models.TextField(null=True)
    published_at = models.DateTimeField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'wiki_article_refs'


class WikiArticleRevision(models.Model):
    id_revision = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey(WikiArticle, on_delete=models.CASCADE)

    revision_no = models.IntegerField()
    editor_user_id = models.UUIDField(null=True)
    change_note = models.TextField(null=True)

    body_fa = models.TextField()
    body_en = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'wiki_article_revisions'
        unique_together = ('article', 'revision_no')


class WikiArticleReports(models.Model):
    id_report = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey(
        WikiArticle,
        on_delete=models.CASCADE,
        db_column='id_article',
        related_name='reports'
    )
    reporter_user_id = models.UUIDField()  # کاربر گزارش‌دهنده
    report_type = models.TextField()       # نوع گزارش
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'wiki_article_reports'
        unique_together = ('article', 'reporter_user_id')
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]

class ArticleFollow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()
    article = models.ForeignKey('WikiArticle', on_delete=models.CASCADE)
    notify = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'article_follows'
        unique_together = ('user_id', 'article')

class ArticleNotification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()
    article = models.ForeignKey('WikiArticle', on_delete=models.CASCADE)
    notification_type = models.CharField(
        max_length=50,
        choices=[
            ('edit', 'ویرایش متن'),
            ('image', 'افزودن/تغییر تصویر'),
            ('tags', 'تغییر برچسب'),
            ('category', 'تغییر دسته'),
            ('new', 'مقاله جدید')
        ]
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'article_notifications'
        indexes = [
            models.Index(fields=['user_id', 'is_read', 'created_at']),
        ]