import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **options):
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        first_name = os.environ.get("DJANGO_SUPERUSER_FIRST_NAME")
        last_name = os.environ.get("DJANGO_SUPERUSER_LAST_NAME")

        if not all([email, password, first_name, last_name]):
            self.stdout.write("Superuser env variables not set.")
            return

        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            self.stdout.write("Superuser created successfully.")
        else:
            self.stdout.write("Superuser already exists.")
