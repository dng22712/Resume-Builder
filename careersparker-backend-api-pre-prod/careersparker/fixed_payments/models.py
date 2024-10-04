from django.db import models

# ----------------------------------------------------------------
# CV Builder Fixed Payment (NO AI) Model
# ----------------------------------------------------------------


class StripeFixedPayments(models.Model):
    """
    Stripe Fixed Payment Model
    """

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='stripe_fixed_payment')
    stripe_session_id = models.CharField(max_length=255, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    stripe_payment_link_id = models.CharField(max_length=255, blank=True)
    stripe_customer_email = models.CharField(max_length=255, blank=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    stripe_payment_status = models.CharField(max_length=255, blank=True)
    stripe_status = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.stripe_customer_email

    class Meta:
        verbose_name = 'StripeFixedPayment'
        verbose_name_plural = 'StripeFixedPayments'






