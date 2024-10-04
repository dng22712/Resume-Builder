# ----------------------------------------------------------------
# deleting CV
# ----------------------------------------------------------------
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from cvbuilder.models import CvBuilder
from fixed_payments.models import StripeFixedPayment


class TestCVDelete(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='Password123!',
            first_name='John',
            last_name='Doe',
            username='johndoe',
            is_active=True,
            is_verified=True,
        )

        self.user.save()  # create a user

        login_url = reverse('user:token_obtain_pair')

        token_data = {
            'email': 'test@example.com',
            'password': 'Password123!',
        }

        response = self.client.post(login_url, token_data, format='json')  # login user
        self.token = response.data['access']  # get token

        # create a CV
        url = reverse('cvbuilder:cvbuilder-list')
        payment_data = {
            'user': self.user,
            'stripe_session_id': 'test_session_id',
            'stripe_customer_id': 'test_customer_id',
            'stripe_payment_intent_id': 'test_payment_intent_id',
            'stripe_payment_link_id': 'test_payment_link_id',
            'stripe_customer_email': 'test@example.com',
            'stripe_payment_status': 'test_payment_status',
            'stripe_status': 'test_status'
        }
        payment = StripeFixedPayment.objects.create(**payment_data)  # create a payment
        payment.save()

        data = {
            'user': self.user.id,
            'cv_title': 'Test CV',
            'cv_template_selected': 'template1',
        }

        response = self.client.post(url, data, format='json, content_type=application/json',
                                    HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.assertEqual(response.status_code, 201)

    def test_delete_cv_builder_success(self):
        cv = CvBuilder.objects.get(cv_title='Test CV')
        url = reverse('cvbuilder:cvbuilder-detail', args=[cv.id])

        response = self.client.delete(
            url,
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )

        self.assertEqual(response.status_code, 404)
        self.assertFalse(CvBuilder.objects.filter(cv_title='Test CV').exists())

    def test_unathorized_user_delete_cv_builder(self):
        cv = CvBuilder.objects.get(cv_title='Test CV')
        url = reverse('cvbuilder:cvbuilder-detail', args=[cv.id])

        response = self.client.delete(
            url,
        )

        self.assertEqual(response.status_code, 401)
        self.assertTrue(CvBuilder.objects.filter(cv_title='Test CV').exists())
