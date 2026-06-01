import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobboard_project.settings')
django.setup()

from users.jobs.models import JobPosting

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

for job in sample_jobs:
    JobPosting.objects.update_or_create(
        title=job['title'],
        company=job['company'],
        defaults={
            'location': job['location'],
            'summary': job['summary'],
            'salary_range': job['salary_range'],
            'application_link': job['application_link'],
        },
    )

print('Seed data loaded.')
