from django.db import transaction
from rest_framework import serializers
from library.telegram import send_telegram_message
from library.payments.services import (
    create_payment_for_borrowing,
    create_fine_for_borrowing)
from library.models import (
    Book,
    Borrowing, Payment,
)


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover", "inventory", "daily_fee")


class BookTitleSerializer(BookSerializer):
    class Meta:
        model = Book
        fields = ("title", "daily_fee")


class PaymentForBorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type_transaction",
            "session_url",
        )


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id",
                  "borrow_date",
                  "actual_return_date",
                  "expected_return_date",
                  "is_active",
                  "book",
                  "user")
        read_only_fields = ("id", "user", "is_active",)

    def create(self, validated_data):
        book = validated_data["book"]
        if book.inventory <= 0:
            raise (serializers
                   .ValidationError("Inventory must be greater than 0"))
        try:
            with transaction.atomic():
                book.borrow()
                borrowing = Borrowing.objects.create(
                    **validated_data,
                    user=self.context["request"].user,
                )
                create_payment_for_borrowing(borrowing)
        except Exception as e:
            raise serializers.ValidationError(str(e))

        message = (f"New borrowing: '{book.title}', "
                   f"User: {borrowing.user.email}, "
                   f"Expected: {borrowing.expected_return_date}")
        send_telegram_message(message)
        return borrowing

    def update(self, instance, validated_data):
        old_return_date = instance.actual_return_date
        new_return_date = validated_data.get("actual_return_date")
        fine_payment = None

        with transaction.atomic():
            instance.actual_return_date = new_return_date

            if old_return_date is None and new_return_date is not None:
                instance.is_active = False
                instance.book.return_book()
                fine_payment = create_fine_for_borrowing(instance)

            instance.save()

        if fine_payment:
            message = (f"Fine created for borrowing: '{instance.book.title}', "
                       f"User: {instance.user.email}, ")
            send_telegram_message(message)
        return instance


class BorrowingCreateSerializer(BorrowingSerializer):
    class Meta:
        model = Borrowing
        fields = ("id",
                  "borrow_date",
                  "actual_return_date",
                  "expected_return_date",
                  "book",
                  "user")
        read_only_fields = ("id", "borrow_date", "actual_return_date", "user")


class BorrowingUpdateSerializer(BorrowingSerializer):
    class Meta:
        model = Borrowing
        fields = ("id",
                  "borrow_date",
                  "actual_return_date",
                  "expected_return_date",
                  "book",
                  "user")
        read_only_fields = ("id",
                            "borrow_date",
                            "expected_return_date",
                            "user",
                            "book")


class BorrowingListSerializer(BorrowingSerializer):
    book = BookTitleSerializer()

    class Meta:
        model = Borrowing
        fields = ("id",
                  "borrow_date",
                  "actual_return_date",
                  "expected_return_date",
                  "is_active",
                  "book",
                  "user")


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookTitleSerializer()
    user = serializers.CharField(source="user.email", read_only=True)
    payments = PaymentForBorrowingSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "actual_return_date",
            "expected_return_date",
            "is_active",
            "book",
            "user",
            "payments",
        )


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("id",
                  "status",
                  "type_transaction",
                  "session_url",
                  )
