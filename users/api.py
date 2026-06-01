from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .serializers import UserSerializer, ProfileSerializer
from users.jobs.models import Job, Application, SavedJob
from .permissions import IsDeveloper, IsEmployer, IsPremiumUser


class UserProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        profile = request.user.get_or_create_profile()
        profile_data = ProfileSerializer(profile).data
        data = serializer.data
        data.update({'profile': profile_data})
        return Response(data)


class DeveloperDashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsDeveloper]

    def get(self, request):
        user = request.user
        saved_count = SavedJob.objects.filter(user=user).count()
        applications = Application.objects.filter(applicant=user).count()
        recommended = Job.objects.filter(status=Job.STATUS_APPROVED).count()
        return Response({'saved_count': saved_count, 'applications': applications, 'recommended_jobs': recommended})


class EmployerDashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsEmployer]

    def get(self, request):
        user = request.user
        jobs = Job.objects.filter(employer=user)
        total_jobs = jobs.count()
        total_applicants = Application.objects.filter(job__in=jobs).count()
        return Response({'total_jobs': total_jobs, 'total_applicants': total_applicants})


class DebugPremiumAPIView(APIView):
    """Return current user premium flags for debugging."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        user = request.user
        data = {'is_authenticated': bool(user and user.is_authenticated)}
        if user and user.is_authenticated:
            profile = user.get_or_create_profile()
            data.update({
                'username': user.username,
                'role': profile.role,
                'is_premium': bool(profile.is_premium),
                'user_is_premium': getattr(user, 'is_premium', False),
                'profile_is_premium': getattr(profile, 'is_premium', False),
            })
            data['effective_is_premium'] = bool(data.get('profile_is_premium'))
        return Response(data)
