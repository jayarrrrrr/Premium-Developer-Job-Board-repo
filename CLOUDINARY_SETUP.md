# Cloudinary Integration Guide

## Overview

Cloudinary is a cloud-based service for managing, transforming, and delivering images and videos. This guide explains the Cloudinary setup for the Premium Developer Job Board.

## What Gets Stored in Cloudinary

1. **Developer Profile Pictures** - User avatar images
2. **Company Logos** - Employer company branding
3. **Job Listing Images** - Any images attached to job postings

## Setup Instructions

### Step 1: Create Cloudinary Account

1. Visit https://cloudinary.com/users/register/free
2. Sign up with your email
3. Verify your email address
4. Set up your cloud name (used in API calls)

### Step 2: Get API Credentials

1. Go to Dashboard (https://cloudinary.com/console/dashboard)
2. Under "Account Details", find:
   - **Cloud Name** - Your public cloud identifier
   - **API Key** - Your API authentication key
   - **API Secret** - Your private authentication key

### Step 3: Configure Environment Variables

Add these to your Railway environment variables or `.env` file:

```
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### Step 4: Test Cloudinary Integration

```bash
# Collect static files
python manage.py collectstatic

# Run development server
python manage.py runserver

# Test image upload:
# 1. Go to user registration page
# 2. Create new account
# 3. Go to profile page
# 4. Upload a profile picture
# 5. Check Cloudinary dashboard to verify image was uploaded
```

## Cloudinary Settings in Django

### Configuration Location

File: `jobboard_project/settings.py`

```python
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}

# Use Cloudinary for production media storage
if os.environ.get('DATABASE_URL'):
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

### How It Works

- **Local Development**: Uses local file storage (`MEDIA_ROOT`)
- **Production (Railway)**: Uses Cloudinary cloud storage
- **Automatic Detection**: Checks for `DATABASE_URL` environment variable to switch storage

## Image Upload Features

### Profile Picture Upload

**File**: `users/forms.py`

Features:
- Accepts JPG, PNG, WEBP formats
- Max file size: 5MB
- Automatically uploaded to Cloudinary
- Can be viewed in user profile
- Can be edited or removed

### Company Logo Upload

**File**: `jobs/forms.py`

Features:
- Accepts JPG, PNG, WEBP formats
- Max file size: 5MB
- Automatically uploaded to Cloudinary
- Displayed on company profile
- Displayed on job listings

## Accessing Uploaded Images

### Cloudinary Media Library

1. Log in to Cloudinary Dashboard
2. Go to "Media Library"
3. View all uploaded images organized by folder:
   - `profiles/` - Developer profile pictures
   - `company_logos/` - Company logos

### In Application

Images are accessed via:
- User profile pages: Display profile picture
- Job listings: Display company logo
- Developer dashboard: Show avatar
- Employer dashboard: Show company logo

## Image Transformations

Cloudinary allows real-time image transformations (resizing, compression, etc.)

### Example Transformations

```python
# In Django templates or views
{{ profile.profile_picture.url }}
# Returns optimized Cloudinary URL with transformations

# You can add custom transformations
image_url = profile.profile_picture.url
resized_url = image_url + "?w=150&h=150&c=fill"  # Resize to 150x150
thumbnail_url = image_url + "?w=50&h=50&c=thumb&g=face"  # Face-aware thumbnail
```

## Storage Quota and Limits

### Free Tier (Cloudinary)

- 25 GB storage
- 25 GB monthly transformations
- Unlimited transformations
- Full media library access

### Upgrade if Needed

1. Go to Cloudinary Dashboard
2. Click "Upgrade Plan"
3. Choose plan based on your needs
4. Billing is per usage or fixed monthly

## Backups and Data Safety

### Cloudinary Backups

- Cloudinary maintains redundant backups
- 99.9% uptime SLA
- Images distributed across CDN globally
- Automatic disaster recovery

### Local Backups (Recommended)

To backup images stored in Cloudinary:

1. Use Cloudinary API to download all media
2. Schedule regular backups
3. Test restoration procedures

## Security Considerations

### API Key Protection

- Never commit API keys to GitHub
- Use environment variables only
- Rotate API keys periodically if compromised
- Use a .gitignore to exclude `.env` files

### Upload Restrictions

Current implementation restricts uploads to:
- Image formats: JPG, PNG, WEBP
- File size: Max 5MB
- Upload location: Authenticated users only

### Cloudinary Security

- Enable signed uploads for extra security (optional)
- Restrict API key permissions if needed
- Monitor usage for unusual activity

## Troubleshooting

### Images Not Uploading

1. **Check API Credentials**: Verify CLOUDINARY_* environment variables are set correctly
2. **Check Permissions**: Ensure API key has write permissions
3. **Check File Size**: Ensure image is under 5MB
4. **Check Format**: Verify image is JPG, PNG, or WEBP
5. **Check Internet**: Verify connection to Cloudinary API

### Slow Image Loading

1. **CDN Optimization**: Cloudinary uses global CDN - should be fast
2. **Image Size**: Reduce image dimensions before upload
3. **Caching**: Browser caching should improve speed
4. **Network**: Check internet connection speed

### Storage Full

1. Log in to Cloudinary Dashboard
2. Review "Media Library" for unused images
3. Delete old or duplicate images
4. Consider upgrading plan

## Performance Tips

1. **Compression**: Cloudinary automatically compresses images
2. **Responsive Images**: Use Cloudinary URL parameters for responsive design
3. **Lazy Loading**: Implement lazy loading in templates for faster page load
4. **Caching**: Set appropriate cache headers

## Testing

### Test Image Upload

```python
# test_image_upload.py
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from users.models import User, Profile

class ImageUploadTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = Profile.objects.create(user=self.user)
    
    def test_profile_picture_upload(self):
        self.client.login(username='testuser', password='testpass123')
        
        # Create a test image
        image = SimpleUploadedFile(
            "test.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        
        response = self.client.post('/profile/edit/', {
            'profile_picture': image,
            'bio': 'Test bio'
        })
        
        # Check image was uploaded
        self.profile.refresh_from_db()
        self.assertIsNotNone(self.profile.profile_picture)
```

## Migration Path

### From Local Storage to Cloudinary

Existing images stored locally will need to be migrated:

1. Create Django management command for migration
2. Upload local media files to Cloudinary
3. Update database references
4. Remove local media files

Example management command:

```python
# jobs/management/commands/migrate_to_cloudinary.py
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from users.models import Profile
import os

class Command(BaseCommand):
    help = 'Migrate existing profile pictures to Cloudinary'
    
    def handle(self, *args, **options):
        count = 0
        for profile in Profile.objects.filter(profile_picture__isnull=False):
            if profile.profile_picture and profile.profile_picture.name:
                # Cloudinary storage will handle the rest
                self.stdout.write(f'Processed: {profile.user.username}')
                count += 1
        self.stdout.write(f'Migrated {count} profile pictures')
```

## Support and Resources

- Cloudinary Docs: https://cloudinary.com/documentation
- Cloudinary Dashboard: https://cloudinary.com/console
- Django-Cloudinary-Storage: https://github.com/klis87/django-cloudinary-storage
- Cloudinary Python SDK: https://github.com/cloudinary/cloudinary_python
