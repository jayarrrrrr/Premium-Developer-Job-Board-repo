from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Job, Application, SavedJob
from .serializers import JobSerializer, ApplicationSerializer
from users.permissions import IsDeveloper, IsEmployer, IsPremiumUser


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated(), IsEmployer()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        # employer is set to requesting user
        serializer.save(employer=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsDeveloper])
    def apply(self, request, pk=None):
        job = self.get_object()
        # create application
        data = request.data.copy()
        data['job'] = job.id
        data['applicant'] = request.user.id
        serializer = ApplicationSerializer(data=data, context={'request': request})
        # allow minimal required fields
        if serializer.is_valid():
            Application.objects.create(applicant=request.user, job=job, resume=serializer.validated_data.get('resume',''), cover_letter=serializer.validated_data.get('cover_letter',''))
            return Response({'detail': 'Application submitted.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer

    def get_permissions(self):
        # Developers can list their own applications; Employers can view applications for their jobs
        if self.action in ('list', 'retrieve'):
            return [permissions.IsAuthenticated()]
        if self.action in ('create',):
            return [permissions.IsAuthenticated(), IsDeveloper()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.get_or_create_profile().role == 'EMPLOYER':
            # employer sees applications for their jobs
            return Application.objects.filter(job__employer=user)
        # developer sees own applications
        return Application.objects.filter(applicant=user)

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)
