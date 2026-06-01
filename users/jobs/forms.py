from django import forms
from django.core.exceptions import ValidationError
from .models import Job, Company, Application

ALLOWED_IMAGE_TYPES = ('image/jpeg', 'image/png', 'image/webp')
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


class CompanyForm(forms.ModelForm):
    remove_logo = forms.BooleanField(required=False, initial=False)

    class Meta:
        model = Company
        fields = ['company_name', 'logo', 'website', 'description', 'location']

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if not logo:
            return logo

        # Validate content type if available
        content_type = getattr(logo, 'content_type', None)
        if content_type and content_type not in ALLOWED_IMAGE_TYPES:
            raise ValidationError('Unsupported image type. Allowed: JPG, PNG, WEBP.')

        # Validate file size
        if logo.size > MAX_IMAGE_SIZE:
            raise ValidationError('Logo file too large (max 5MB).')

        return logo


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['company', 'title', 'description', 'location', 'salary', 'employment_type', 'skills_required', 'application_url']


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['resume', 'cover_letter']
