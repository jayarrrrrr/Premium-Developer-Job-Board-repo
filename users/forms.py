from django import forms
from django.core.exceptions import ValidationError
from .models import Profile

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
