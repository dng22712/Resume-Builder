from fixed_payments.models import StripeFixedPayment
from rest_framework import serializers


class StripeFixedPaymentSerializer(serializers.Serializer):
    class Meta:
        model = StripeFixedPayment
        fields = '__all__'

        extra_kwargs = {'id': {'read_only': True}}
