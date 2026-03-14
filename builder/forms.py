"""Forms used by authentication and CV management views."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CV


class SignupForm(UserCreationForm):
    """Custom signup form with optional email for smoother onboarding."""

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'you@example.com (optional)',
            }
        ),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        """Apply Bootstrap classes and friendly placeholders."""

        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {
                'class': 'form-control',
                'placeholder': 'Choose a username',
            }
        )
        self.fields['password1'].widget.attrs.update(
            {
                'class': 'form-control',
                'placeholder': 'Create a password',
            }
        )
        self.fields['password2'].widget.attrs.update(
            {
                'class': 'form-control',
                'placeholder': 'Confirm your password',
            }
        )

    def clean_email(self):
        """Normalize and validate email uniqueness only when provided."""

        email = (self.cleaned_data.get('email') or '').strip().lower()
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                'An account with this email already exists.'
            )
        return email

    def save(self, commit=True):
        """Persist email onto the user record before saving."""

        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class CVForm(forms.ModelForm):
    """Form for collecting structured CV data used by the AI prompt."""

    class Meta:
        model = CV
        fields = [
            'title', 'summary', 'phone_number', 'location',
            'education', 'experience', 'skills',
        ]
        labels = {
            'title': 'CV Profile Name',
            'summary': 'Personal Statement',
            'phone_number': 'Phone Number',
            'location': 'Location',
            'education': 'Education',
            'experience': 'Work Experience',
            'skills': 'Skills',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Retail CV, Developer CV',
            }),
            'summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': (
                    'e.g. Results-driven software engineer with 3 years '
                    'of experience building web APIs. Passionate about '
                    'clean code and mentoring junior developers.'
                ),
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. +44 7700 900000',
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. London, UK',
            }),
            'education': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': (
                    'e.g.\n'
                    'BSc Computer Science, University of Manchester '
                    '(2019\u20132022)\n'
                    'A-Levels: Maths (A), Physics (B), Computing (A*)'
                ),
            }),
            'experience': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': (
                    'e.g.\n'
                    'Junior Developer, Acme Ltd (2022\u2013present)\n'
                    '\u2013 Built REST APIs used by 10,000+ daily users\n'
                    '\u2013 Reduced page load time by 40% via caching\n\n'
                    'Retail Assistant, Starbucks (2020\u20132022)\n'
                    '\u2013 Managed stock and peak-hour customer operations'
                ),
            }),
            'skills': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': (
                    'e.g. Python, Django, React, PostgreSQL, Git, '
                    'Agile, communication, problem-solving'
                ),
            }),
        }

    def _clean_non_empty_text(self, field_name):
        """Shared validator for required textareas after trimming spaces."""

        value = self.cleaned_data.get(field_name, '')
        cleaned_value = value.strip()
        if not cleaned_value:
            raise forms.ValidationError('This field cannot be empty.')
        return cleaned_value

    def clean_title(self):
        return self._clean_non_empty_text('title')

    def clean_education(self):
        return self._clean_non_empty_text('education')

    def clean_experience(self):
        return self._clean_non_empty_text('experience')

    def clean_skills(self):
        return self._clean_non_empty_text('skills')
