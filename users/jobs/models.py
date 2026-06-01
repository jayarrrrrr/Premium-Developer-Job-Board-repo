from django.conf import settings
from django.db import models

# Attempt to use CloudinaryField when cloudinary is installed; fall back to ImageField
try:
    from cloudinary.models import CloudinaryField
    _CLOUDINARY_AVAILABLE = True
except Exception:
    CloudinaryField = None
    _CLOUDINARY_AVAILABLE = False


class JobPosting(models.Model):
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=150)
    location = models.CharField(max_length=120)
    summary = models.TextField()
    salary_range = models.CharField(max_length=100)
    application_link = models.URLField()
    posted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-posted_at']

    def __str__(self):
        return f"{self.title} at {self.company}"


class Company(models.Model):
    employer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='companies', on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)
    
    # Logo field with Cloudinary support
    if _CLOUDINARY_AVAILABLE:
        logo = CloudinaryField('logo', blank=True, null=True)
    else:
        logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name


class Job(models.Model):
    EMPLOYMENT_FULL_TIME = 'Full-Time'
    EMPLOYMENT_PART_TIME = 'Part-Time'
    EMPLOYMENT_CONTRACT = 'Contract'
    EMPLOYMENT_INTERNSHIP = 'Internship'

    EMPLOYMENT_CHOICES = [
        (EMPLOYMENT_FULL_TIME, 'Full-Time'),
        (EMPLOYMENT_PART_TIME, 'Part-Time'),
        (EMPLOYMENT_CONTRACT, 'Contract'),
        (EMPLOYMENT_INTERNSHIP, 'Internship'),
    ]

    STATUS_PENDING = 'PENDING'
    STATUS_APPROVED = 'APPROVED'
    STATUS_REJECTED = 'REJECTED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    employer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='jobs', on_delete=models.CASCADE)
    company = models.ForeignKey(Company, related_name='jobs', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=150)
    salary = models.CharField(max_length=120)
    employment_type = models.CharField(max_length=30, choices=EMPLOYMENT_CHOICES, default=EMPLOYMENT_FULL_TIME)
    skills_required = models.CharField(max_length=300, blank=True)
    application_url = models.URLField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} at {self.company.company_name}"


class Application(models.Model):
    STATUS_SUBMITTED = 'SUBMITTED'
    STATUS_REVIEWED = 'REVIEWED'
    STATUS_ACCEPTED = 'ACCEPTED'
    STATUS_REJECTED = 'REJECTED'

    STATUS_CHOICES = [
        (STATUS_SUBMITTED, 'Submitted'),
        (STATUS_REVIEWED, 'Reviewed'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='applications', on_delete=models.CASCADE)
    job = models.ForeignKey(Job, related_name='applications', on_delete=models.CASCADE)
    resume = models.TextField(blank=True)
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SUBMITTED)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-applied_at']

    def __str__(self):
        return f"Application by {self.applicant.username} to {self.job.title}"


class SavedJob(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='saved_jobs', on_delete=models.CASCADE)
    job = models.ForeignKey(Job, related_name='saved_jobs', on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')
        ordering = ['-saved_at']

    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"
