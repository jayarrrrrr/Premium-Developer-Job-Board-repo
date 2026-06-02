from django.db.models import Count, Q
from users.jobs.models import Job, Company, Application


def effective_premium(request):
    """Expose a unified premium flag to templates: True if either User or Profile marks premium."""
    is_premium = False
    try:
        if getattr(request, 'user', None) and request.user.is_authenticated:
            profile = request.user.get_or_create_profile()
            is_premium = bool(getattr(profile, 'is_premium', False))
    except Exception:
        is_premium = False
    return {'effective_is_premium': bool(is_premium)}


def job_stats(request):
    """Calculate and provide job marketplace statistics to templates."""
    try:
        # Active Jobs: Count of approved job postings
        active_jobs = Job.objects.filter(status=Job.STATUS_APPROVED).count()
        
        # Companies Hiring: Count of unique companies with at least one approved job
        companies_hiring = Company.objects.filter(
            jobs__status=Job.STATUS_APPROVED
        ).distinct().count()
        
        # Developers Hired: Count of applications with ACCEPTED status
        developers_hired = Application.objects.filter(
            status=Application.STATUS_ACCEPTED
        ).count()
        
        return {
            'active_jobs': active_jobs,
            'companies_hiring': companies_hiring,
            'developers_hired': developers_hired,
        }
    except Exception:
        # Return zeros if there's any error
        return {
            'active_jobs': 0,
            'companies_hiring': 0,
            'developers_hired': 0,
        }
