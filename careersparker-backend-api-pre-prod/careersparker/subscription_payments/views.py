import os

from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from subscription_payments.models import SubscriptionCreated, ProcessedEvent
from util.payments.stripe_user_subscription_hook import process_stripe_user_subscription_payment_link_event


@extend_schema(tags=['Payments: Create Subscription'])
class StripeCreateSubscription(APIView):
    """
    Create a subscription.
    """
    serializer_class = None

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    @transaction.atomic
    def post(request, *args, **kwargs):
        """
        Create a subscription.
        """

        endpoint_secret = os.getenv('STRIPE_CREATE_SUBSCRIPTION_WEBHOOK_SECRET')  # Stripe api key
        print("endpoint_secret: ", endpoint_secret)

        # call the process_stripe_subscription_payment_link_event function
        subscription_data = process_stripe_user_subscription_payment_link_event(
            request,
            endpoint_secret,
        )
        print(subscription_data)

        if subscription_data is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'subscription not created'})

        # Capture the returned values in separate variables
        (user, stripe_subscription_id, stripe_subscription_customer_id, stripe_product_name, stripe_status,
         current_period_start,
         current_period_end, stripe_days_left, stripe_subscription_active, stripe_interval,
         stripe_start_date, event_id) = subscription_data

        # -------------------Check if the subscription already exists in the database-------------------

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

        # create a new subscription_created model
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
