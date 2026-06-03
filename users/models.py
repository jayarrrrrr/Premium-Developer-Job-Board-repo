from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

# Attempt to use CloudinaryField when cloudinary is installed and configured;
# fall back to ImageField when the package is missing or credentials are not set.
import os
from django.conf import settings

try:
    from cloudinary.models import CloudinaryField
    _CLOUDINARY_PACKAGE_AVAILABLE = True
except Exception:
    CloudinaryField = None
    _CLOUDINARY_PACKAGE_AVAILABLE = False

# Consider Cloudinary usable only when both the package is present and the
# environment contains configured credentials (CLOUDINARY_URL or explicit keys).
_CLOUDINARY_CONFIGURED = False
if _CLOUDINARY_PACKAGE_AVAILABLE:
    if os.environ.get('CLOUDINARY_URL'):
        _CLOUDINARY_CONFIGURED = True
    elif os.environ.get('CLOUDINARY_API_KEY') and os.environ.get('CLOUDINARY_API_SECRET') and os.environ.get('CLOUDINARY_CLOUD_NAME'):
        _CLOUDINARY_CONFIGURED = True

_CLOUDINARY_AVAILABLE = _CLOUDINARY_PACKAGE_AVAILABLE and _CLOUDINARY_CONFIGURED


class User(AbstractUser):
    is_premium = models.BooleanField(default=False)
    premium_activated_at = models.DateTimeField(null=True, blank=True)
    premium_expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email or self.username

    def get_or_create_profile(self):
        try:
            profile = self.profile
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=self)

        # Keep legacy user-level premium flag aligned with profile premium status.
        if self.is_premium and not profile.is_premium:
            profile.is_premium = True
            profile.save(update_fields=['is_premium'])
        elif profile.is_premium and not self.is_premium:
            self.is_premium = True
            self.save(update_fields=['is_premium'])

        return profile

    @property
    def profile_role(self):
        return self.get_or_create_profile().role

    def get_role(self):
        """Return normalized role string: 'developer' or 'employer'.

        This maps legacy stored values to the two supported roles without
        requiring a database migration.
        """
        try:
            role = self.get_or_create_profile().role
            if not role:
                return 'developer'
            r = str(role).upper()
            if 'EMPLOY' in r or r == 'ADMIN':
                return 'employer'
            # treat job seeker / job_seeker / JOB_SEEKER as developer
            if 'JOB' in r or 'SEEK' in r or 'DEVELO' in r:
                return 'developer'
            return 'developer'
        except Exception:
            return 'developer'

    @property
    def effective_is_premium(self):
        """True if profile premium flag is set."""
        profile = self.get_or_create_profile()
        return bool(getattr(profile, 'is_premium', False))

    def activate_premium(self, months=1):
        from django.utils import timezone
        from datetime import timedelta

        self.is_premium = True
        self.premium_activated_at = timezone.now()
        self.premium_expires_at = self.premium_activated_at + timedelta(days=30 * months)
        self.save(update_fields=['is_premium', 'premium_activated_at', 'premium_expires_at'])

        profile = self.get_or_create_profile()
        if not profile.is_premium:
            profile.is_premium = True
            profile.save(update_fields=['is_premium'])


class Profile(models.Model):
    ROLE_ADMIN = 'ADMIN'
    ROLE_EMPLOYER = 'EMPLOYER'
    ROLE_JOB_SEEKER = 'JOB_SEEKER'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_EMPLOYER, 'Employer'),
        (ROLE_JOB_SEEKER, 'Job Seeker'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile', on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_JOB_SEEKER)

    # Profile fields
    if _CLOUDINARY_AVAILABLE:
        profile_picture = CloudinaryField('profile_picture', blank=True, null=True)
    else:
        profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)

    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    Profile.objects.get_or_create(user=instance)
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        pass
