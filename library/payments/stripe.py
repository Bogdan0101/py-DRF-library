import os

import stripe
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


def create_stripe_session(amount: int, name: str):

    """
    amount=1000 (10.00$)
    Stripe Checkout Session is created in test mode for backend-only
    """

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
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel",
    )
    return session
