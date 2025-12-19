from datetime import timedelta, date
from unittest.mock import patch
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.core.cache import cache
from django.test import TestCase
from library.models import Borrowing, Book, Payment
from library.payments.services import (create_payment_for_borrowing,
                                       create_fine_for_borrowing)


class PaymentServiceTests(TestCase):
    def setUp(self):
        self.patcher = patch("library.payments.services.create_stripe_session")
        self.mock_create_session = self.patcher.start()
        self.mock_create_session.return_value.id = "sess_723"
        self.mock_create_session.return_value.url = "https://stripe.test/session"
        self.addCleanup(self.patcher.stop)
        cache.clear()
        self.user = get_user_model().objects.create_user(
            email="user@gmail.com",
            first_name="user",
            last_name="user",
            password="ASDasfsfgwe$123",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.book = Book.objects.create(
            title="Book JS",
            author="John Black",
            cover="HARD",
            inventory=3,
            daily_fee=3.20,
        )

    def test_create_payment_for_borrowing(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=3),
        )
        payment = create_payment_for_borrowing(borrowing)

        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(payment.borrowing, borrowing)
        self.assertEqual(payment.session_id, "sess_723")
        self.assertEqual(payment.session_url, "https://stripe.test/session")
        self.assertEqual(payment.type_transaction, Payment.TypeChoices.PAYMENT)
        self.assertEqual(payment.status, Payment.StatusChoices.PENDING)
        self.mock_create_session.assert_called_once()

    def test_create_fine_for_overdue_borrowing(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=date.today() + timedelta(days=-3),
            expected_return_date=date.today() + timedelta(days=-2),
            actual_return_date=date.today() + timedelta(days=-1),
        )
        payment = create_fine_for_borrowing(borrowing)
        self.assertIsNotNone(payment)
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(payment.session_id, "sess_723")
        self.assertEqual(payment.session_url, "https://stripe.test/session")
        self.assertEqual(payment.type_transaction, Payment.TypeChoices.FINE)
        self.mock_create_session.assert_called_once()

    def test_create_fine_without_overdue(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=date.today(),
            expected_return_date=date.today() + timedelta(days=1),
            actual_return_date=date.today(),
        )
        payment = create_fine_for_borrowing(borrowing)
        self.assertIsNone(payment)
        self.assertEqual(Payment.objects.count(), 0)
