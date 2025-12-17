import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_session(amount: int, name: str) -> stripe.checkout.Session:
    """
    amount=1000 (10.00$)
    Stripe Checkout Session is created in test mode for backend-only
    """

    if amount <= 0:
        raise ValueError("Amount must be positive")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": name,
                    },
                    "unit_amount": amount,
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=(
            "https://localhost:8000/api/payments/success/"
            "?session_id={CHECKOUT_SESSION_ID}"
        ),
        cancel_url="https://localhost:8000/api/payments/cancel/",
    )
    return session
