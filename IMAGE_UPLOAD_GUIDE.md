# Image Upload Implementation Guide

## Overview

The Premium Developer Job Board supports two types of image uploads:
1. **Developer Profile Pictures** - User avatars
2. **Company Logos** - Employer branding

Both use Cloudinary for cloud storage and are automatically optimized for web delivery.

## Architecture

### Local Development vs Production

**Local Development:**
- Images stored in `media/` directory
- Uses Django's default `ImageField`
- Files persist in project directory

**Production (Railway):**
- Images stored in Cloudinary cloud
- Uses `django-cloudinary-storage`
- Automatic CDN distribution
- Scalable and reliable

### Storage Configuration

File: `jobboard_project/settings.py`

```python
# Automatic detection based on DATABASE_URL
if os.environ.get('DATABASE_URL'):
    # Production (Railway) - use Cloudinary
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
else:
    # Local development - use local storage
    MEDIA_ROOT = BASE_DIR / 'media'
```

## Profile Picture Upload Implementation

### Model Configuration

File: `users/models.py`

```python
class Profile(models.Model):
    # Conditional field - CloudinaryField in production, ImageField locally
    if _CLOUDINARY_AVAILABLE:
        profile_picture = CloudinaryField('profile_picture', blank=True, null=True)
    else:
        profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
```

### Form Validation

File: `users/forms.py`

```python
class ProfileForm(forms.ModelForm):
    remove_profile_picture = forms.BooleanField(required=False)
    
    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio', 'location', 'website', 'phone']
    
    def clean_profile_picture(self):
        pic = self.cleaned_data.get('profile_picture')
        # Validation checks:
        # - File type: JPG, PNG, WEBP only
        # - File size: Max 5MB
```

### View Implementation

File: `users/views.py`

```python
class ProfileEditView(LoginRequiredMixin, View):
    def get(self, request):
        profile = request.user.get_or_create_profile()
        form = ProfileForm(instance=profile)
        return render(request, 'users/profile_edit.html', {'form': form})

    def post(self, request):
        profile = request.user.get_or_create_profile()
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Handle removal of existing picture
            if form.cleaned_data.get('remove_profile_picture'):
                profile.profile_picture.delete(save=False)
                profile.profile_picture = None
            
            form.save()
            return redirect('profile')
        return render(request, 'users/profile_edit.html', {'form': form})
```

### Display in Templates

**Profile Page** (`templates/users/profile.html`):
```html
{% if profile.profile_picture %}
    <img src="{{ profile.profile_picture.url }}" alt="Profile Picture" class="avatar">
{% else %}
    <img src="/static/images/default-avatar.png" alt="No Profile Picture" class="avatar">
{% endif %}
```

**Dashboard** (`templates/users/developer_dashboard.html`):
```html
<div class="navbar-avatar">
    {% if request.user.profile.profile_picture %}
        <img src="{{ request.user.profile.profile_picture.url }}" alt="Avatar">
    {% endif %}
</div>
```

## Company Logo Upload Implementation

### Model Configuration

File: `jobs/models.py`

```python
class Company(models.Model):
    employer = models.ForeignKey(User, related_name='companies', on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)
    
    # Conditional field - CloudinaryField in production, ImageField locally
    if _CLOUDINARY_AVAILABLE:
        logo = CloudinaryField('logo', blank=True, null=True)
    else:
        logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=150)
```

### Form Validation

File: `jobs/forms.py`

```python
class CompanyForm(forms.ModelForm):
    remove_logo = forms.BooleanField(required=False)
    
    class Meta:
        model = Company
        fields = ['company_name', 'logo', 'website', 'description', 'location']
    
    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        # Same validation as profile picture
        # - File type check
        # - File size check (5MB max)
```

### View Implementation

File: `jobs/views.py`

```python
class CompanyCreateView(LoginRequiredMixin, EmployerRequiredMixin, View):
    def post(self, request):
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save(commit=False)
            company.employer = request.user
            company.save()
            return redirect('employer_dashboard')
        return render(request, 'jobs/company_form.html', {'form': form})

class CompanyUpdateView(LoginRequiredMixin, EmployerRequiredMixin, View):
    def post(self, request, pk):
        company = get_object_or_404(Company, pk=pk, employer=request.user)
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            # Handle logo removal
            if form.cleaned_data.get('remove_logo'):
                company.logo.delete(save=False)
                company.logo = None
            
            form.save()
            return redirect('employer_dashboard')
        return render(request, 'jobs/company_form.html', {'form': form})
```

### URLs

File: `jobs/urls.py`

```python
urlpatterns = [
    path('employer/company/create/', CompanyCreateView.as_view(), name='company_create'),
    path('employer/company/<int:pk>/edit/', CompanyUpdateView.as_view(), name='company_edit'),
    # ... other patterns
]
```

### Display in Templates

**Job Listing** (`templates/jobs/list.html`):
```html
<div class="job-card">
    {% if job.company.logo %}
        <img src="{{ job.company.logo.url }}" alt="{{ job.company.company_name }}" class="company-logo">
    {% endif %}
    <h3>{{ job.title }}</h3>
    <p>{{ job.company.company_name }}</p>
</div>
```

**Employer Dashboard** (`templates/jobs/employer_dashboard.html`):
```html
<div class="company-profile">
    {% if company_profile.logo %}
        <img src="{{ company_profile.logo.url }}" alt="Company Logo" class="logo">
    {% endif %}
    <h2>{{ company_profile.company_name }}</h2>
</div>
```

## User Workflows

### Developer Profile Picture Upload

1. Developer logs in
2. Navigates to Profile → Edit Profile
3. Selects a JPG, PNG, or WEBP image (max 5MB)
4. Submits form
5. Image uploads to Cloudinary (production) or local storage (development)
6. Cloudinary generates optimized URL
7. Image displays in:
   - User profile page
   - Developer dashboard
   - Navbar avatar

### Employer Company Logo Upload

1. Employer logs in
2. Creates or edits a company profile
3. Selects a JPG, PNG, or WEBP image (max 5MB)
4. Submits form
5. Image uploads to Cloudinary (production) or local storage (development)
6. Logo displays on:
   - Job listings
   - Employer dashboard
   - Company profile page

### Image Removal

For both profile pictures and company logos:
1. User checks "Remove [image type]" checkbox
2. Submits form
3. Image file is deleted from storage
4. Field is cleared
5. Default placeholder displays if configured

## Image URL Optimization

### Cloudinary URL Parameters

You can add URL parameters to optimize images:

```html
<!-- Resize to fixed dimensions -->
<img src="{{ image.url }}?w=150&h=150&c=fill" alt="Thumbnail">

<!-- Face-aware thumbnail -->
<img src="{{ image.url }}?w=100&h=100&c=thumb&g=face" alt="Avatar">

<!-- Quality optimization -->
<img src="{{ image.url }}?q=auto&f=auto" alt="Auto-optimized">

<!-- Multiple formats for responsive design -->
<picture>
    <source srcset="{{ image.url }}?w=500&f=webp" type="image/webp">
    <img src="{{ image.url }}?w=500" alt="Responsive">
</picture>
```

## Testing Image Upload Functionality

### Local Testing

1. Start development server:
   ```bash
   python manage.py runserver
   ```

2. Test profile picture upload:
   - Go to http://localhost:8000/signup
   - Create developer account
   - Go to profile edit
   - Upload an image
   - Verify image displays

3. Test company logo upload:
   - Create employer account
   - Go to employer dashboard
   - Create company
   - Upload logo
   - Verify logo displays on job listings

4. Test image removal:
   - Check removal checkbox
   - Submit form
   - Verify image removed

### Production Testing (Railway)

After deployment to Railway:

1. Test profile picture upload to Cloudinary
2. Check Cloudinary Media Library for uploaded images
3. Verify images serve from Cloudinary CDN
4. Test image persistence across deployments
5. Monitor Cloudinary storage usage

### Python Unit Tests

Example test for profile picture upload:

```python
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from users.models import User, Profile

class ProfilePictureUploadTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.profile = Profile.objects.create(user=self.user)
    
    def test_profile_picture_upload(self):
        self.client.login(username='testuser', password='testpass123')
        
        # Create test image
        image = SimpleUploadedFile(
            "test.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        
        # Upload via form
        response = self.client.post('/profile/edit/', {
            'profile_picture': image,
            'bio': 'Test bio'
        }, follow=True)
        
        # Verify upload
        self.profile.refresh_from_db()
        self.assertIsNotNone(self.profile.profile_picture)
        self.assertIn('test', self.profile.profile_picture.name)
    
    def test_invalid_file_type(self):
        self.client.login(username='testuser', password='testpass123')
        
        # Create non-image file
        file = SimpleUploadedFile(
            "test.txt",
            b"text content",
            content_type="text/plain"
        )
        
        # Attempt upload
        response = self.client.post('/profile/edit/', {
            'profile_picture': file,
        })
        
        # Verify rejection
        self.assertFormError(response, 'form', 'profile_picture', 
                            'Unsupported image type. Allowed: JPG, PNG, WEBP.')
    
    def test_file_size_limit(self):
        self.client.login(username='testuser', password='testpass123')
        
        # Create oversized image
        large_file = SimpleUploadedFile(
            "large.jpg",
            b"x" * (6 * 1024 * 1024),  # 6MB
            content_type="image/jpeg"
        )
        
        # Attempt upload
        response = self.client.post('/profile/edit/', {
            'profile_picture': large_file,
        })
        
        # Verify rejection
        self.assertFormError(response, 'form', 'profile_picture',
                            'Image file too large (max 5MB).')
```

## Troubleshooting

### Images Not Uploading

1. **Check file size**: Ensure image is under 5MB
2. **Check file format**: Only JPG, PNG, WEBP allowed
3. **Check Cloudinary credentials**: Verify environment variables set correctly
4. **Check permissions**: Ensure database user can write files

### Images Display as Broken Links

1. **Check Cloudinary status**: Is Cloudinary API responding?
2. **Check URL generation**: Verify template is rendering correct URL
3. **Check CSRF tokens**: Ensure form has CSRF token
4. **Check browser cache**: Clear browser cache and retry

### Slow Image Loading

1. **Cloudinary optimization**: Images are auto-optimized
2. **CDN caching**: Cloudinary uses global CDN
3. **Browser caching**: Set appropriate cache headers

### Storage Full (Cloudinary Free Tier)

Cloudinary free tier has 25GB storage:
1. Monitor usage in Cloudinary dashboard
2. Delete old/unused images
3. Upgrade to paid plan if needed

## Security Considerations

### File Validation

- Only allow image formats: JPG, PNG, WEBP
- Enforce file size limit: 5MB
- Scan for malicious content (optional with Cloudinary)

### Access Control

- Profile pictures only accessible to owner
- Company logos accessible to employer only
- Public display of images through templates

### Storage Security

- Cloudinary stores on secure servers
- SSL/TLS encryption in transit
- Regular backups automatic

### API Key Protection

- Store API keys in environment variables only
- Never commit keys to git
- Rotate keys if compromised

## Performance Optimization

### Image Transformations

Cloudinary provides real-time transformations:
- Automatic format optimization
- Responsive image generation
- Lazy loading support

### Caching Strategies

1. **Browser caching**: Set Cache-Control headers
2. **CDN caching**: Cloudinary caches globally
3. **Database caching**: Cache image URLs in memory

### Lazy Loading Example

```html
<img src="{{ image.url }}" 
     loading="lazy" 
     alt="Lazy loaded image">
```

## Migration from Local to Cloudinary

When moving existing images to Cloudinary:

```python
# Management command: jobs/management/commands/migrate_to_cloudinary.py
from django.core.management.base import BaseCommand
from users.models import Profile

class Command(BaseCommand):
    def handle(self, *args, **options):
        for profile in Profile.objects.exclude(profile_picture=''):
            # Images automatically migrate when accessed
            # Cloudinary storage handles the transition
            self.stdout.write(f'✓ {profile.user.username}')
```

## Related Documentation

- Django File Upload: https://docs.djangoproject.com/en/5.2/topics/files/
- Cloudinary Django SDK: https://github.com/klis87/django-cloudinary-storage
- Image Optimization: https://cloudinary.com/documentation/image_optimization
