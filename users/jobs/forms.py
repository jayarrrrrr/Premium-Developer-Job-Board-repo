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
    # Allow employers to either pick one of their existing companies or type a new company name.
    company_name = forms.CharField(required=False, label='company name')

    class Meta:
        model = Job
        fields = ['company', 'company_name', 'title', 'description', 'location', 'salary', 'employment_type', 'skills_required', 'application_url']

    def __init__(self, *args, **kwargs):
        # Accept an optional `user` kwarg to scope available companies to that employer
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            qs = Company.objects.filter(employer=user)
            if qs.exists():
                self.fields['company'].queryset = qs
            else:
                # If the employer has no companies, remove the company select
                # so the user can only enter a new company name.
                self.fields.pop('company', None)

    def clean(self):
        cleaned = super().clean()
        company = cleaned.get('company')
        company_name = cleaned.get('company_name')

        # If no existing company selected, require a new company name
        if not company and not company_name:
            raise ValidationError('Please select an existing company or enter a new company name.')

        return cleaned


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['resume', 'cover_letter']
