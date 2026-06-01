# Production Deployment Quick Reference

**Status:** ✅ Ready for Production  
**Last Updated:** May 2026  
**Environment:** Railway + PostgreSQL + Cloudinary

## Essential Commands

### Local Development Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create local .env file
cp .env.example .env

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Prepare for Deployment
```bash
# Collect static files
python manage.py collectstatic --noinput

# Generate secret key for production
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Check for issues
python manage.py check

# Run tests
python manage.py test
```

### Deploy to Railway
```bash
# Commit all changes
git add .
git commit -m "Production deployment configuration"

# Push to main branch
git push origin main

# Railway auto-deploys on push
# Monitor at https://railway.app/dashboard
```

## Configuration Checklist

### Before Railway Deployment

**Code Repository:**
- [ ] All code committed to main branch
- [ ] No local changes
- [ ] .gitignore includes `.env` and `venv/`
- [ ] Procfile present and correct
- [ ] requirements.txt updated

**Django Configuration:**
- [ ] settings.py configured for production
- [ ] DEBUG = False in production
- [ ] ALLOWED_HOSTS set correctly
- [ ] SECRET_KEY strong and random
- [ ] Database settings dynamic (DATABASE_URL)
- [ ] Static files configuration correct

**Environment Variables:**
- [ ] DJANGO_SECRET_KEY generated
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS configured
- [ ] DATABASE_URL auto-set by Railway
- [ ] Cloudinary credentials obtained

### Railway Dashboard Setup

1. Create new project
2. Add PostgreSQL service
3. Connect GitHub repository
4. Configure environment variables:

```env
DJANGO_SECRET_KEY=<generate-new>
DEBUG=False
ALLOWED_HOSTS=yourdomain.railway.app,yourdomain.com
CLOUDINARY_CLOUD_NAME=<your-cloud-name>
CLOUDINARY_API_KEY=<your-api-key>
CLOUDINARY_API_SECRET=<your-api-secret>
CSRF_TRUSTED_ORIGINS=https://yourdomain.railway.app,https://yourdomain.com
```

### Cloudinary Setup

1. Create account at https://cloudinary.com
2. Go to Dashboard → Settings
3. Copy credentials:
   - Cloud Name
   - API Key
   - API Secret
4. Add to Railway environment variables

## File Changes Summary

### Updated Files
- `requirements.txt` - Added production packages
- `jobboard_project/settings.py` - Production configuration
- `jobs/models.py` - Company logo CloudinaryField
- `jobs/forms.py` - Logo validation
- `jobs/views.py` - Company CRUD views
- `jobs/urls.py` - Company routes
- `users/forms.py` - (No changes, already has validation)

### New Files
- `Procfile` - Railway deployment config
- `.env.example` - Environment variables template
- `jobs/migrations/0003_company_logo_image_field.py` - Model migration

### Documentation
- `RAILWAY_DEPLOYMENT.md` - Full deployment guide
- `CLOUDINARY_SETUP.md` - Cloudinary integration
- `IMAGE_UPLOAD_GUIDE.md` - Image upload details
- `DEPLOYMENT_CHECKLIST.md` - Verification checklist
- `DEPLOYMENT_SUMMARY.md` - Complete summary

## Deployment Flow

```
Local Development
    ↓
Commit to GitHub
    ↓
Push to main branch
    ↓
Railway detects changes
    ↓
Railway builds application
    ↓
Procfile release command: python manage.py migrate
    ↓
Procfile web command: gunicorn jobboard_project.wsgi
    ↓
Application live at Railway URL
```

## Key Features

✅ **Database**: PostgreSQL on Railway  
✅ **Media Storage**: Cloudinary CDN  
✅ **Static Files**: WhiteNoise compression  
✅ **Authentication**: JWT + Session  
✅ **Security**: HTTPS, CSRF protection  
✅ **Image Uploads**: Profile pictures & company logos  
✅ **Premium Features**: Membership management  

## Troubleshooting

### Application Won't Start
```
Check logs in Railway Dashboard → Deployments
Common issues:
- Missing environment variables
- Database connection error
- Import error from missing package
```

### Database Connection Error
```
Verify:
1. PostgreSQL service added to Railway
2. DATABASE_URL environment variable set
3. Check Railway logs for connection details
```

### Cloudinary Images Not Loading
```
Verify:
1. CLOUDINARY_* environment variables set correctly
2. Check Cloudinary dashboard for API status
3. Test with smaller image file
```

### Static Files Not Loading (CSS/JS)
```
Check:
1. WhiteNoise middleware in MIDDLEWARE
2. STATICFILES_STORAGE configured
3. collectstatic ran successfully
4. Check browser console for 404 errors
```

## Monitoring

### Railway Dashboard
- Monitor deployments
- View application logs
- Track resource usage
- Manage environment variables

### Cloudinary Dashboard
- Monitor media library
- Track storage usage
- View API usage statistics

### Application
- Django admin: /admin
- User registrations: Track new users
- Job postings: Monitor job creation
- Errors: Check logs for issues

## Rollback Procedure

If deployment has issues:

1. Identify the problem in logs
2. Fix code locally
3. Test fix locally
4. Commit and push to main
5. Railway auto-redeploys with fix

To revert to previous version:
1. Identify last working commit
2. Use `git revert` or create hotfix branch
3. Push to main
4. Railway redeploys

## Performance Tips

1. **Database**: Connection pooling enabled by default
2. **Static Files**: WhiteNoise compresses automatically
3. **Images**: Cloudinary optimizes automatically
4. **Caching**: Add Redis if needed for high traffic

## Security Reminders

🔒 Never commit:
- `.env` file
- Secret keys
- API credentials
- Private keys

✅ Always use:
- Environment variables for secrets
- HTTPS in production
- CSRF tokens in forms
- Input validation on all forms

## Support Contacts

- **Railway**: https://railway.app/support
- **Cloudinary**: https://support.cloudinary.com
- **Django**: https://www.djangoproject.com/

## Useful Links

- Railway Docs: https://docs.railway.app
- Django Docs: https://docs.djangoproject.com
- Cloudinary Docs: https://cloudinary.com/documentation
- DRF: https://www.django-rest-framework.org

## Quick Deployment Checklist

```bash
# Day 1: Prepare
□ pip install -r requirements.txt
□ python manage.py migrate
□ python manage.py collectstatic --noinput
□ python manage.py check
□ python manage.py test

# Day 2: Deploy
□ Generate SECRET_KEY
□ Create Cloudinary account & get credentials
□ Create Railway project
□ Set up environment variables
□ git push origin main

# Day 3: Verify
□ Access application URL
□ Test user registration
□ Test login
□ Test image upload
□ Check Cloudinary media library
□ Monitor Railway logs

# Ongoing
□ Monitor Railway dashboard daily
□ Check error logs regularly
□ Track Cloudinary storage usage
□ Update dependencies monthly
```

## Notes

- All migrations run automatically via Procfile
- No manual database setup needed
- Cloudinary handles image optimization
- Railway auto-scales if needed
- SSL certificate auto-renewed

---

**Ready to deploy? Start with RAILWAY_DEPLOYMENT.md**
