from django import forms
from django.core.exceptions import ValidationError
from .models import Profile, User
from django.contrib.auth.password_validation import validate_password

ALLOWED_IMAGE_TYPES = ('image/jpeg', 'image/png', 'image/webp')
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


class ProfileForm(forms.ModelForm):
    remove_profile_picture = forms.BooleanField(required=False, initial=False)

    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio', 'location', 'website', 'phone']

    def clean_profile_picture(self):
        pic = self.cleaned_data.get('profile_picture')
        if not pic:
            return pic

        # Validate content type if available
        content_type = getattr(pic, 'content_type', None)
        if content_type and content_type not in ALLOWED_IMAGE_TYPES:
            raise ValidationError('Unsupported image type. Allowed: JPG, PNG, WEBP.')

        # Validate file size
        if pic.size > MAX_IMAGE_SIZE:
            raise ValidationError('Image file too large (max 5MB).')

        return pic


class ForgotPasswordForm(forms.Form):
    """Form for requesting a password reset."""
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autofocus': True,
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and not User.objects.filter(email=email).exists():
            raise ValidationError('No account found with this email address.')
        return email


class ResetPasswordForm(forms.Form):
    """Form for resetting password with verification code."""
    code = forms.CharField(
        label='Verification Code',
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter the 6-digit code sent to your email',
            'autofocus': True,
        })
    )
    new_password = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your new password',
        })
    )
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your new password',
        })
    )

    def clean_new_password(self):
        password = self.cleaned_data.get('new_password')
        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                raise ValidationError(e.messages)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('new_password')
        confirm = cleaned_data.get('confirm_password')

        if password and confirm and password != confirm:
            raise ValidationError('Passwords do not match.')

        return cleaned_data

        return pic
