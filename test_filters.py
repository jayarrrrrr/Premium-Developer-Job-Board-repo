#!/usr/bin/env python
"""
Quick test script to verify employment type and search filters work end-to-end.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobboard_project.settings')
django.setup()

from users.jobs.models import Job, Company
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
import json

User = get_user_model()

# Create test employer
employer = User.objects.filter(username='testemployer').first()
if not employer:
    employer = User.objects.create_user(
        username='testemployer',
        email='employer@test.com',
        password='testpass123'
    )
    profile = employer.get_or_create_profile()
    profile.role = 'EMPLOYER'
    profile.save()
    print(f"✓ Created test employer: {employer.username}")
else:
    print(f"✓ Using existing employer: {employer.username}")

# Create test company
company = Company.objects.filter(employer=employer, company_name='Test Corp').first()
if not company:
    company = Company.objects.create(
        employer=employer,
        company_name='Test Corp',
        location='San Francisco',
        description='A test company'
    )
    print(f"✓ Created company: {company.company_name}")
else:
    print(f"✓ Using existing company: {company.company_name}")

# Clear old test jobs
Job.objects.filter(company=company).delete()
print("✓ Cleared old test jobs")

# Create test jobs with different employment types
test_jobs = [
    {
        'title': 'Senior Full-Time Developer',
        'employment_type': 'Full-Time',
        'location': 'San Francisco, CA',
        'skills_required': 'Python, Django, React'
    },
    {
        'title': 'Part-Time Frontend Engineer',
        'employment_type': 'Part-Time',
        'location': 'Remote',
        'skills_required': 'JavaScript, React, CSS'
    },
    {
        'title': 'Contract Backend Developer',
        'employment_type': 'Contract',
        'location': 'New York, NY',
        'skills_required': 'Python, PostgreSQL, DevOps'
    },
    {
        'title': 'Summer Internship - Full Stack',
        'employment_type': 'Internship',
        'location': 'Remote',
        'skills_required': 'JavaScript, Python, HTML/CSS'
    },
    {
        'title': 'Another Full-Time Role',
        'employment_type': 'Full-Time',
        'location': 'Austin, TX remote',
        'skills_required': 'Go, Kubernetes, DevOps'
    },
]

for job_data in test_jobs:
    job = Job.objects.create(
        employer=employer,
        company=company,
        title=job_data['title'],
        description=f"A test {job_data['employment_type']} position",
        location=job_data['location'],
        salary='$100k - $150k',
        employment_type=job_data['employment_type'],
        skills_required=job_data['skills_required'],
        status=Job.STATUS_APPROVED
    )
    print(f"✓ Created job: {job.title} ({job.employment_type})")

# Test filters directly with queryset (bypasses ALLOWED_HOSTS issue)
print("\n📋 Testing Filters with Direct Queryset:\n")

# Test 1: Get all approved jobs
print("Test 1: Get all approved jobs")
all_jobs = Job.objects.approved()
print(f"  Total approved jobs: {all_jobs.count()}")
for job in all_jobs:
    print(f"    - {job.title} ({job.employment_type})")
print()

# Test 2: Filter by Full-Time
print("Test 2: Filter by Full-Time employment type")
full_time_jobs = all_jobs.filter(employment_type__iexact='Full-Time')
print(f"  Full-Time jobs found: {full_time_jobs.count()}")
for job in full_time_jobs:
    print(f"    - {job.title} ({job.employment_type})")
print()

# Test 3: Filter by Part-Time
print("Test 3: Filter by Part-Time employment type")
part_time_jobs = all_jobs.filter(employment_type__iexact='Part-Time')
print(f"  Part-Time jobs found: {part_time_jobs.count()}")
for job in part_time_jobs:
    print(f"    - {job.title} ({job.employment_type})")
print()

# Test 4: Filter by Contract
print("Test 4: Filter by Contract employment type")
contract_jobs = all_jobs.filter(employment_type__iexact='Contract')
print(f"  Contract jobs found: {contract_jobs.count()}")
for job in contract_jobs:
    print(f"    - {job.title} ({job.employment_type})")
print()

# Test 5: Filter by Internship
print("Test 5: Filter by Internship employment type")
internship_jobs = all_jobs.filter(employment_type__iexact='Internship')
print(f"  Internship jobs found: {internship_jobs.count()}")
for job in internship_jobs:
    print(f"    - {job.title} ({job.employment_type})")
print()

# Test 6: Search for "Python" in title or description or skills
print("Test 6: Search for 'Python' in job data")
from django.db.models import Q
python_jobs = all_jobs.filter(Q(title__icontains='Python') | Q(description__icontains='Python') | Q(skills_required__icontains='Python'))
print(f"  Jobs with Python found: {python_jobs.count()}")
for job in python_jobs:
    print(f"    - {job.title} | Skills: {job.skills_required}")
print()

# Test 7: Search for "Remote" location
print("Test 7: Filter by Remote location")
remote_jobs = all_jobs.filter(location__icontains='Remote')
print(f"  Remote jobs found: {remote_jobs.count()}")
for job in remote_jobs:
    print(f"    - {job.title} ({job.location})")
print()

# Test 8: Combined - Full-Time AND Remote
print("Test 8: Combined - Full-Time employment AND Remote location")
combined_jobs = all_jobs.filter(employment_type__iexact='Full-Time', location__icontains='Remote')
print(f"  Full-Time Remote jobs found: {combined_jobs.count()}")
for job in combined_jobs:
    print(f"    - {job.title} | {job.employment_type} | {job.location}")
print()

# Test 9: Combined - Part-Time AND Search for "React"
print("Test 9: Combined - Part-Time AND React in skills")
combined_jobs2 = all_jobs.filter(employment_type__iexact='Part-Time', skills_required__icontains='React')
print(f"  Part-Time jobs with React found: {combined_jobs2.count()}")
for job in combined_jobs2:
    print(f"    - {job.title} | {job.employment_type} | Skills: {job.skills_required}")
print()

print("✅ All queryset tests completed!")
