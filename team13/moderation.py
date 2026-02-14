# منطق تأیید پیشنهاد مکان و پیشنهاد مسیر (Internal Moderation)

from django.db import transaction

from .models import Image, Place, PlaceContribution, PlaceTranslation, RouteContribution, RouteLog

TEAM13_DB = "team13"


def _address_from_contribution_coords(contribution):
    """آدرس نهایی مکان بر اساس طول و عرض پیشنهاد (برای ذخیره در Place پس از تأیید)."""
    from .geo_utils import address_from_coords
    return address_from_coords(contribution.latitude, contribution.longitude)


def approve_route_contribution(route_contribution_id):
    """
    تأیید یک RouteContribution: ایجاد دو Place (مبدأ و مقصد)، یک RouteLog، و حذف پیشنهاد مسیر.

    Returns:
        RouteLog ایجاد شده.
    """
    rc = RouteContribution.objects.using(TEAM13_DB).get(contribution_id=route_contribution_id)
    with transaction.atomic(using=TEAM13_DB):
        source_place = Place.objects.using(TEAM13_DB).create(
            type=Place.PlaceType.ENTERTAINMENT,
            city="",
            address=rc.source_address or "",
            latitude=rc.source_latitude,
            longitude=rc.source_longitude,
        )
        PlaceTranslation.objects.using(TEAM13_DB).create(
            place=source_place,
            lang="fa",
            name="مبدأ: " + (rc.source_address[:200] if rc.source_address else "مسیر پیشنهادی"),
            description="",
        )
        dest_place = Place.objects.using(TEAM13_DB).create(
            type=Place.PlaceType.ENTERTAINMENT,
            city="",
            address=rc.destination_address or "",
            latitude=rc.destination_latitude,
            longitude=rc.destination_longitude,
        )
        PlaceTranslation.objects.using(TEAM13_DB).create(
            place=dest_place,
            lang="fa",
            name="مقصد: " + (rc.destination_address[:200] if rc.destination_address else "مسیر پیشنهادی"),
            description="",
        )
        route_log = RouteLog.objects.using(TEAM13_DB).create(
            user_id=rc.user_id,
            source_place=source_place,
            destination_place=dest_place,
            travel_mode=rc.travel_mode,
        )
        rc.delete()
    return route_log


def approve_contribution(contribution_id):
    """
    تأیید یک PlaceContribution: مکان را در دیتابیس SQLite تیم ۱۳ (جدول team13_places)
    به‌صورت رسمی ذخیره می‌کند تا در لیست مکان‌ها و نقشه برای همه نمایش داده شود.
    - ایجاد رکورد Place و PlaceTranslation در همان دیتابیس
    - انتقال تصاویر پیشنهاد به Image با target_type=place و is_approved=True
    - حذف پیشنهاد (PlaceContribution)

    Args:
        contribution_id: UUID (یا str) شناسه PlaceContribution.

    Returns:
        Place: مکان ایجاد شده.

    Raises:
        PlaceContribution.DoesNotExist: اگر پیشنهاد یافت نشود.
    """
    contribution = PlaceContribution.objects.using(TEAM13_DB).get(contribution_id=contribution_id)
    address = _address_from_contribution_coords(contribution) or contribution.address or ""
    with transaction.atomic(using=TEAM13_DB):
        place = Place.objects.using(TEAM13_DB).create(
            type=contribution.type,
            city=contribution.city or "",
            address=address,
            latitude=contribution.latitude,
            longitude=contribution.longitude,
        )
        PlaceTranslation.objects.using(TEAM13_DB).create(
            place=place,
            lang="fa",
            name=contribution.name_fa,
            description="",
        )
        if contribution.name_en:
            PlaceTranslation.objects.using(TEAM13_DB).create(
                place=place,
                lang="en",
                name=contribution.name_en,
                description="",
            )
        Image.objects.using(TEAM13_DB).filter(
            target_type=Image.TargetType.PENDING_PLACE,
            target_id=contribution.contribution_id,
        ).update(
            target_type=Image.TargetType.PLACE,
            target_id=place.place_id,
            is_approved=True,
        )
        contribution.delete()
    return place
