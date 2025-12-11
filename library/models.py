import datetime
from django.core.validators import MinValueValidator
from django.conf import settings
from django.db import models


class Book(models.Model):
    class CoverChoices(models.TextChoices):
        HARD = "HARD"
        SOFT = "SOFT"

    title = models.CharField(max_length=100, unique=True)
    author = models.CharField(max_length=100)
    cover = models.CharField(
        max_length=10,
        choices=CoverChoices.choices)
    inventory = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)])
    daily_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def borrow(self):
        if self.inventory <= 0:
            raise ValueError("inventory books = 0")
        self.inventory -= 1
        self.save()

    def return_book(self):
        self.inventory += 1
        self.save()

    def __str__(self):
        return (f"{self.title}, "
                f"{self.author}")


class Borrowing(models.Model):
    borrow_date = models.DateField(default=datetime.date.today)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowings",
    )

    def __str__(self):
        return f"{self.book.title}, {self.borrow_date}"


class Payment(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "PENDING"
        PAID = "PAID"

    class TypeChoices(models.TextChoices):
        PAYMENT = "PAYMENT"
        FINE = "FINE"

    status = models.CharField(max_length=10, choices=StatusChoices.choices)
    type_transaction = models.CharField(
        max_length=10,
        choices=TypeChoices.choices)
    borrowing = models.ForeignKey(
        Borrowing,
        on_delete=models.CASCADE,
        related_name="payments")
    session_url = models.URLField()
    session_id = models.CharField(max_length=200)

    def __str__(self):
        return (f"{self.status}, "
                f"{self.type_transaction}, "
                f"{self.session_url}, "
                f"{self.session_id}")
