import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobboard_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.jobs.models import JobPosting, Job, Company

User = get_user_model()

sample_jobs = [
    {
        'title': 'Senior Django Engineer',
        'company': 'Tech Growth Co.',
        'location': 'Remote',
        'summary': 'Build and maintain scalable web APIs for developer products.',
        'salary_range': '$120k - $150k',
        'application_link': 'https://apply.techgrowth.co/django-engineer',
    },
    {
        'title': 'Frontend Developer',
        'company': 'Pixel Labs',
        'location': 'New York, NY',
        'summary': 'Create polished UI experiences with vanilla JS and progressive enhancement.',
        'salary_range': '$95k - $115k',
        'application_link': 'https://careers.pixellabs.com/frontend',
    },
    {
        'title': 'Backend API Engineer',
        'company': 'Cloud Commerce',
        'location': 'London, UK',
        'summary': 'Design performant backend systems and publish REST APIs for global customers.',
        'salary_range': '£80k - £105k',
        'application_link': 'https://cloudcommerce.jobs/api-engineer',
    },
]

employer, created = User.objects.get_or_create(
    username='employer1',
    defaults={
        'email': 'employer@example.com',
    },
)
if created:
    employer.set_password('Password123!')
    employer.save()

profile = employer.get_or_create_profile()
if profile.role != 'EMPLOYER':
    profile.role = 'EMPLOYER'
    profile.save(update_fields=['role'])

for job_data in sample_jobs:
    JobPosting.objects.update_or_create(
        title=job_data['title'],
        company=job_data['company'],
        defaults={
            'location': job_data['location'],
            'summary': job_data['summary'],
            'salary_range': job_data['salary_range'],
            'application_link': job_data['application_link'],
        },
    )

    company, _ = Company.objects.update_or_create(
        employer=employer,
        company_name=job_data['company'],
        defaults={
            'location': job_data['location'],
        },
    )

    Job.objects.update_or_create(
        title=job_data['title'],
        company=company,
        defaults={
            'employer': employer,
            'description': job_data['summary'],
            'location': job_data['location'],
            'salary': job_data['salary_range'],
            'status': Job.STATUS_APPROVED,
        },
    )

print('Seed data loaded.')
