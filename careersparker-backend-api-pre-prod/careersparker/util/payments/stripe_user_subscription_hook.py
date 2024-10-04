import os
import stripe
from rest_framework import status
from rest_framework.response import Response

from subscription_payments.models import SubscriptionCreated, ProcessedEvent
from user.models import User


def process_stripe_user_subscription_payment_link_event(request, endpoint_secret):
    """
    Process Stripe User Subscription Payment Link Event
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

    event_id = event['id']  # Get the event id

    # Check if the event has already been processed
    if ProcessedEvent.objects.filter(event_id=event_id).exists():
        return Response(status=status.HTTP_200_OK, data={'message': 'Event already processed'})

    # Here you can process the customer email further or store it in your database
    if event['type'] == 'customer.subscription.created':

        stripe_subscription_id = event['data']['object']['id']
        stripe_subscription_customer_id = event['data']['object']['customer']

        stripe_customer_id = stripe.Customer.retrieve(stripe_subscription_customer_id).id  # get the customer id

        if stripe_customer_id is None or stripe_subscription_customer_id is None: # check if the customer id is None
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'customer_id is None'})

        if stripe_customer_id != stripe_subscription_customer_id:  # check if the customer id matches the stripe_subscription_customer_id
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'error': 'customer_id does not match stripe_subscription_customer_id'})

        stripe_subscription_customer_email = stripe.Customer.retrieve(stripe_subscription_customer_id).email # get the customer email

        if stripe_subscription_customer_email is None: # check if the customer email is None
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'customer_email is None'})

        # get the user from the User model
        user = User.objects.get(email=stripe_subscription_customer_email)


        # check if the user is None
        if user is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'user is not registered'})

        # Check if the user already has an active subscription
        if SubscriptionCreated.objects.filter(user=user, stripe_subscription_active='active').exists():
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'error': 'User already has an active subscription'})

        # Get the current_period_start and current_period_end
        current_period_start = event['data']['object']['current_period_start']
        current_period_end = event['data']['object']['current_period_end']
        stripe_days_left = (current_period_end - current_period_start) / 86400
        stripe_subscription_active = event['data']['object']['status']
        stripe_interval = event['data']['object']['items']['data'][0]['price']['recurring']['interval']
        stripe_product_name = event['data']['object']['items']['data'][0]['price']['nickname']
        stripe_start_date = event['data']['object']['start_date']
        stripe_status = event['data']['object']['status']

        # check if subscription already exists and subscription is active in the database

        subscription_exists = SubscriptionCreated.objects.get(stripe_subscription_id=stripe_subscription_id)

        # Check for Inactive or Incomplete Status
        if subscription_exists.stripe_status in ['incomplete', 'canceled']:
            # Update if inactive or incomplete (combined condition)
            subscription_exists.stripe_subscription_customer_id = stripe_subscription_customer_id
            subscription_exists.stripe_product_name = stripe_product_name
            subscription_exists.stripe_current_period_start = current_period_start
            subscription_exists.stripe_current_period_end = current_period_end
            subscription_exists.stripe_days_left = stripe_days_left
            subscription_exists.stripe_subscription_active = stripe_subscription_active
            subscription_exists.stripe_subscription_interval = stripe_interval
            subscription_exists.stripe_status = stripe_status  # Update status if needed
            subscription_exists.save()
            ProcessedEvent.objects.create(event_id=event_id)  # Save the processed event
            return user, stripe_product_name, stripe_days_left, stripe_subscription_active, stripe_interval

        # Check for Active Status
        elif subscription_exists.stripe_status == 'active':
            # No need to update if already active
            return Response(status=status.HTTP_200_OK, data={'message': 'Subscription is active and exists'})

        # save the subscription_created model
        SubscriptionCreated.objects.create(
            user=user,
            stripe_subscription_id=stripe_subscription_id,
            stripe_subscription_customer_id=stripe_subscription_customer_id,
            stripe_product_name=stripe_product_name,
            stripe_current_period_start=current_period_start,
            stripe_current_period_end=current_period_end,
            stripe_days_left=stripe_days_left,
            stripe_subscription_active=stripe_subscription_active,
            stripe_subscription_interval=stripe_interval,
        )

        # Save the processed event
        ProcessedEvent.objects.create(event_id=event_id)

        return user, stripe_subscription_id, stripe_subscription_customer_id, stripe_product_name, stripe_status, current_period_start, \
            current_period_end, stripe_days_left, stripe_subscription_active, stripe_interval, stripe_start_date, event_id
