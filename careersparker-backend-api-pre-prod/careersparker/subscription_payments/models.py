from django.db import models


class SubscriptionCreated(models.Model):
    """
    Stripe Subscription created model
    """

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='subscription_created_user')
    stripe_subscription_id = models.CharField(max_length=255, blank=True, unique=True)
    stripe_subscription_customer_id = models.CharField(max_length=255, blank=True, unique=True)
    stripe_product_name = models.CharField(max_length=255, blank=True)
    stripe_current_period_start = models.IntegerField(default=0)
    stripe_current_period_end = models.IntegerField(default=0)
    stripe_days_left = models.IntegerField(default=0)
    stripe_subscription_active = models.CharField(max_length=255, blank=True)
    stripe_subscription_interval = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.stripe_product_name

    class Meta:
        verbose_name = 'SubscriptionCreated'
        verbose_name_plural = 'SubscriptionCreateds'


# ----------------------------------------------------------------
class ProcessedEvent(models.Model):
    event_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
