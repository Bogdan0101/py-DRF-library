from datetime import timedelta, date
from unittest import mock
from unittest.mock import patch
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from library.models import Borrowing, Book, Payment
from library.payments.services import create_payment_for_borrowing


class StripeViewTests(TestCase):
    def setUp(self):
        cache.clear()
        self.patcher_retrieve = patch("library.payments.views.stripe.checkout.Session.retrieve")
        self.mock_retrieve = self.patcher_retrieve.start()

        self.patcher_create = patch("library.payments.stripe.stripe.checkout.Session.create")
        self.mock_create = self.patcher_create.start()

        self.mock_create.return_value = type("obj", (object,), {
            "id": "test_session_id",
            "url": "http://test-url.com",
        })
        self.addCleanup(self.patcher_retrieve.stop)
        self.addCleanup(self.patcher_create.stop)

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

    def test_stripe_success_mark_payment_paid(self):
        self.mock_retrieve.return_value.payment_status = "paid"
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=date.today(),
            expected_return_date=date.today() + timedelta(days=3),
            actual_return_date=date.today() + timedelta(days=3),
        )
        payment = create_payment_for_borrowing(borrowing)
        res = self.client.get(
            reverse("library:stripe:stripe-success"),
            {"session_id": payment.session_id},
        )
        payment.refresh_from_db()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(payment.status, Payment.StatusChoices.PAID)

    def test_stripe_without_session_id(self):
        res = self.client.get(reverse("library:stripe:stripe-success"))
        self.assertEqual(res.status_code, 400)

    def test_stripe_cancel(self):
        res = self.client.get(reverse("library:stripe:stripe-cancel"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["detail"], "Payment cancelled")
