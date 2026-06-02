from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .models import JobPosting
from .serializers import JobPostingSerializer
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
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer
    pagination_class = JobPostingPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.query_params.get('search')
        location = self.request.query_params.get('location')
        filters = SearchService.build_filters(search_term, location)
        return queryset.filter(filters)


# Django web views for multi-role app
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Job, Company, Application, SavedJob
from .forms import JobForm, CompanyForm, ApplicationForm
from django.urls import reverse


class JobListView(TemplateView):
    template_name = 'jobs/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['jobs'] = Job.objects.filter(status=Job.STATUS_APPROVED)
        return context


class JobDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        job = get_object_or_404(Job, pk=pk, status__in=[Job.STATUS_APPROVED, Job.STATUS_PENDING])
        can_view_salary = False
        if request.user.is_authenticated:
            user = request.user
            profile = user.get_or_create_profile()
            if getattr(user, 'is_staff', False):
                can_view_salary = True
            elif profile.role == 'EMPLOYER':
                can_view_salary = True
            else:
                try:
                    if job.employer_id and user.id == job.employer_id:
                        can_view_salary = True
                except Exception:
                    pass
                if profile.is_premium:
                    can_view_salary = True
        can_apply_link = can_view_salary
        return render(request, 'jobs/detail.html', {
            'job': job,
            'can_view_salary': can_view_salary,
            'can_apply_link': can_apply_link,
            'application_form': ApplicationForm(),
        })

    def post(self, request, pk, *args, **kwargs):
        # submit application
        if not request.user.is_authenticated:
            return redirect('login')
        job = get_object_or_404(Job, pk=pk, status=Job.STATUS_APPROVED)
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.applicant = request.user
            application.job = job
            application.save()
            return redirect('application_history')
        return render(request, 'jobs/detail.html', {'job': job, 'application_form': form})


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
            if not job.company and company_name:
                company = Company.objects.create(employer=request.user, company_name=company_name)
                job.company = company

            job.employer = request.user
            # default to pending for admin approval
            job.status = Job.STATUS_PENDING
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
            if not form.instance.company and company_name:
                company = Company.objects.create(employer=request.user, company_name=company_name)
                form.instance.company = company
            form.save()
            return redirect('employer_dashboard')
        return render(request, 'jobs/form.html', {'form': form, 'job': job})


class JobDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        job = get_object_or_404(Job, pk=pk)
        if job.employer != request.user and not request.user.is_staff:
            return redirect('job_list')
        job.delete()
        return redirect('employer_dashboard')


class ApplyJobView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        job = get_object_or_404(Job, pk=pk, status=Job.STATUS_APPROVED)
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.applicant = request.user
            application.job = job
            application.save()
        return redirect('application_history')


class SaveJobView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        job = get_object_or_404(Job, pk=pk, status=Job.STATUS_APPROVED)
        SavedJob.objects.get_or_create(user=request.user, job=job)
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
        if job.employer != request.user and not request.user.is_staff:
            return redirect('job_list')
        applicants = job.applications.all()
        return render(request, self.template_name, {'job': job, 'applicants': applicants})


class EmployerDashboardView(LoginRequiredMixin, EmployerRequiredMixin, TemplateView):
    template_name = 'jobs/employer_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        jobs = self.request.user.jobs.all()
        total_applicants = Application.objects.filter(job__in=jobs).count()
        recent_applications = Application.objects.filter(job__in=jobs).order_by('-applied_at')[:5]
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
