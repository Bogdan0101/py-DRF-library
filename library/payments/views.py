import stripe
from django.conf import settings
from django.http import JsonResponse
from library.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


def stripe_success(request):
    session_id = request.GET.get("session_id")
    if not session_id:
        return JsonResponse(
            {"detail": "No session ID provided."},
            status=400,
        )

    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.error.StripeError:
        return JsonResponse(
            {"detail": "Invalid Stripe session"},
            status=400,
        )
    if session.payment_status != "paid":
        return JsonResponse(
            {"detail": "Payment not completed"},
            status=400,
        )
    try:
        payment = Payment.objects.get(session_id=session_id)
    except Payment.DoesNotExist:
        return JsonResponse(
            {"detail": "Payment not found"},
            status=404,
        )
    payment.status = Payment.StatusChoices.PAID
    payment.save()

    return JsonResponse(
        {
            "detail": "Payment successful",
            "payment_id": payment.id,
            "borrowing_id": payment.borrowing_id,
            "type": payment.type_transaction,
        },
    )


def stripe_cancel(request):
    return JsonResponse({
        "detail": "Payment cancelled",
    })
