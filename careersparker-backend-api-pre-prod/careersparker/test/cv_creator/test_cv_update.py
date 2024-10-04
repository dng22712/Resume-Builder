from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from cvbuilder.models import CvBuilder
from fixed_payments.models import StripeFixedPayment


# ----------------------------------------------------------------
# updating CV
# ----------------------------------------------------------------
class TestCVUpdate(TestCase):
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
            'cv_slug': 'test-cv',
            'cv_template_selected': 'template1',
        }

        response = self.client.post(url, data, format='json, content_type=application/json',
                                    HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.assertEqual(response.status_code, 201)

    def test_update_cv_builder_success(self):
        cv = CvBuilder.objects.get(cv_title='Test CV')
        url = reverse('cvbuilder:cv-update', args=[cv.id])

        data = {
            'cv_title': 'Updated CV'
        }

        response = self.client.patch(
            url,
            data,
            format='json',
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, 200)
        cv.refresh_from_db()
        self.assertEqual(cv.cv_title, 'Updated CV')
        self.assertEqual(cv.cv_slug, 'updated-cv')

    def test_update_cv_builder_no_update_if_title_empty(self):
        cv = CvBuilder.objects.get(cv_title='Test CV')
        url = reverse('cvbuilder:cv-update', args=[cv.id])

        data = {
            'cv_title': ''

        }

        response = self.client.patch(
            url,
            data,
            format='json',
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(cv.cv_title, 'Test CV')

    def test_update_cv_builder_no_update_if_title_none(self):
        cv = CvBuilder.objects.get(cv_title='Test CV')
        url = reverse('cvbuilder:cv-update', args=[cv.id])

        data = {
            'cv_title': None

        }

        response = self.client.patch(
            url,
            data,
            format='json',
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(cv.cv_title, 'Test CV')

    def test_update_cv_builder_when_user_is_not_owner(self):
        cv = CvBuilder.objects.get(cv_title='Test CV')
        url = reverse('cvbuilder:cv-update', args=[cv.id])

        data = {
            'cv_title': 'Updated CV'
        }

        user = get_user_model().objects.create_user(
            email='test2@example.com',
            password='Password123!',
            first_name='John',
            last_name='Doe',
            username='johndoe2',
            is_active=True,
            is_verified=True,
        )

        user.save()  # create a user

        login_url = reverse('user:token_obtain_pair')

        token_data = {
            'email': 'test2@example.com',
            'password': 'Password123!',
        }

        response = self.client.post(login_url, token_data, format='json')  # login user
        token = response.data['access']  # get token

        response = self.client.patch(
            url,
            data,
            format='json',
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 404)
        cv.refresh_from_db()
        self.assertEqual(cv.cv_title, 'Test CV')
        self.assertEqual(cv.cv_slug, 'test-cv')


