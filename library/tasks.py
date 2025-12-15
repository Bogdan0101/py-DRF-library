from datetime import date, timedelta
from django.utils import timezone
from django_q.models import Task, Schedule


def check_overdue_borrowings():
    from .telegram import send_telegram_message
    from .models import Borrowing
    today = date.today()
    borrowings = Borrowing.objects.filter(
        expected_return_date__lte=today,
        actual_return_date__isnull=True,
    )

    if not borrowings.exists():
        send_telegram_message("No borrowings overdue today!")
        return
    send_telegram_message(f"Borrowings overdue today ({today})!")
    for borrowing in borrowings:
        message = (
            f"User: {borrowing.user.email}\n"
            f"Book: {borrowing.book.title}\n"
            f"Borrow date: {borrowing.borrow_date}\n"
            f"Expected return date: {borrowing.expected_return_date}"
        )
        send_telegram_message(message)


def cleanup_tasks():
    try:
        old_tasks = (Task
                     .objects
                     .filter
                     (started__lte=timezone.now() - timedelta(days=7)))
        tasks_deleted = old_tasks.count()
        old_tasks.delete()
        old_schedules = (Schedule
                         .objects
                         .filter
                         (next_run__lte=timezone.now() - timedelta(days=7)))
        schedules_deleted = old_schedules.count()
        old_schedules.delete()
        print(f"Deleted {tasks_deleted} old tasks.")
        print(f"Deleted {schedules_deleted} old schedules.")
    except Exception as e:
        print(e)
