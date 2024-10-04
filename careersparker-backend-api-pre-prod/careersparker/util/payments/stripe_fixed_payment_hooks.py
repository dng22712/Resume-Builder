import os

import stripe
from rest_framework import status
from rest_framework.response import Response

from user.models import User


def process_stripe_fixed_payment_link_event(request, endpoint_secret, event_type):
    """
    Process Stripe Fixed Cv Create Payment Link Event
    """
    stripe.api_key = os.getenv('STRIPE_API_KEY')
    payload = request.body.decode('utf-8')
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)

    except ValueError as e:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': str(e)})

    except stripe.error.SignatureVerificationError as e:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': str(e)})

    if event['type'] == event_type:

        session = event['data']['object']
        stripe_session_id = event['data']['object']['id']
        stripe_customer_id = event['data']['object']['customer']
        stripe_payment_intent_id = event['data']['object']['payment_intent'] if event['data']['object']['payment_intent'] is not None else 0
        stripe_payment_link_id = event['data']['object']['payment_link']
        stripe_customer_email = event['data']['object']['customer_details']['email']
        if stripe_customer_email is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'customer_email is None'})

        user = User.objects.get(email=stripe_customer_email)  # get user from User model
        if user is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'user is registered'})

        stripe_payment_status = event['data']['object']['payment_status']
        if stripe_payment_status != 'paid':  # check if payment status is paid
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'payment status is not paid'})

        stripe_status = event['data']['object']['status']
        if stripe_status != 'complete':     # check if payment status is complete
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'payment status is not complete'})

        # compare the payment intent id with the payment intent id in the session
        if stripe_payment_intent_id != session['payment_intent']:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'payment intent id does not match'})

        line_items = stripe.checkout.Session.list_line_items(session['id'])
        quantity = line_items['data'][0]['quantity']

        return user, stripe_session_id, stripe_customer_id, stripe_payment_intent_id, stripe_payment_link_id, \
            stripe_customer_email, stripe_payment_status, stripe_status, quantity


# ------------------------------------------------------------------------------------------
# Send Receipt Email
# ------------------------------------------------------------------------------------------
def send_fixed_payment_receipt_email(user, stripe_session_id, stripe_customer_id, stripe_payment_intent_id,
                                     stripe_payment_link_id,
                                     stripe_customer_email, stripe_payment_status, stripe_status, cv_create_count,
                                     cv_template_count,
                                     cv_pdf_download_count, cv_word_download_count):
    """
    Send Receipt Email
    """
    # TODO:  send_receipt_email process_stripe_fixed_payment_link_event  this function

