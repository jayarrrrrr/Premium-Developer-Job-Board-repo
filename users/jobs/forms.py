from django import forms
from django.core.exceptions import ValidationError
from .models import Job, Company, Application, JobApplication

ALLOWED_IMAGE_TYPES = ('image/jpeg', 'image/png', 'image/webp')
ALLOWED_RESUME_TYPES = ('application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_RESUME_SIZE = 10 * 1024 * 1024  # 10MB


class CompanyForm(forms.ModelForm):
    remove_logo = forms.BooleanField(required=False, initial=False)

    class Meta:
        model = Company
        fields = ['company_name', 'logo', 'website', 'description', 'location']

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if not logo:
            return logo

        try:
            # Validate content type if available
            content_type = getattr(logo, 'content_type', None)
            if content_type and content_type not in ALLOWED_IMAGE_TYPES:
                raise ValidationError('Unsupported image type. Allowed: JPG, PNG, WEBP.')

            # Validate file size (if size is accessible)
            size = getattr(logo, 'size', None)
            if size and size > MAX_IMAGE_SIZE:
                raise ValidationError('Logo file too large (max 5MB).')
        except ValidationError:
            raise
        except Exception as e:
            # Log unexpected errors but don't fail validation
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f'Error validating logo: {e}')

        return logo


class JobForm(forms.ModelForm):
    # Allow employers to either pick one of their existing companies or type a new company name.
    company = forms.ModelChoiceField(
        queryset=Company.objects.none(),
        required=False,
        label='Existing Company',
        empty_label='-- Select a company or create a new one --'
    )
    company_name = forms.CharField(
        required=False,
        label='New Company Name',
        widget=forms.TextInput(attrs={'placeholder': 'Enter company name if not listed above'})
    )

    class Meta:
        model = Job
        fields = ['company', 'company_name', 'title', 'description', 'location', 'salary', 'employment_type', 'skills_required']

    def __init__(self, *args, **kwargs):
        # Accept an optional `user` kwarg to scope available companies to that employer
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            # Set the queryset to only the employer's companies
            self.fields['company'].queryset = Company.objects.filter(employer=user)
        else:
            # If no user provided, just allow empty queryset
            self.fields['company'].queryset = Company.objects.none()

    def clean(self):
        cleaned = super().clean()
        company = cleaned.get('company')
        company_name = cleaned.get('company_name', '').strip()

        # Require either an existing company OR a new company name
        if not company and not company_name:
            raise ValidationError(
                'Please either select an existing company from the dropdown or enter a new company name.'
            )

        return cleaned


class JobApplicationForm(forms.ModelForm):
    """Form for applicants to apply to jobs."""
    class Meta:
        model = JobApplication
        fields = ['full_name', 'email', 'phone_number', 'resume', 'cover_letter', 'portfolio_url']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Your full name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'your.email@example.com'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+1 (555) 123-4567'}),
            'cover_letter': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Tell us why you are interested in this role...'}),
            'portfolio_url': forms.URLInput(attrs={'placeholder': 'https://myportfolio.com (optional)'}),
        }

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if not resume:
            raise ValidationError('Resume file is required.')

        # Validate file size
        if resume.size > MAX_RESUME_SIZE:
            raise ValidationError('Resume file too large (max 10MB).')

        # Validate file type
        content_type = getattr(resume, 'content_type', None)
        if content_type and content_type not in ALLOWED_RESUME_TYPES:
            raise ValidationError('Unsupported resume format. Allowed: PDF, DOC, DOCX.')

        return resume


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['resume', 'cover_letter']
