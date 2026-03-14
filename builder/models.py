"""Data models for CVs, generated cover letters, and billing profile."""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class CV(models.Model):
    """Stores one reusable CV profile per user workflow."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(
        max_length=200,
        help_text="e.g., Software Engineer CV",
    )
    summary = models.TextField(
        blank=True,
        help_text="A short personal statement about your career goals.",
    )
    phone_number = models.CharField(max_length=30, blank=True)
    location = models.CharField(max_length=100, blank=True)
    education = models.TextField()
    experience = models.TextField()
    skills = models.TextField()

    def __str__(self):
        return f"{self.user.username}'s CV: {self.title}"


class CoverLetter(models.Model):
    """Stores generated cover letters linked to a CV and user."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cv = models.ForeignKey(CV, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    generated_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Letter for {self.job_title} at {self.company_name}"


class Profile(models.Model):
    """Extends user with premium and Stripe subscription metadata."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_premium = models.BooleanField(default=False)
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    subscription_status = models.CharField(max_length=50, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create a profile whenever a new auth user is created."""

    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Keep the profile persisted when a user record is saved."""

    if hasattr(instance, 'profile'):
        instance.profile.save()
