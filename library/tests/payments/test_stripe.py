from unittest.mock import patch
from django.core.cache import cache
from django.test import TestCase
from library.payments.stripe import create_stripe_session


class StripeClientTests(TestCase):
    def setUp(self):
        cache.clear()
        self.patcher = patch("library.payments.stripe.stripe.checkout.Session.create")
        self.mock_create_stripe = self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_negative_amount(self):
        with self.assertRaises(ValueError):
            create_stripe_session(-100, "Test")
        self.mock_create_stripe.assert_not_called()

    def test_stripe_create_called(self):
        self.mock_create_stripe.return_value = "session"
        session = create_stripe_session(1000, "Test")
        self.assertEqual(session, "session")
        self.mock_create_stripe.assert_called_once()
