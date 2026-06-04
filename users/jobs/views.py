from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.db import models
from django.db.models import Q
from .models import JobPosting, Job
from .serializers import JobPostingSerializer, JobSerializer
from .services import SearchService


class JobPostingPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'page': self.page.number,
            'page_size': self.page.paginator.per_page,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })


class JobPostingViewSet(viewsets.ReadOnlyModelViewSet):
    """Legacy ViewSet for old JobPosting model."""
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer
    pagination_class = JobPostingPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.query_params.get('search')
        location = self.request.query_params.get('location')
        filters = SearchService.build_filters(search_term, location)
        return queryset.filter(filters)


class JobViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for new internal Job model with approved jobs only."""
    queryset = Job.objects.approved()
    serializer_class = JobSerializer
    pagination_class = JobPostingPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = (self.request.query_params.get('search') or '').strip()
        location = (self.request.query_params.get('location') or '').strip()

        logger.debug('JobViewSet fetching approved jobs search=%s location=%s', search_term, location)

        # Filter by search term if provided
        if search_term:
            queryset = queryset.filter(
                Q(title__icontains=search_term) |
                Q(company__company_name__icontains=search_term) |
                Q(description__icontains=search_term) |
                Q(skills_required__icontains=search_term)
            )

        # Filter by location if provided
        if location:
            queryset = queryset.filter(location__icontains=location)

        # Filter by exact employment type if provided via frontend filters.
        employment_type = (self.request.query_params.get('employment_type') or '').strip()
        if employment_type and employment_type.lower() != 'all':
            queryset = queryset.filter(employment_type__iexact=employment_type)

        logger.debug('JobViewSet returning queryset count=%d', queryset.count())
        return queryset


# Django web views for multi-role app
import logging

from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from .models import Job, Company, Application, SavedJob, JobApplication
from .forms import JobForm, CompanyForm, ApplicationForm, JobApplicationForm
from django.urls import reverse

logger = logging.getLogger(__name__)


class JobListView(TemplateView):
    template_name = 'jobs/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        approved_jobs = Job.objects.approved()
        logger.debug('JobListView loaded jobs count=%d', approved_jobs.count())
        context['jobs'] = approved_jobs
        context['job_count'] = approved_jobs.count()
        context['active_jobs'] = approved_jobs.count()
        context['employment_type_choices'] = Job.EMPLOYMENT_CHOICES
        return context


class JobDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        job = get_object_or_404(Job, pk=pk, status__in=[Job.STATUS_APPROVED, Job.STATUS_PENDING])
        can_view_salary = False
        can_apply = False
        already_applied = False
        
        if request.user.is_authenticated:
            user = request.user
            profile = user.get_or_create_profile()
            if getattr(user, 'is_staff', False):
                can_view_salary = True
                can_apply = False  # Staff don't apply
            elif profile.role == 'EMPLOYER':
                can_view_salary = True
                can_apply = False  # Employers don't apply
            else:
                try:
                    if job.employer_id and user.id == job.employer_id:
                        can_view_salary = True
                except Exception:
                    pass
                if profile.is_premium:
                    can_view_salary = True
                    can_apply = True
                    # Check if user already applied
                    already_applied = JobApplication.objects.filter(job=job, applicant=user).exists()
        
        return render(request, 'jobs/detail.html', {
            'job': job,
            'can_view_salary': can_view_salary,
            'can_apply': can_apply,
            'already_applied': already_applied,
        })


class EmployerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        try:
            return self.request.user.is_authenticated and self.request.user.get_or_create_profile().role == 'EMPLOYER'
        except Exception:
            return False


class JobCreateView(LoginRequiredMixin, EmployerRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = JobForm(user=request.user)
        return render(request, 'jobs/form.html', {'form': form, 'creating': True})

    def post(self, request, *args, **kwargs):
        form = JobForm(request.POST, user=request.user)
        if form.is_valid():
            job = form.save(commit=False)
            # If a new company name was provided, create the company and assign it
            company_name = form.cleaned_data.get('company_name')
            if not job.company_id and company_name:
                company = Company.objects.create(employer=request.user, company_name=company_name)
                job.company = company

            job.employer = request.user
            # Auto-approve jobs when created (can be changed to PENDING for admin review)
            job.status = Job.STATUS_APPROVED
            job.save()
            return redirect('employer_dashboard')
        return render(request, 'jobs/form.html', {'form': form, 'creating': True})


class JobUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        job = get_object_or_404(Job, pk=pk)
        if job.employer != request.user and not request.user.is_staff:
            return redirect('job_list')
        form = JobForm(instance=job, user=request.user)
        return render(request, 'jobs/form.html', {'form': form, 'job': job})

    def post(self, request, pk, *args, **kwargs):
        job = get_object_or_404(Job, pk=pk)
        if job.employer != request.user and not request.user.is_staff:
            return redirect('job_list')
        form = JobForm(request.POST, instance=job, user=request.user)
        if form.is_valid():
            # If a new company name was provided, create or assign it
            company_name = form.cleaned_data.get('company_name')
            if not form.instance.company_id and company_name:
                company = Company.objects.create(employer=request.user, company_name=company_name)
                form.instance.company = company
            form.save()
            return redirect('employer_dashboard')
        return render(request, 'jobs/form.html', {'form': form, 'job': job})


class JobDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        job = get_object_or_404(Job, pk=pk)
        if job.employer != request.user and not request.user.is_staff:
            messages.error(request, 'You do not have permission to delete this job.')
            return redirect('job_list')
        job.delete()
        messages.success(request, 'Job deleted successfully.')
        return redirect('employer_dashboard')


class ApplyJobView(LoginRequiredMixin, View):
    """New view for applying to jobs with JobApplication model."""
    
    def get(self, request, pk, *args, **kwargs):
        job = get_object_or_404(Job, pk=pk, status=Job.STATUS_APPROVED)
        
        # Check if user can apply (must be premium)
        profile = request.user.get_or_create_profile()
        if profile.role == 'EMPLOYER' or not profile.is_premium:
            messages.error(request, 'You must be a Premium member to apply for jobs.')
            return redirect('job_detail', pk=pk)
        
        # Check if already applied
        if JobApplication.objects.filter(job=job, applicant=request.user).exists():
            messages.info(request, 'You have already applied for this job.')
            return redirect('job_detail', pk=pk)
        
        # Pre-fill form with user data
        initial_data = {
            'full_name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
        }
        form = JobApplicationForm(initial=initial_data)
        
        return render(request, 'jobs/apply.html', {
            'form': form,
            'job': job,
        })
    
    def post(self, request, pk, *args, **kwargs):
        job = get_object_or_404(Job, pk=pk, status=Job.STATUS_APPROVED)
        
        # Check if user can apply
        profile = request.user.get_or_create_profile()
        if profile.role == 'EMPLOYER' or not profile.is_premium:
            messages.error(request, 'You must be a Premium member to apply for jobs.')
            return redirect('job_detail', pk=pk)
        
        # Prevent duplicate applications
        if JobApplication.objects.filter(job=job, applicant=request.user).exists():
            messages.error(request, 'You have already applied for this job.')
            return redirect('job_detail', pk=pk)
        
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, 'Your application has been submitted successfully!')
            return redirect('job_detail', pk=pk)
        
        return render(request, 'jobs/apply.html', {
            'form': form,
            'job': job,
        })


class SaveJobView(View):
    """Toggle save/unsave for a job.
    Returns JSON when requested via AJAX, otherwise redirects to saved_jobs.
    Only non-employer authenticated users can save jobs.
    """
    def post(self, request, pk, *args, **kwargs):
        # Determine if request expects JSON
        accepts_json = 'application/json' in request.META.get('HTTP_ACCEPT', '') or request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

        if not request.user.is_authenticated:
            if accepts_json:
                from django.http import JsonResponse
                return JsonResponse({'detail': 'Authentication required.'}, status=401)
            return redirect('login')

        profile = request.user.get_or_create_profile()
        if profile.role == 'EMPLOYER':
            if accepts_json:
                from django.http import JsonResponse
                return JsonResponse({'detail': 'Employers cannot save jobs.'}, status=403)
            messages.error(request, 'Employers cannot save jobs.')
            return redirect('job_list')

        job = get_object_or_404(Job, pk=pk, status=Job.STATUS_APPROVED)

        saved_obj = SavedJob.objects.filter(user=request.user, job=job).first()
        if saved_obj:
            # Unsave
            saved_obj.delete()
            saved = False
        else:
            SavedJob.objects.create(user=request.user, job=job)
            saved = True

        if accepts_json:
            from django.http import JsonResponse
            return JsonResponse({'saved': saved}, status=200)

        return redirect('saved_jobs')


class SavedJobsView(LoginRequiredMixin, TemplateView):
    template_name = 'jobs/saved.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['saved'] = SavedJob.objects.filter(user=self.request.user)
        return context


class ApplicationHistoryView(LoginRequiredMixin, TemplateView):
    template_name = 'jobs/applications.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['applications'] = Application.objects.filter(applicant=self.request.user)
        return context


class JobApplicantsView(LoginRequiredMixin, TemplateView):
    template_name = 'jobs/applicants.html'

    def get(self, request, pk, *args, **kwargs):
        job = get_object_or_404(Job, pk=pk)
        
        # Only employer or staff can view applicants
        if job.employer != request.user and not request.user.is_staff:
            messages.error(request, 'You do not have permission to view applicants for this job.')
            return redirect('job_list')
        
        applicants = job.job_applications.all().order_by('-applied_at')

        # Map job_application id -> existing Application.status (if previously created)
        application_statuses = {}
        for app in applicants:
            existing = Application.objects.filter(job=job, applicant=app.applicant).first()
            if existing:
                application_statuses[app.id] = existing.status
                # attach status to the JobApplication instance for template access
                setattr(app, 'status', existing.status)
            else:
                application_statuses[app.id] = Application.STATUS_SUBMITTED
                setattr(app, 'status', Application.STATUS_SUBMITTED)

        return render(request, self.template_name, {
            'job': job,
            'applicants': applicants,
            'application_statuses': application_statuses,
        })


class AcceptApplicationView(LoginRequiredMixin, View):
    """Allows an employer to accept a JobApplication. This will create or update
    a corresponding Application record with STATUS_ACCEPTED and redirect back
    to the applicants page for the job.
    """

    def post(self, request, pk, *args, **kwargs):
        job_app = get_object_or_404(JobApplication, pk=pk)
        job = job_app.job

        # Only the employer who owns the job (or staff) can accept
        if job.employer != request.user and not request.user.is_staff:
            messages.error(request, 'You do not have permission to accept this applicant.')
            return redirect('job_applicants', pk=job.pk)

        # Create or update the Application record
        application_obj, created = Application.objects.get_or_create(
            job=job,
            applicant=job_app.applicant,
            defaults={
                'resume': job_app.resume.name if getattr(job_app, 'resume', None) else '',
                'cover_letter': job_app.cover_letter or '',
                'status': Application.STATUS_ACCEPTED,
            }
        )

        if not created:
            application_obj.status = Application.STATUS_ACCEPTED
            application_obj.save()

        messages.success(request, f"Accepted {job_app.full_name}'s application.")
        return redirect('job_applicants', pk=job.pk)


class EmployerDashboardView(LoginRequiredMixin, EmployerRequiredMixin, TemplateView):
    template_name = 'jobs/employer_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        jobs = self.request.user.jobs.all()
        
        # Count job applications (new system)
        total_applicants = JobApplication.objects.filter(job__in=jobs).count()
        recent_applications = JobApplication.objects.filter(job__in=jobs).order_by('-applied_at')[:5]
        
        company_profile = self.request.user.companies.first()
        active_jobs = jobs.filter(status=Job.STATUS_APPROVED)
        
        context.update({
            'jobs': jobs,
            'active_jobs': active_jobs,
            'total_applicants': total_applicants,
            'recent_applications': recent_applications,
            'company_profile': company_profile,
        })
        return context


class PendingJobsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'admin/pending_jobs.html'

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_jobs'] = Job.objects.filter(status=Job.STATUS_PENDING)
        return context


class ApproveJobView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('job_list')
        job = get_object_or_404(Job, pk=pk)
        job.status = Job.STATUS_APPROVED
        job.save()
        return redirect('pending_jobs')


class RejectJobView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('job_list')
        job = get_object_or_404(Job, pk=pk)
        job.status = Job.STATUS_REJECTED
        job.save()
        return redirect('pending_jobs')


class CompanyCreateView(LoginRequiredMixin, EmployerRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = CompanyForm()
        return render(request, 'jobs/company_form.html', {'form': form, 'creating': True})

    def post(self, request, *args, **kwargs):
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save(commit=False)
            company.employer = request.user
            company.save()
            return redirect('employer_dashboard')
        return render(request, 'jobs/company_form.html', {'form': form, 'creating': True})


class CompanyUpdateView(LoginRequiredMixin, EmployerRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        company = get_object_or_404(Company, pk=pk, employer=request.user)
        form = CompanyForm(instance=company)
        return render(request, 'jobs/company_form.html', {'form': form, 'company': company})


class CompanyProfileView(LoginRequiredMixin, EmployerRequiredMixin, View):
    """Redirect helper: if the employer has a company profile, open the edit page;
    otherwise send them to the create page. This keeps the `company_profile`
    URL stable for templates and navigation.
    """
    def get(self, request, *args, **kwargs):
        company = request.user.companies.first()
        if company:
            return redirect('company_edit', pk=company.pk)
        return redirect('company_create')

    def post(self, request, pk, *args, **kwargs):
        company = get_object_or_404(Company, pk=pk, employer=request.user)
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            # Handle logo removal if requested
            if form.cleaned_data.get('remove_logo'):
                try:
                    company.logo.delete(save=False)
                except Exception:
                    pass
                company.logo = None
            
            form.save()
            return redirect('employer_dashboard')
        return render(request, 'jobs/company_form.html', {'form': form, 'company': company})
