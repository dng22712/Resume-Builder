from django.urls import path

from fixed_payments.views import StripeFixedPayment

urlpatterns = [
    # cv builder fixed payment urls
    path(
        'fixed/',
        StripeFixedPayment.as_view(),
        name='create-fixed-payment'
    ),

]
