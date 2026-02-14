from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from .models import WikiArticle, WikiCategory, WikiTag, WikiArticleRevision, WikiArticleReports

# ۱. نمایش تاریخچه ویرایش‌ها به صورت درختی در داخل صفحه مقاله
class RevisionInline(admin.TabularInline):
    model = WikiArticleRevision
    extra = 0
    readonly_fields = ('revision_no', 'editor_user_id', 'created_at')
    can_delete = False

# ۲. مدیریت دسته‌بندی‌ها
@admin.register(WikiCategory)
class WikiCategoryAdmin(admin.ModelAdmin):
    list_display = ('title_fa', 'slug', 'parent', 'created_at')
    search_fields = ('title_fa', 'slug')
    prepopulated_fields = {'slug': ('title_fa',)}

# ۳. مدیریت تگ‌ها
@admin.register(WikiTag)
class WikiTagAdmin(admin.ModelAdmin):
    list_display = ('title_fa', 'slug')
    search_fields = ('title_fa',)

# ۴. مدیریت اصلی مقالات (بخش پیشرفته)
@admin.register(WikiArticle)
class WikiArticleAdmin(admin.ModelAdmin):
    # فیلدهایی که در لیست اصلی نمایش داده می‌شوند
    list_display = ('title_fa', 'category', 'status', 'view_count', 'report_count_display', 'created_at')
    
    # فیلترهای سمت راست
    list_filter = ('status', 'category', 'created_at')
    
    # جستجو در فیلدهای مختلف
    search_fields = ('title_fa', 'body_fa', 'place_name', 'slug')
    
    # فیلدهای فقط خواندنی
    readonly_fields = ('view_count', 'url', 'created_at', 'updated_at')
    
    # اضافه کردن بخش تاریخچه به پایین صفحه ویرایش مقاله
    inlines = [RevisionInline]
    
    # انتخاب راحت‌تر تگ‌ها
    filter_horizontal = ('tags',)

    # متد محاسبه تعداد گزارش‌ها برای هر مقاله
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(_report_count=Count('reports'))
        return queryset

    def report_count_display(self, obj):
        count = obj._report_count
        if count > 0:
            # نمایش تعداد گزارش‌ها با رنگ قرمز اگر بیشتر از صفر بود
            return format_html('<span style="color: red; font-weight: bold;">{} گزارش</span>', count)
        return "۰"
    report_count_display.short_description = "تعداد تخلفات"

# ۵. مدیریت گزارش‌های کاربران
@admin.register(WikiArticleReports)
class WikiArticleReportsAdmin(admin.ModelAdmin):
    list_display = ('article', 'report_type', 'status', 'created_at')
    list_filter = ('status', 'report_type')
    search_fields = ('description', 'article__title_fa')
    actions = ['make_resolved', 'make_closed']

    @admin.action(description="تغییر وضعیت به: بررسی شده")
    def make_resolved(self, request, queryset):
        queryset.update(status='resolved')

    @admin.action(description="تغییر وضعیت به: بسته شده")
    def make_closed(self, request, queryset):
        queryset.update(status='closed')