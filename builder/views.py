import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseBadRequest
from django.conf import settings
from django.urls import reverse
from django.db.models import Q
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import stripe
from reportlab.lib.pagesizes import letter as pdf_letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

from .models import CV, CoverLetter, Profile
from .services import generate_cover_letter
from .forms import CVForm, SignupForm

# Make sure STRIPE_SECRET_KEY is in your settings.py
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', 'sk_test_placeholder')


def _profile_from_checkout_session(session):
    user_id = session.get('client_reference_id')
    if not user_id:
        return None

    try:
        return Profile.objects.select_related('user').get(user_id=user_id)
    except Profile.DoesNotExist:
        return None


def _sync_profile_from_subscription(profile, subscription):
    status = subscription.get('status', '')
    period_end_ts = subscription.get('current_period_end')
    period_end = None
    if period_end_ts:
        period_end = datetime.datetime.fromtimestamp(
            period_end_ts,
            tz=datetime.timezone.utc,
        )

    profile.stripe_customer_id = subscription.get('customer', '') or ''
    profile.stripe_subscription_id = subscription.get('id', '') or ''
    profile.subscription_status = status
    profile.current_period_end = period_end
    profile.is_premium = status in {'active', 'trialing'}
    profile.save()


def _sync_profile_from_checkout_session_id(profile, session_id):
    try:
        checkout_session = stripe.checkout.Session.retrieve(
            session_id,
            expand=['subscription'],
        )
    except Exception:
        return False

    customer_id = checkout_session.get('customer')
    if customer_id and profile.stripe_customer_id != customer_id:
        profile.stripe_customer_id = customer_id
        profile.save(update_fields=['stripe_customer_id'])

    subscription = checkout_session.get('subscription')
    if not subscription:
        return False

    if isinstance(subscription, str):
        subscription = stripe.Subscription.retrieve(subscription)

    _sync_profile_from_subscription(profile, subscription)
    return profile.is_premium


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            email_sent = False
            if user.email:
                send_mail(
                    subject='Welcome to AI Career Pro',
                    message=(
                        f'Hi {user.username},\n\n'
                        'Your account has been created successfully. '
                        'You can now create your CV profile and generate '
                        'tailored cover letters.\n\n'
                        'Thanks,\nAI Career Pro'
                    ),
                    from_email=getattr(
                        settings,
                        'DEFAULT_FROM_EMAIL',
                        'no-reply@aicareerpro.local',
                    ),
                    recipient_list=[user.email],
                    fail_silently=True,
                )
                email_sent = True
            login(request, user)
            if email_sent:
                messages.success(
                    request,
                    'Account created successfully. A welcome email '
                    'was sent to your inbox.',
                )
            else:
                messages.success(request, 'Account created successfully.')
            return redirect('index')
        messages.error(
            request,
            'We could not create your account. Please fix the errors below.',
        )
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def index(request):
    letter = None
    generated_letter_id = None
    profile, _ = Profile.objects.get_or_create(user=request.user)
    cvs = CV.objects.filter(user=request.user)

    if request.method == "POST":
        cv_id = request.POST.get('cv_id')
        job_description = request.POST.get('job_description', '').strip()
        job_title = request.POST.get('job_title', '').strip()
        company_name = request.POST.get('company_name', '').strip()

        if not cvs.exists():
            messages.warning(
                request,
                'Create a CV before generating a cover letter.',
            )
            return redirect('cv_create')

        if not cv_id:
            messages.error(request, 'Please select a CV to continue.')
            return redirect('index')

        if not all([job_description, job_title, company_name]):
            messages.error(request, 'Please fill in all job fields.')
            return redirect('index')

        selected_cv = get_object_or_404(CV, id=cv_id, user=request.user)
        cv_parts = []
        if selected_cv.summary:
            cv_parts.append(
                f'Personal Statement: {selected_cv.summary}'
            )
        cv_parts.append(f'Education:\n{selected_cv.education}')
        cv_parts.append(
            f'Work Experience:\n{selected_cv.experience}'
        )
        cv_parts.append(f'Skills: {selected_cv.skills}')
        if selected_cv.location:
            cv_parts.append(f'Location: {selected_cv.location}')
        cv_text = '\n\n'.join(cv_parts)

        letter = generate_cover_letter(cv_text, job_description)

        created_letter = CoverLetter.objects.create(
            user=request.user,
            cv=selected_cv,
            job_title=job_title,
            company_name=company_name,
            generated_content=letter
        )
        generated_letter_id = created_letter.id
        messages.success(request, 'Cover letter generated and saved.')

    return render(
        request,
        'builder/index.html',
        {
            'cvs': cvs,
            'letter': letter,
            'generated_letter_id': generated_letter_id,
            'profile': profile,
        },
    )


@login_required
def dashboard(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    user_cvs = CV.objects.filter(user=request.user)
    user_letters = CoverLetter.objects.filter(
        user=request.user
    ).order_by('-created_at')
    letter_query = request.GET.get('q', '').strip()
    if letter_query:
        user_letters = user_letters.filter(
            Q(job_title__icontains=letter_query)
            | Q(company_name__icontains=letter_query)
            | Q(generated_content__icontains=letter_query)
        )

    return render(
        request,
        'builder/dashboard.html',
        {
            'cvs': user_cvs,
            'letters': user_letters,
            'letter_query': letter_query,
            'cv_count': user_cvs.count(),
            'letter_count': CoverLetter.objects.filter(
                user=request.user
            ).count(),
            'profile': profile,
        },
    )


@login_required
def cv_create(request):
    if request.method == "POST":
        form = CVForm(request.POST)
        if form.is_valid():
            cv = form.save(commit=False)
            cv.user = request.user
            cv.save()
            messages.success(request, 'CV saved successfully.')
            return redirect('index')
    else:
        form = CVForm()
    return render(request, 'builder/cv_form.html', {'form': form})


@login_required
def cv_update(request, pk):
    cv = get_object_or_404(CV, pk=pk, user=request.user)
    if request.method == "POST":
        form = CVForm(request.POST, instance=cv)
        if form.is_valid():
            form.save()
            messages.success(request, 'CV updated.')
            return redirect('dashboard')
    else:
        form = CVForm(instance=cv)
    return render(
        request,
        'builder/cv_form.html',
        {'form': form, 'edit_mode': True},
    )


@login_required
def cv_delete(request, pk):
    cv = get_object_or_404(CV, pk=pk, user=request.user)
    if request.method == "POST":
        cv.delete()
        messages.success(request, 'CV deleted.')
        return redirect('dashboard')
    return render(request, 'builder/cv_confirm_delete.html', {'cv': cv})


@login_required
def letter_detail(request, pk):
    letter = get_object_or_404(CoverLetter, pk=pk, user=request.user)
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(
        request,
        'builder/letter_detail.html',
        {
            'letter': letter,
            'profile': profile,
        },
    )


@login_required
def letter_delete(request, pk):
    letter = get_object_or_404(CoverLetter, pk=pk, user=request.user)
    if request.method == "POST":
        letter.delete()
        messages.success(request, 'Cover letter deleted.')
        return redirect('dashboard')
    return render(
        request,
        'builder/letter_confirm_delete.html',
        {'letter': letter},
    )


@login_required
def export_pdf(request, pk):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if not profile.is_premium:
        messages.info(request, 'Upgrade to premium to export letters as PDF.')
        return redirect('upgrade_page')

    letter_obj = get_object_or_404(CoverLetter, pk=pk, user=request.user)
    response = HttpResponse(content_type='application/pdf')
    safe_job_title = slugify(letter_obj.job_title) or 'cover-letter'
    filename = f'cover_letter_{safe_job_title}.pdf'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    doc = SimpleDocTemplate(
        response, pagesize=pdf_letter,
        rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72
    )

    styles = getSampleStyleSheet()
    letter_style = ParagraphStyle(
        'LetterStyle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=11, leading=15, spaceAfter=12
    )

    story = []
    content_blocks = letter_obj.generated_content.split('\n')
    for block in content_blocks:
        if block.strip():
            story.append(Paragraph(block, letter_style))
        else:
            story.append(Spacer(1, 0.1 * inch))

    doc.build(story)
    return response


@login_required
def upgrade_page(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(
        request,
        'builder/upgrade.html',
        {
            'price_label': settings.STRIPE_PREMIUM_MONTHLY_DISPLAY,
            'profile': profile,
        },
    )


@login_required
@require_POST
def create_checkout_session(request):
    price_id = getattr(settings, 'STRIPE_PRICE_ID', None)
    monthly_amount_pence = int(
        getattr(settings, 'STRIPE_PREMIUM_MONTHLY_PENCE', 999)
    )
    currency = getattr(settings, 'STRIPE_CURRENCY', 'gbp')

    profile, _ = Profile.objects.get_or_create(user=request.user)

    stripe_kwargs = {
        'mode': 'subscription',
        'line_items': [],
        'allow_promotion_codes': True,
        'client_reference_id': str(request.user.id),
        'success_url': request.build_absolute_uri(
            reverse('payment_success')
        ) + '?session_id={CHECKOUT_SESSION_ID}',
        'cancel_url': request.build_absolute_uri(
            reverse('payment_cancelled')
        ),
    }
    if profile.stripe_customer_id:
        stripe_kwargs['customer'] = profile.stripe_customer_id
    elif request.user.email:
        stripe_kwargs['customer_email'] = request.user.email

    if price_id:
        stripe_kwargs['line_items'] = [
            {
                'price': price_id,
                'quantity': 1,
            }
        ]
    else:
        stripe_kwargs['line_items'] = [
            {
                'price_data': {
                    'currency': currency,
                    'unit_amount': monthly_amount_pence,
                    'product_data': {
                        'name': 'AI Career Pro Premium',
                    },
                    'recurring': {
                        'interval': 'month',
                    },
                },
                'quantity': 1,
            }
        ]

    try:
        session = stripe.checkout.Session.create(**stripe_kwargs)
    except Exception as exc:
        error_message = (
            'Payment service is temporarily unavailable. '
            'Try again shortly.'
        )
        if settings.DEBUG:
            error_message = f'Unable to start Stripe checkout: {exc}'
        messages.error(
            request,
            error_message,
        )
        return redirect('upgrade_page')

    return redirect(session.url, code=303)


@login_required
@require_POST
def create_billing_portal_session(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if not profile.stripe_customer_id:
        messages.info(request, 'Start a subscription first to manage billing.')
        return redirect('upgrade_page')

    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=profile.stripe_customer_id,
            return_url=request.build_absolute_uri(reverse('dashboard')),
        )
    except Exception:
        messages.error(request, 'Unable to open billing portal right now.')
        return redirect('dashboard')

    return redirect(portal_session.url, code=303)


@login_required
def payment_success(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    session_id = request.GET.get('session_id')

    if profile.is_premium:
        messages.success(request, 'Subscription is active. Premium unlocked.')
    elif session_id:
        unlocked = _sync_profile_from_checkout_session_id(profile, session_id)
        if unlocked:
            messages.success(
                request,
                'Subscription is active. Premium unlocked.',
            )
        else:
            messages.info(
                request,
                'Payment received. Activating your subscription now.',
            )

    return render(
        request,
        'builder/success.html',
        {
            'profile': profile,
        },
    )


@login_required
def payment_cancelled(request):
    messages.info(request, 'Checkout cancelled. No charges were made.')
    return redirect('upgrade_page')


def terms_page(request):
    return render(request, 'builder/terms.html')


def privacy_page(request):
    return render(request, 'builder/privacy.html')


def refund_policy_page(request):
    return render(request, 'builder/refund_policy.html')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)
    signature = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    payload = request.body

    if not webhook_secret:
        return HttpResponseBadRequest('Webhook secret not configured.')

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=signature,
            secret=webhook_secret,
        )
    except Exception:
        return HttpResponseBadRequest('Invalid webhook signature.')

    event_type = event.get('type')
    event_object = event.get('data', {}).get('object', {})

    if event_type == 'checkout.session.completed':
        profile = _profile_from_checkout_session(event_object)
        subscription_id = event_object.get('subscription')
        customer_id = event_object.get('customer')

        if profile and customer_id:
            profile.stripe_customer_id = customer_id
            profile.save(update_fields=['stripe_customer_id'])

        if profile and subscription_id:
            subscription = stripe.Subscription.retrieve(subscription_id)
            _sync_profile_from_subscription(profile, subscription)

    if event_type in {'customer.subscription.updated'}:
        subscription_id = event_object.get('id', '')
        profile = Profile.objects.filter(
            stripe_subscription_id=subscription_id
        ).first()
        if profile:
            _sync_profile_from_subscription(profile, event_object)

    if event_type in {'customer.subscription.deleted'}:
        subscription_id = event_object.get('id', '')
        profile = Profile.objects.filter(
            stripe_subscription_id=subscription_id
        ).first()
        if profile:
            profile.is_premium = False
            profile.subscription_status = 'canceled'
            profile.current_period_end = None
            profile.save(
                update_fields=[
                    'is_premium',
                    'subscription_status',
                    'current_period_end',
                ]
            )

    return HttpResponse(status=200)
