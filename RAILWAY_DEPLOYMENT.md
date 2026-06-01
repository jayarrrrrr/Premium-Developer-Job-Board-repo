# Railway Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Premium Developer Job Board to Railway with Cloudinary for media storage and Railway PostgreSQL for the database.

## Prerequisites

1. Railway account (https://railway.app)
2. Cloudinary account (https://cloudinary.com)
3. GitHub repository with your Django project
4. Git installed locally

## Step 1: Prepare for Deployment

### 1.1 Install Dependencies

```bash
pip install -r requirements.txt
```

### 1.2 Generate Secret Key

Generate a secure Django secret key:

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Save this value for later.

### 1.3 Verify Static Files Collection

```bash
python manage.py collectstatic --noinput
```

## Step 2: Set Up Cloudinary

### 2.1 Create Cloudinary Account

1. Go to https://cloudinary.com
2. Sign up for a free account
3. Go to Dashboard → Settings → API Keys
4. Note your:
   - Cloud Name
   - API Key
   - API Secret

**IMPORTANT:** Never commit these credentials to GitHub. Use environment variables only.

## Step 3: Set Up Railway

### 3.1 Create Railway Project

1. Go to https://railway.app/dashboard
2. Click "New Project"
3. Select "GitHub Repo" (or "Empty Project" if not using GitHub)
4. Connect your GitHub account and select your repository

### 3.2 Add PostgreSQL Database

1. In Railway Dashboard, click "New Service"
2. Select "PostgreSQL"
3. Railway will create a PostgreSQL database automatically
4. It will set `DATABASE_URL` environment variable automatically

### 3.3 Add Python Environment

If you started with "Empty Project":
1. Click "New Service" → "Dockerfile" (or Railway will auto-detect Python from Procfile)
2. Railway will automatically detect and use the Procfile

## Step 4: Configure Environment Variables

In Railway Dashboard:

1. Go to your project
2. Click "Variables"
3. Add the following environment variables:

```
DJANGO_SECRET_KEY = [your-generated-secret-key]
DEBUG = False
ALLOWED_HOSTS = premium-job-board.up.railway.app
CLOUDINARY_CLOUD_NAME = [your-cloudinary-cloud-name]
CLOUDINARY_API_KEY = [your-cloudinary-api-key]
CLOUDINARY_API_SECRET = [your-cloudinary-api-secret]
CSRF_TRUSTED_ORIGINS = https://premium-job-board.up.railway.app
```

> Use the actual Railway app domain for `ALLOWED_HOSTS`, e.g. `premium-job-board.up.railway.app`.

**Note:** Railway automatically sets `DATABASE_URL` when PostgreSQL is added.

## Step 5: Deploy

### 5.1 Initial Deployment

1. Push your changes to GitHub:

```bash
git add .
git commit -m "Add Railway and Cloudinary deployment configuration"
git push
```

2. Railway will automatically deploy when it detects changes to your main/master branch

### 5.2 Monitor Deployment

1. In Railway Dashboard, click on your Python service
2. Go to "Deployments" tab to see deployment logs
3. Wait for the deployment to complete

### 5.3 Run Migrations

The Procfile includes a release command that automatically runs migrations:

```
release: python manage.py migrate
```

This happens automatically before the web service starts.

## Step 6: Verify Deployment

1. Once deployed, access your application at the Railway URL provided
2. Test the following features:
   - User registration
   - User login
   - Premium membership functionality
   - Profile picture upload (should upload to Cloudinary)
   - Company logo upload (should upload to Cloudinary)
   - Job posting creation
   - Job application submission
   - JWT API authentication

## Troubleshooting

### Application Won't Start

Check the deployment logs in Railway Dashboard. Common issues:

1. **ModuleNotFoundError**: Missing dependency in requirements.txt
   - Add missing package and push to GitHub

2. **Database connection error**: DATABASE_URL not set
   - Verify PostgreSQL service was added to project
   - Railway should automatically set DATABASE_URL

3. **SecretKey error**: DJANGO_SECRET_KEY environment variable not set
   - Add DJANGO_SECRET_KEY to Variables

### Static Files Not Loading

1. Verify `WhiteNoiseMiddleware` is in MIDDLEWARE (already done)
2. Run: `python manage.py collectstatic --noinput` locally
3. Check that `STATICFILES_STORAGE` is set to use WhiteNoise

### Cloudinary Images Not Uploading

1. Verify Cloudinary credentials in environment variables
2. Check Cloudinary dashboard for any API errors
3. Ensure `cloudinary_storage` and `cloudinary` are in INSTALLED_APPS

### Database Migration Issues

1. Check if all migrations have been created locally
2. Test migrations locally:
   ```bash
   python manage.py migrate
   ```
3. The Procfile release command should run migrations automatically

## Custom Domain Setup (Optional)

### 6.1 Add Custom Domain

1. In Railway Dashboard, go to your Python service
2. Find "Domain" or "Settings"
3. Add your custom domain
4. Update DNS records with Railway's nameservers or CNAME

### 6.2 Update Environment Variables

Add your custom domain to:
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`

## Security Checklist

- [ ] DEBUG = False in production
- [ ] DJANGO_SECRET_KEY is strong and unique
- [ ] All API keys stored in environment variables (not in code)
- [ ] ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS configured
- [ ] Database backups enabled
- [ ] SSL/HTTPS enabled (Railway provides by default)
- [ ] Media files served from Cloudinary
- [ ] No sensitive data in version control

## Performance Optimization

1. **Database Connection Pooling**: Already configured in settings.py with `conn_max_age=600`
2. **Static Files Compression**: WhiteNoise automatically compresses static files
3. **Image Optimization**: Cloudinary automatically optimizes images
4. **Caching**: Configure additional caching as needed

## Monitoring

Monitor your application health:

1. Railway Dashboard → Deployments
2. Cloudinary Dashboard → Usage Analytics
3. Set up error tracking (consider Sentry)
4. Monitor database performance in Railway

## Scaling

- Railway automatically handles scaling based on resource usage
- Adjust service plan as traffic increases
- Consider database upgrades for high traffic

## Additional Resources

- Railway Documentation: https://docs.railway.app
- Cloudinary Documentation: https://cloudinary.com/documentation
- Django Deployment Checklist: https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/
- WhiteNoise Documentation: http://whitenoise.evans.io/

## Support

For Railway support: https://railway.app/support
For Cloudinary support: https://support.cloudinary.com
