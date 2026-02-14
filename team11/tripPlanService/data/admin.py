import json
from django.contrib import admin
from django.http import HttpResponse
from django.core.serializers import serialize
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from .models import Trip, TripDay, TripItem, ItemDependency, ShareLink, Vote, TripReview, UserMedia


# ─── Export Action ──────────────────────────────────────────────────

def export_as_json(modeladmin, request, queryset):
    """Admin action to export selected objects as JSON."""
    data = json.loads(serialize('json', queryset))
    clean_data = []
    for item in data:
        obj = {'id': item['pk'], **item['fields']}
        clean_data.append(obj)

    response = HttpResponse(
        json.dumps(clean_data, ensure_ascii=False, indent=2, default=str),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="{modeladmin.model.__name__}.json"'
    return response

export_as_json.short_description = "📥 Export selected as JSON"


# ─── Import Mixin ──────────────────────────────────────────────────

class ImportExportMixin:
    """Mixin that adds JSON export action + import page to ModelAdmin."""
    actions = [export_as_json]
    change_list_template = 'admin/import_change_list.html'

    def get_urls(self):
        custom_urls = [
            path(
                'import-json/',
                self.admin_site.admin_view(self.import_json_view),
                name=f'{self.model._meta.app_label}_{self.model._meta.model_name}_import_json',
            ),
        ]
        return custom_urls + super().get_urls()

    def import_json_view(self, request):
        if request.method == 'POST':
            json_file = request.FILES.get('json_file')
            if not json_file:
                messages.error(request, '❌ فایل JSON انتخاب نشده.')
                return redirect('..')

            try:
                data = json.load(json_file)
                if not isinstance(data, list):
                    data = [data]

                created_count = 0
                updated_count = 0
                for item in data:
                    item_copy = dict(item)
                    pk = item_copy.pop('id', None) or item_copy.pop('pk', None)

                    # Clean: remove fields that don't exist on the model
                    model_fields = {f.name for f in self.model._meta.get_fields()}
                    clean_item = {k: v for k, v in item_copy.items() if k in model_fields}

                    if pk:
                        obj, created = self.model.objects.update_or_create(
                            pk=pk, defaults=clean_item
                        )
                    else:
                        self.model.objects.create(**clean_item)
                        created = True

                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

                messages.success(
                    request,
                    f'✅ Import done: {created_count} created, {updated_count} updated.'
                )
            except json.JSONDecodeError:
                messages.error(request, '❌ فایل JSON معتبر نیست.')
            except Exception as e:
                messages.error(request, f'❌ خطا: {e}')

            return redirect('..')

        return render(request, 'admin/import_json.html', {
            'title': f'Import {self.model._meta.verbose_name_plural}',
            'opts': self.model._meta,
        })


# ─── Model Admins ──────────────────────────────────────────────────

@admin.register(Trip)
class TripAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ['trip_id', 'title',
                    'province', 'city', 'status', 'created_at']
    list_filter = ['status', 'budget_level', 'travel_style']
    search_fields = ['title', 'province', 'city']


@admin.register(TripDay)
class TripDayAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ['day_id', 'trip', 'day_index', 'specific_date']
    list_filter = ['trip']


@admin.register(TripItem)
class TripItemAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ['item_id', 'day', 'item_type',
                    'title', 'start_time', 'end_time']
    list_filter = ['item_type', 'category', 'price_tier']
    search_fields = ['title', 'place_ref_id']


@admin.register(ItemDependency)
class ItemDependencyAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ['dependency_id', 'item',
                    'prerequisite_item', 'dependency_type']


@admin.register(ShareLink)
class ShareLinkAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ['link_id', 'trip',
                    'permission', 'expires_at', 'created_at']
    list_filter = ['permission']


@admin.register(Vote)
class VoteAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ['vote_id', 'item', 'is_upvote', 'created_at']
    list_filter = ['is_upvote']


@admin.register(TripReview)
class TripReviewAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ['review_id', 'trip', 'rating',
                    'sent_to_central_service', 'created_at']
    list_filter = ['rating', 'sent_to_central_service']


@admin.register(UserMedia)
class UserMediaAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ['media_id', 'trip', 'user_id', 'media_type', 'uploaded_at']
    list_filter = ['media_type']
