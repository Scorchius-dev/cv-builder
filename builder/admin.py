"""Admin registrations for project data models."""

from django.contrib import admin

from .models import CV, CoverLetter, Profile


@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    """CV management view in Django admin."""

    list_display = ('title', 'user')
    search_fields = ('title', 'user__username', 'skills')
    list_select_related = ('user',)


@admin.register(CoverLetter)
class CoverLetterAdmin(admin.ModelAdmin):
    """Cover letter management view in Django admin."""

    list_display = ('job_title', 'company_name', 'user', 'created_at')
    search_fields = (
        'job_title',
        'company_name',
        'user__username',
        'generated_content',
    )
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    list_select_related = ('user', 'cv')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Subscription profile management view in Django admin."""

    list_display = ('user', 'is_premium')
    search_fields = ('user__username',)
    list_filter = ('is_premium',)
