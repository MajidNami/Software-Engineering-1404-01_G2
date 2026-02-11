import random
from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from team5.models import Team5City, Team5Media, Team5MediaRating, Team5Place
from team5.services.mock_provider import MockProvider


User = get_user_model()


@dataclass(frozen=True)
class DemoProfile:
    first_name: str
    last_name: str
    email: str
    age: int


DEMO_USERS = [
    DemoProfile("Ali", "Rahimi", "ali.rahimi@gmail.com", 24),
    DemoProfile("Sara", "Mohammadi", "sara.mohammadi@yahoo.com", 27),
    DemoProfile("Reza", "Karimi", "reza.karimi@gmail.com", 31),
    DemoProfile("Neda", "Ahmadi", "neda.ahmadi@gmail.com", 23),
    DemoProfile("Hamed", "Jafari", "hamed.jafari@yahoo.com", 29),
    DemoProfile("Maryam", "Nazari", "maryam.nazari@gmail.com", 26),
    DemoProfile("Pouya", "Taghavi", "pouya.taghavi@gmail.com", 33),
    DemoProfile("Zahra", "Ebrahimi", "zahra.ebrahimi@yahoo.com", 22),
    DemoProfile("Arman", "Soleimani", "arman.soleimani@gmail.com", 28),
    DemoProfile("Shiva", "Kiani", "shiva.kiani@gmail.com", 30),
    DemoProfile("Milad", "Hosseini", "milad.hosseini@yahoo.com", 25),
    DemoProfile("Yasmin", "Darvishi", "yasmin.darvishi@gmail.com", 24),
    DemoProfile("Kian", "Shahbazi", "kian.shahbazi@gmail.com", 21),
    DemoProfile("Parisa", "Farhadi", "parisa.farhadi@yahoo.com", 32),
    DemoProfile("Amin", "Rostami", "amin.rostami@gmail.com", 27),
]


class Command(BaseCommand):
    help = "Seed catalog data and realistic demo users/ratings in Team5 databases."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            default="Pass1234!Strong",
            help="Password used for users created by this seed command.",
        )
        parser.add_argument(
            "--clear-ratings",
            action="store_true",
            help="Delete existing Team5 ratings before seeding.",
        )
        parser.add_argument(
            "--clear-catalog",
            action="store_true",
            help="Delete city/place/media catalog and recreate it from mock files.",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=1404,
            help="Random seed for deterministic rating generation.",
        )

    def handle(self, *args, **options):
        password = options["password"]
        random.seed(options["seed"])
        provider = MockProvider()
        if options["clear_catalog"]:
            Team5Media.objects.all().delete()
            Team5Place.objects.all().delete()
            Team5City.objects.all().delete()
            self.stdout.write(self.style.WARNING("Deleted existing Team5 catalog records."))

        if options["clear_ratings"]:
            deleted_count, _ = Team5MediaRating.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Deleted existing ratings: {deleted_count}"))

        self._seed_catalog(provider)
        media_ids = list(Team5Media.objects.values_list("media_id", flat=True))

        created_users = 0
        total_ratings = 0

        for profile in DEMO_USERS:
            user, created = User.objects.get_or_create(
                email=profile.email,
                defaults={
                    "first_name": profile.first_name,
                    "last_name": profile.last_name,
                    "age": profile.age,
                    "is_active": True,
                },
            )

            if created:
                user.set_password(password)
                user.save()
                created_users += 1

            sample_size = random.randint(3, min(6, len(media_ids)))
            selected_media_ids = random.sample(media_ids, sample_size)

            for media_id in selected_media_ids:
                rate = random.choice([2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0])
                Team5MediaRating.objects.update_or_create(
                    user_id=user.id,
                    media_id=media_id,
                    defaults={
                        "user_email": user.email,
                        "rate": rate,
                        "liked": rate >= 4.0,
                    },
                )
                total_ratings += 1

        self.stdout.write(self.style.SUCCESS(f"Users created: {created_users}"))
        self.stdout.write(self.style.SUCCESS(f"Ratings upserted: {total_ratings}"))
        self.stdout.write("Demo users are now available in core.User (default DB).")
        self.stdout.write("Team5 catalog+ratings are now stored in team5 database.")

    def _seed_catalog(self, provider: MockProvider):
        for city in provider.get_cities():
            Team5City.objects.update_or_create(
                city_id=city["cityId"],
                defaults={
                    "city_name": city["cityName"],
                    "latitude": float(city["coordinates"][0]),
                    "longitude": float(city["coordinates"][1]),
                },
            )

        for place in provider.get_all_places():
            Team5Place.objects.update_or_create(
                place_id=place["placeId"],
                defaults={
                    "city_id": place["cityId"],
                    "place_name": place["placeName"],
                    "latitude": float(place["coordinates"][0]),
                    "longitude": float(place["coordinates"][1]),
                },
            )

        for media in provider.get_media():
            Team5Media.objects.update_or_create(
                media_id=media["mediaId"],
                defaults={
                    "place_id": media["placeId"],
                    "title": media["title"],
                    "caption": media["caption"],
                },
            )
