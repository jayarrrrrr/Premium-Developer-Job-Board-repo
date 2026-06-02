from rest_framework import serializers
from .models import JobPosting, Job


class JobPostingSerializer(serializers.ModelSerializer):
    salary_range = serializers.SerializerMethodField()
    application_link = serializers.SerializerMethodField()
    debug_info = serializers.SerializerMethodField()

    class Meta:
        model = JobPosting
        fields = [
            'id',
            'title',
            'company',
            'location',
            'summary',
            'salary_range',
            'application_link',
            'posted_at',
            'debug_info',
        ]

    def get_salary_range(self, obj):
        request = self.context.get('request')
        if request and getattr(request.user, 'is_authenticated', False):
            request.user.get_or_create_profile()
            if request.user.profile.role == 'EMPLOYER' or request.user.profile.is_premium:
                return obj.salary_range
        return 'Premium members only. Upgrade to view salary details.'

    def get_application_link(self, obj):
        return getattr(obj, 'application_link', '#')

    def get_debug_info(self, obj):
        return {}


class JobSerializer(serializers.ModelSerializer):
    """Serializer for the new internal Job model."""
    company = serializers.CharField(source='company.company_name', read_only=True)
    logo = serializers.SerializerMethodField()
    salary_range = serializers.SerializerMethodField()
    summary = serializers.CharField(source='description', read_only=True)
    application_link = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id',
            'title',
            'company',
            'location',
            'summary',
            'salary_range',
            'application_link',
            'employment_type',
            'skills_required',
            'created_at',
            'logo',
        ]

    def get_logo(self, obj):
        """Get company logo URL if available."""
        try:
            if obj.company and obj.company.logo:
                return obj.company.logo.url
        except Exception:
            pass
        return None

    def get_salary_range(self, obj):
        """Show salary to premium users and employers only."""
        request = self.context.get('request')
        if request and getattr(request.user, 'is_authenticated', False):
            profile = request.user.get_or_create_profile()
            if profile.role == 'EMPLOYER' or profile.is_premium:
                return obj.salary
        return 'Premium members only. Upgrade to view salary details.'

    def get_application_link(self, obj):
        """Return the apply URL for the job."""
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/jobs/job/{obj.id}/apply/')
        return f'/jobs/job/{obj.id}/apply/'

    def get_application_link(self, obj):
        request = self.context.get('request')
        if request and getattr(request.user, 'is_authenticated', False):
            request.user.get_or_create_profile()
            if request.user.profile.role == 'EMPLOYER' or request.user.profile.is_premium:
                return obj.application_link
        return 'Premium members only. Upgrade to access application details.'

    def get_debug_info(self, obj):
        request = self.context.get('request')
        if not request or not getattr(request.user, 'is_authenticated', False):
            return None
        profile = request.user.get_or_create_profile()
        return {
            'username': request.user.username,
            'role': profile.role,
            'is_premium': bool(profile.is_premium),
        }


# API serializers for Job and Application models
from .models import Job, Application


class JobSerializer(serializers.ModelSerializer):
    salary = serializers.SerializerMethodField()
    application_url = serializers.SerializerMethodField()
    debug_info = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ['id', 'title', 'company', 'location', 'description', 'salary', 'employment_type', 'skills_required', 'application_url', 'status', 'created_at', 'debug_info']

    def get_salary(self, obj):
        request = self.context.get('request')
        if request and getattr(request.user, 'is_authenticated', False):
            user = request.user
            if getattr(user, 'is_staff', False):
                return obj.salary
            try:
                if obj.employer_id and user.id == obj.employer_id:
                    return obj.salary
            except Exception:
                pass
            user.get_or_create_profile()
            if user.profile.role == 'EMPLOYER' or user.profile.is_premium:
                return obj.salary
        return 'Premium Required'

    def get_application_url(self, obj):
        request = self.context.get('request')
        if request and getattr(request.user, 'is_authenticated', False):
            user = request.user
            if getattr(user, 'is_staff', False):
                return obj.application_url
            try:
                if obj.employer_id and user.id == obj.employer_id:
                    return obj.application_url
            except Exception:
                pass
            user.get_or_create_profile()
            if user.profile.role == 'EMPLOYER' or user.profile.is_premium:
                return obj.application_url
        return 'Premium Required'

    def get_debug_info(self, obj):
        request = self.context.get('request')
        if not request or not getattr(request.user, 'is_authenticated', False):
            return None
        profile = request.user.get_or_create_profile()
        return {
            'username': request.user.username,
            'role': profile.role,
            'is_premium': bool(profile.is_premium),
        }


class ApplicationSerializer(serializers.ModelSerializer):
    applicant = serializers.StringRelatedField(read_only=True)
    job = JobSerializer(read_only=True)

    class Meta:
        model = Application
        fields = ['id', 'applicant', 'job', 'resume', 'cover_letter', 'status', 'applied_at']
