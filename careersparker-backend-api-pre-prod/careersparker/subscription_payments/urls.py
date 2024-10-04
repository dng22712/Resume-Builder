from django.urls import path
from subscription_payments.views import StripeCreateSubscription

urlpatterns = [
    # cv builder fixed payment urls
    path(
        'create-subscription/',
        StripeCreateSubscription.as_view(),
        name='create-subscription-payment'
    ),

]
