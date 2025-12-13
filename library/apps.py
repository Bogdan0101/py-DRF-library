from django.apps import AppConfig
from datetime import datetime, time, date

from django.db import transaction
from django.utils.timezone import make_aware
from django.db.utils import OperationalError, ProgrammingError


class LibraryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "library"

    def ready(self):
        try:
            from django_q.models import Schedule

            with transaction.atomic():
                try:
                    Schedule.objects.get_or_create(
                        func="library.tasks.check_overdue_borrowings",
                        defaults={
                            "schedule_type": "D",
                            "next_run": make_aware(datetime.combine(date.today(), time(8, 30))),
                            "repeats": -1
                        }
                    )
                    print("check_overdue_borrowings task.")

                    Schedule.objects.get_or_create(
                        func="library.tasks.cleanup_tasks",
                        defaults={
                            "schedule_type": "W",
                            "next_run": make_aware(datetime.combine(date.today(), time(1, 0))),
                            "repeats": -1
                        },
                    )
                    print("cleanup_tasks task.")

                except (OperationalError, ProgrammingError):
                    pass

        except ImportError:
            pass
