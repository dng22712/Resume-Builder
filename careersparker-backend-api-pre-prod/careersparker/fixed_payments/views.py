import os
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from fixed_payments.models import StripeFixedPayments
from util.payments.stripe_fixed_payment_hooks import process_stripe_fixed_payment_link_event


@extend_schema(tags=['Payments: Fixed Payment'])
class StripeFixedPayment(APIView):
    """

    """

    serializer_class = None

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    @transaction.atomic
    def post(request, *args, **kwargs):
        """

        """

        # Stripe api key
        endpoint_secret = os.getenv('STRIPE_FIXED_PAYMENT_WEBHOOK_SECRET')

        # call the process_stripe_fixed_payment_link_event function
        fixed_payment_session_data = process_stripe_fixed_payment_link_event(
            request,
            endpoint_secret,
            'checkout.session.completed', )

        if fixed_payment_session_data is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'fixed payment not created'})

        # Capture the returned values in separate variables
        (user, stripe_session_id, stripe_customer_id, stripe_payment_intent_id, stripe_payment_link_id,
         stripe_customer_email, stripe_payment_status, stripe_status, quantity) = fixed_payment_session_data

        # check if session_id already exists in database and if it does, increase the count
        if StripeFixedPayments.objects.filter(stripe_session_id=stripe_session_id).exists():
            stripe_fixed_payment_session = StripeFixedPayments.objects.get(stripe_session_id=stripe_session_id)

            # increase the counter
            user.cv_create_count += quantity
            user.cv_template_count += quantity
            user.cv_pdf_download_count += quantity
            user.cv_word_download_count += quantity
            user.total_number_of_purchase += 1
            StripeFixedPayment.stripe_customer_id = stripe_customer_id

            # save the updated stripe fixed payment session
            stripe_fixed_payment_session.save()
            user.save()
            return Response(status=status.HTTP_200_OK, data={'message': 'CV fixed payment link updated successfully'})

        # # check user exists in database, if yes update the record
        # if stripe_fixed_payment.objects.filter(user=user).exists():
        #     stripe_fixed_payment_session = stripe_fixed_payment.objects.get(user=user)
        #     print('stripe_fixed_payment_session:', stripe_fixed_payment_session)
        #
        #     # increase the counter
        #     user.cv_create_count += cv_create_count
        #     user.cv_template_count += cv_template_count
        #     user.cv_pdf_download_count += cv_pdf_download_count
        #     user.cv_word_download_count += cv_word_download_count
        #     stripe_fixed_payment.stripe_customer_id = stripe_customer_id
        #
        #     # update the total number of purchase
        #     total_number_of_purchase_counter = stripe_fixed_payment_session.total_number_of_purchase
        #     stripe_fixed_payment_session.total_number_of_purchase += total_number_of_purchase_counter

            # save the updated stripe fixed payment session
            # stripe_fixed_payment_session.save()
            # return Response(status=status.HTTP_200_OK, data={'message': 'CV fixed payment link updated successfully'})

        # create a new stripe fixed payment session
        StripeFixedPayments.objects.create(
            user=user,
            stripe_session_id=stripe_session_id,
            stripe_customer_id=stripe_customer_id,
            stripe_payment_intent_id=stripe_payment_intent_id,
            stripe_payment_link_id=stripe_payment_link_id,
            stripe_customer_email=stripe_customer_email,
            stripe_payment_status=stripe_payment_status,
            stripe_status=stripe_status,

        )
        # increase the counter in the user model
        user.cv_create_count += quantity
        user.cv_template_count += quantity
        user.cv_pdf_download_count += quantity
        user.cv_word_download_count += quantity
        user.total_number_of_purchase += 1
        user.save()

        return Response(status=status.HTTP_200_OK, data={'message': 'CV fixed payment  created successfully'})

# ------------------------------------------------------------------------------------------
# Send fixed payment Receipt Email
# ------------------------------------------------------------------------------------------
