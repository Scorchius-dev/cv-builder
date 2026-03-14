from types import SimpleNamespace
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from unittest.mock import patch
from django.test.utils import override_settings

from .models import CV, CoverLetter, Profile


class CareerProTests(TestCase):
    def setUp(self):
        """Set up a test environment before every test function runs."""
        # Create a test user
        self.user = User.objects.create_user(
            username='tester',
            password='password123'
        )

        # Create a second user to test security/privacy
        self.other_user = User.objects.create_user(
            username='hacker',
            password='password123'
        )

        # Create a CV for the main tester
        self.cv = CV.objects.create(
            user=self.user,
            title="Software Engineer CV",
            education="Degree",
            experience="3 Years",
            skills="Django, Python"
        )

    # --- 1. CRUD TESTING ---

    def test_dashboard_access_and_read(self):
        """Test if a logged-in user can see their CV on the dashboard."""
        self.client.login(username='tester', password='password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Software Engineer CV")

    def test_cv_update(self):
        """Test if a user can edit an existing CV (The 'U' in CRUD)."""
        self.client.login(username='tester', password='password123')
        new_title = "Senior Developer CV"
        response = self.client.post(reverse('cv_update', args=[self.cv.pk]), {
            'title': new_title,
            'education': self.cv.education,
            'experience': self.cv.experience,
            'skills': self.cv.skills
        })
        self.cv.refresh_from_db()
        self.assertEqual(self.cv.title, new_title)
        self.assertRedirects(response, reverse('dashboard'))

    def test_cv_delete(self):
        """Test if a user can remove a CV (The 'D' in CRUD)."""
        self.client.login(username='tester', password='password123')
        response = self.client.post(reverse('cv_delete', args=[self.cv.pk]))
        self.assertEqual(CV.objects.count(), 0)
        self.assertRedirects(response, reverse('dashboard'))

    # --- 2. SECURITY & AUTH TESTING ---

    def test_privacy_isolation(self):
        """Security: Ensure User A cannot see or edit User B's data."""
        # Log in as the 'hacker' user
        self.client.login(username='hacker', password='password123')

        # Try to view the dashboard (should not see the tester's CV)
        response = self.client.get(reverse('dashboard'))
        self.assertNotContains(response, "Software Engineer CV")

        # Try to delete the tester's CV directly via URL
        # (Should return 404 Not Found)
        response = self.client.post(reverse('cv_delete', args=[self.cv.pk]))
        self.assertEqual(response.status_code, 404)

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
    )
    def test_signup_creates_user_and_sends_confirmation_email(self):
        """Signup should create user, login, flash success, and send email."""
        response = self.client.post(
            reverse('signup'),
            {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password1': 'StrongPassword123!',
                'password2': 'StrongPassword123!',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue('_auth_user_id' in self.client.session)
        self.assertContains(response, 'Account created successfully')

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Welcome to AI Career Pro', mail.outbox[0].subject)
        self.assertIn('newuser@example.com', mail.outbox[0].to)

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
    )
    def test_signup_without_email_creates_user(self):
        """Signup should work without email and skip sending email."""
        response = self.client.post(
            reverse('signup'),
            {
                'username': 'noemailuser',
                'email': '',
                'password1': 'StrongPassword123!',
                'password2': 'StrongPassword123!',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='noemailuser').exists())
        self.assertContains(response, 'Account created successfully.')
        self.assertEqual(len(mail.outbox), 0)

    def test_signup_rejects_duplicate_email(self):
        """Signup should block creating another account with same email."""
        User.objects.create_user(
            username='emailowner',
            email='taken@example.com',
            password='password123',
        )

        response = self.client.post(
            reverse('signup'),
            {
                'username': 'differentuser',
                'email': 'taken@example.com',
                'password1': 'StrongPassword123!',
                'password2': 'StrongPassword123!',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'An account with this email already exists.',
        )

    # --- 3. AI LOGIC TESTING ---

    def test_cover_letter_storage(self):
        """
        Test if a letter is successfully saved to the database (Persistence).
        """
        CoverLetter.objects.create(
            user=self.user,
            cv=self.cv,
            job_title="Python Dev",
            company_name="Google",
            generated_content="This is a test AI letter."
        )
        self.assertEqual(CoverLetter.objects.count(), 1)

    @patch(
        'builder.views.generate_cover_letter',
        return_value='Generated text'
    )
    def test_index_missing_fields_does_not_create_letter(self, _mock_ai):
        """Posting incomplete generation data should not create a letter."""
        self.client.login(username='tester', password='password123')
        response = self.client.post(reverse('index'), {
            'cv_id': str(self.cv.pk),
            'job_title': 'Backend Engineer',
            'company_name': '',
            'job_description': 'Build APIs.',
        })
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(CoverLetter.objects.count(), 0)

    def test_dashboard_search_filters_letters(self):
        """Dashboard query param filters letters by title/company/content."""
        CoverLetter.objects.create(
            user=self.user,
            cv=self.cv,
            job_title='Python Developer',
            company_name='OpenAI',
            generated_content='Great fit for backend role.'
        )
        CoverLetter.objects.create(
            user=self.user,
            cv=self.cv,
            job_title='Frontend Developer',
            company_name='Contoso',
            generated_content='React focused position.'
        )

        self.client.login(username='tester', password='password123')
        response = self.client.get(reverse('dashboard'), {'q': 'OpenAI'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'OpenAI')
        self.assertNotContains(response, 'Contoso')

    def test_payment_success_does_not_auto_upgrade_profile(self):
        """Success page should not bypass webhook subscription updates."""
        self.client.login(username='tester', password='password123')
        response = self.client.get(reverse('payment_success'))
        self.assertEqual(response.status_code, 200)

        profile = Profile.objects.get(user=self.user)
        self.assertFalse(profile.is_premium)

    @patch('builder.views.stripe.checkout.Session.retrieve')
    def test_payment_success_with_session_id_unlocks_premium(
        self,
        mock_session_retrieve,
    ):
        """Success page can sync premium from Stripe if webhook lags."""
        mock_session_retrieve.return_value = {
            'customer': 'cus_test_1',
            'subscription': {
                'id': 'sub_test_1',
                'customer': 'cus_test_1',
                'status': 'active',
                'current_period_end': 2000000000,
            },
        }

        self.client.login(username='tester', password='password123')
        response = self.client.get(
            reverse('payment_success'),
            {'session_id': 'cs_test_123'},
        )
        self.assertEqual(response.status_code, 200)

        profile = Profile.objects.get(user=self.user)
        self.assertTrue(profile.is_premium)
        self.assertEqual(profile.stripe_customer_id, 'cus_test_1')
        self.assertEqual(profile.subscription_status, 'active')

    @override_settings(STRIPE_PRICE_ID='price_test_123')
    @patch('builder.views.stripe.checkout.Session.create')
    def test_checkout_session_uses_subscription_mode(self, mock_create):
        """Checkout should be created in recurring subscription mode."""
        mock_create.return_value = SimpleNamespace(
            url='https://stripe.test/checkout'
        )
        self.client.login(username='tester', password='password123')

        response = self.client.post(reverse('create_checkout_session'))
        self.assertIn(response.status_code, {302, 303})
        self.assertEqual(response.url, 'https://stripe.test/checkout')

        kwargs = mock_create.call_args.kwargs
        self.assertEqual(kwargs['mode'], 'subscription')
        self.assertEqual(kwargs['line_items'][0]['price'], 'price_test_123')

    @override_settings(
        STRIPE_PRICE_ID='',
        STRIPE_PREMIUM_MONTHLY_PENCE=1299,
        STRIPE_CURRENCY='gbp',
    )
    @patch('builder.views.stripe.checkout.Session.create')
    def test_checkout_session_uses_fallback_price_data(
        self,
        mock_create,
    ):
        """Missing STRIPE_PRICE_ID should use recurring fallback price_data."""
        mock_create.return_value = SimpleNamespace(
            url='https://stripe.test/checkout'
        )
        self.client.login(username='tester', password='password123')

        response = self.client.post(reverse('create_checkout_session'))
        self.assertIn(response.status_code, {302, 303})

        kwargs = mock_create.call_args.kwargs
        price_data = kwargs['line_items'][0]['price_data']
        self.assertEqual(price_data['currency'], 'gbp')
        self.assertEqual(price_data['unit_amount'], 1299)
        self.assertEqual(price_data['recurring']['interval'], 'month')

    @override_settings(STRIPE_WEBHOOK_SECRET='whsec_test')
    @patch('builder.views.stripe.Subscription.retrieve')
    @patch('builder.views.stripe.Webhook.construct_event')
    def test_webhook_checkout_completed_activates_profile(
        self,
        mock_construct_event,
        mock_subscription_retrieve,
    ):
        """Stripe webhook should activate premium from completed checkout."""
        mock_construct_event.return_value = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'client_reference_id': str(self.user.id),
                    'subscription': 'sub_123',
                    'customer': 'cus_123',
                }
            }
        }
        mock_subscription_retrieve.return_value = {
            'id': 'sub_123',
            'customer': 'cus_123',
            'status': 'active',
            'current_period_end': 2000000000,
        }

        response = self.client.post(
            reverse('stripe_webhook'),
            data='{}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='sig_test',
        )
        self.assertEqual(response.status_code, 200)

        profile = Profile.objects.get(user=self.user)
        self.assertTrue(profile.is_premium)
        self.assertEqual(profile.subscription_status, 'active')
        self.assertEqual(profile.stripe_customer_id, 'cus_123')
        self.assertEqual(profile.stripe_subscription_id, 'sub_123')
