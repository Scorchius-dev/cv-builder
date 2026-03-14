"""URL routing table for all app pages and Stripe endpoints."""

from django.contrib import admin
from django.urls import path, include
from builder.views import (
    signup, index, dashboard, cv_create, cv_update, cv_delete,
    letter_detail, letter_delete, export_pdf, upgrade_page,
    create_checkout_session, create_billing_portal_session,
    payment_success, payment_cancelled, stripe_webhook,
    terms_page, privacy_page, refund_policy_page
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', signup, name='signup'),

    # Home & Dashboard
    path('', index, name='index'),
    path('dashboard/', dashboard, name='dashboard'),

    # CV Operations
    path('cv/new/', cv_create, name='cv_create'),
    path('cv/<int:pk>/edit/', cv_update, name='cv_update'),
    path('cv/<int:pk>/delete/', cv_delete, name='cv_delete'),

    # Letter Operations
    path('letter/<int:pk>/', letter_detail, name='letter_detail'),
    path('letter/<int:pk>/delete/', letter_delete, name='letter_delete'),
    path('letter/<int:pk>/pdf/', export_pdf, name='export_pdf'),

    # Stripe Payment Flow
    path('upgrade/', upgrade_page, name='upgrade_page'),
    path(
        'upgrade/checkout/',
        create_checkout_session,
        name='create_checkout_session',
    ),
    path(
        'billing/portal/',
        create_billing_portal_session,
        name='billing_portal',
    ),
    path('payment-success/', payment_success, name='payment_success'),
    path('payment-cancelled/', payment_cancelled, name='payment_cancelled'),
    path('stripe/webhook/', stripe_webhook, name='stripe_webhook'),

    # Legal
    path('terms/', terms_page, name='terms_page'),
    path('privacy/', privacy_page, name='privacy_page'),
    path('refund-policy/', refund_policy_page, name='refund_policy_page'),
]
