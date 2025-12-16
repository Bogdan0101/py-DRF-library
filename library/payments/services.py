from library.models import Payment
from library.payments.stripe import create_stripe_session


def create_payment_for_borrowing(borrowing):
    amount = borrowing.total_amount_cents()
    session = create_stripe_session(
        amount=amount,
        name=f"Borrowing #{borrowing.id}",
    )
    return Payment.objects.create(
        borrowing=borrowing,
        session_url=session.url,
        session_id=session.id,
    )


def create_fine_for_borrowing(borrowing):
    if not borrowing.actual_return_date:
        return None
    days_of_overdue = (borrowing.actual_return_date - borrowing.expected_return_date).days
    if days_of_overdue <= 0:
        return None
    daily_fee = borrowing.book.daily_fee
    multiplier = 2
    amount = int(daily_fee * multiplier * days_of_overdue * 100)
    session = create_stripe_session(
        amount=amount,
        name=f"Borrowing #{borrowing.id}",
    )
    return Payment.objects.create(
        borrowing=borrowing,
        session_url=session.url,
        session_id=session.id,
    )
