from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.reverse import reverse

from cvbuilder.models import CvBuilder
from fixed_payments.models import StripeFixedPayment


# ----------------------------------------------
# Create a new CV
# ----------------------------------------------
class Cv_Creation(TestCase):

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

    def test_create_cv_builder_success_with_fixed_payment(self):
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
        # self.user.cv_create_count = 1
        # self.user.save()

        data = {
            'user': self.user.id,
            'cv_title': 'Test CV',
            'cv_slug': 'test-cv',
            'cv_template_selected': 'template1',
        }
        response = self.client.post(url, data, format='json, content_type=application/json',
                                    HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            CvBuilder.objects.filter(cv_title='Test CV', cv_slug='test-cv', user=self.user).exists())

    def test_create_cv_builder_success_with_free_offer(self):
        payment_data = {
            'user': self.user,
            'stripe_session_id': 'test_session_id',
            'stripe_customer_id': 'test_customer_id',
            'stripe_payment_intent_id': 'test_payment_intent_id',
            'stripe_payment_link_id': 'test_payment_link_id',
            'stripe_customer_email': 'test@example.com',
            'stripe_payment_status': 'test_payment_status',
            'stripe_status': 'test_status',
        }
        payment = StripeFixedPayment.objects.create(**payment_data)  # create a payment
        url = reverse('cvbuilder:cvbuilder-list')
        data = {
            'user': self.user.id,
            'cv_title': 'Test CV',
            'cv_slug': 'test-cv',
            'cv_template_selected': 'template1',
        }
        # save user as free
        self.user.set_user_is_free_to_true()  # set user.is_free to True
        self.user.save()

        response = self.client.post(url, data, format='json, content_type=application/json',
                                    HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            CvBuilder.objects.filter(cv_title='Test CV', cv_slug='test-cv', user=self.user).exists())

    def test_create_cv_builder_fail_with_no_fixed_payment(self):
        payment_data = {
            'user': self.user,
            'stripe_session_id': 'test_session_id',
            'stripe_customer_id': 'test_customer_id',
            'stripe_payment_intent_id': 'test_payment_intent_id',
            'stripe_payment_link_id': 'test_payment_link_id',
            'stripe_customer_email': 'test@example.com',
            'stripe_payment_status': 'test_payment_status',
            'stripe_status': 'test_status',
        }
        payment = StripeFixedPayment.objects.create(**payment_data)  # create a payment

        payment.save()

        # set user.is_free to False
        self.user.set_user_is_free_to_false()  # set user.is_free to False
        self.user.save()

        url = reverse('cvbuilder:cvbuilder-list')
        data = {
            'user': self.user.id,
            'cv_title': 'Test CV',
            'cv_slug': 'test-cv',

        }
        response = self.client.post(url, data, format='json, content_type=application/json',
                                    HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.assertEqual(response.status_code, 400)
        self.assertFalse(
            CvBuilder.objects.filter(cv_title='Test CV', cv_slug='test-cv', user=self.user).exists())

    def test_create_cv_builder_fail_with_no_user(self):
        url = reverse('cvbuilder:cvbuilder-list')
        data = {
            'cv_title': 'Test CV',
            'cv_slug': 'test-cv',

        }
        response = self.client.post(url, data, format='json, content_type=application/json', HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.assertEqual(response.status_code, 400)
        self.assertFalse(
            CvBuilder.objects.filter(cv_title='Test CV', cv_slug='test-cv',
                                     user=self.user).exists())

    def test_cv_create_count_decreases_after_cv_creation(self):  # test cv_create_count decreases after cv creation
        payment_data = {
            'user': self.user,
            'stripe_session_id': 'test_session_id',
            'stripe_customer_id': 'test_customer_id',
            'stripe_payment_intent_id': 'test_payment_intent_id',
            'stripe_payment_link_id': 'test_payment_link_id',
            'stripe_customer_email': 'test@example.com',
            'stripe_payment_status': 'test_payment_status',
            'stripe_status': 'test_status',
        }
        self.user.cv_create_count = 1
        self.user.save()
        payment = StripeFixedPayment.objects.create(**payment_data)
        payment.save()
        self.assertEqual(self.user.cv_create_count, 1)
        url = reverse('cvbuilder:cvbuilder-list')
        data = {
            'user': self.user.id,
            'cv_title': 'Test CV',
            'cv_slug': 'test-cv',
            'cv_template_selected': 'template1',
        }
        response = self.client.post(url, data, format='json, content_type=application/json',
                                    HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(CvBuilder.objects.filter(cv_title='Test CV', cv_slug='test-cv', user=self.user).exists())

        payment.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual(self.user.cv_create_count, 0)

    def test_create_cv_builder_fail_with_no_cv_title(self):
        url = reverse('cvbuilder:cvbuilder-list')
        data = {
            'user': self.user.id,
            'cv_slug': 'test-cv',

        }
        response = self.client.post(url, data, format='json, content_type=application/json',
                                    HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.assertEqual(response.status_code, 400)
        self.assertFalse(
            CvBuilder.objects.filter(cv_title='Test CV', cv_slug='test-cv', user=self.user).exists())


