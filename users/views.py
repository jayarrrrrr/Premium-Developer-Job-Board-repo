from datetime import timedelta

from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.urls import reverse
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .serializers import SignupSerializer
from .services import SecurityService, EmailService
from .forms import ProfileForm, ForgotPasswordForm, ResetPasswordForm
from .models import PasswordResetToken, User
from django.shortcuts import get_object_or_404

from users.jobs.models import Job, Application, SavedJob


class PremiumTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        profile = user.get_or_create_profile()
        token['user_id'] = user.id
        token['role'] = profile.role
        token['is_premium'] = bool(profile.is_premium)
        return token


class PremiumTokenObtainPairView(TokenObtainPairView):
    serializer_class = PremiumTokenObtainPairSerializer


class SignupAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'Signup successful', 'user': {'username': user.username, 'email': user.email}}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignupView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'users/signup.html', {'honeypot_name': SecurityService.get_honeypot_field_name()})

    def post(self, request, *args, **kwargs):
        if SecurityService.is_bot_submission(request.POST):
            return HttpResponseBadRequest('Bot submission detected.')
        serializer = SignupSerializer(data=request.POST)
        if serializer.is_valid():
            user = serializer.save()
            # redirect based on role
            role = user.get_or_create_profile().role
            if user.is_staff or role == 'ADMIN':
                return HttpResponseRedirect(reverse('pending_jobs'))
            return HttpResponseRedirect(reverse('dashboard'))
        return render(request, 'users/signup.html', {
            'errors': serializer.errors,
            'honeypot_name': SecurityService.get_honeypot_field_name(),
        })


class LoginView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'users/login.html')

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('dashboard'))
        return render(request, 'users/login.html', {'error': 'Invalid username or password.'})


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse('login'))

    def post(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse('login'))


class DashboardView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            return redirect('pending_jobs')
        profile = request.user.get_or_create_profile()
        if profile.role == 'EMPLOYER':
            return redirect('employer_dashboard')
        return redirect('developer_dashboard')


class DeveloperDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'users/developer_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile = user.get_or_create_profile()
        saved_jobs = SavedJob.objects.filter(user=user)
        applications = Application.objects.filter(applicant=user).order_by('-applied_at')
        recommended_jobs = Job.objects.filter(status=Job.STATUS_APPROVED)
        if user.is_authenticated:
            recommended_jobs = recommended_jobs.exclude(saved_jobs__user=user).exclude(applications__applicant=user)
        context.update({
            'user_profile': user,
            'profile_completion': self._get_profile_completion(user),
            'saved_count': saved_jobs.count(),
            'applied_count': applications.count(),
            'applications': applications[:5],
            'recommended_jobs': recommended_jobs[:4],
            'is_premium': bool(profile.is_premium),
        })
        return context

    def _get_profile_completion(self, user):
        score = 40
        if user.email:
            score += 20
        if user.first_name:
            score += 15
        if user.last_name:
            score += 15
        return min(score, 100)


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_profile'] = self.request.user
        # expose profile object for templates
        context['profile'] = self.request.user.get_or_create_profile()
        return context


class ProfileEditView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        profile = request.user.get_or_create_profile()
        form = ProfileForm(instance=profile)
        return render(request, 'users/profile_edit.html', {'form': form, 'profile': profile})

    def post(self, request, *args, **kwargs):
        profile = request.user.get_or_create_profile()
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # handle remove picture
            if form.cleaned_data.get('remove_profile_picture'):
                try:
                    profile.profile_picture.delete(save=False)
                except Exception:
                    pass
                profile.profile_picture = None

            try:
                form.save()
                return redirect('profile')
            except Exception as exc:
                form.add_error(None, 'Unable to save profile. Please try again later.')
                if hasattr(exc, 'args') and exc.args:
                    form.add_error(None, exc.args[0])

        return render(request, 'users/profile_edit.html', {'form': form, 'profile': profile})


class UpgradeView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        profile = request.user.get_or_create_profile()
        if profile.is_premium:
            return HttpResponseRedirect(reverse('dashboard'))
        return render(request, 'users/upgrade.html')


class PaymentView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        profile = request.user.get_or_create_profile()
        if profile.is_premium:
            return HttpResponseRedirect(reverse('dashboard'))
        return render(request, 'users/payment.html')

    def post(self, request, *args, **kwargs):
        user = request.user
        user.is_premium = True
        user.premium_activated_at = timezone.now()
        user.premium_expires_at = timezone.now() + timedelta(days=30)
        user.save()
        profile = user.get_or_create_profile()
        profile.is_premium = True
        profile.save()
        return HttpResponseRedirect(reverse('payment_confirmation'))


class PaymentConfirmationView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        profile = request.user.get_or_create_profile()
        if not profile.is_premium:
            return HttpResponseRedirect(reverse('upgrade'))
        return render(request, 'users/payment_confirmation.html')


class ForgotPasswordView(View):
    """View for requesting a password reset via email."""

    def get(self, request, *args, **kwargs):
        form = ForgotPasswordForm()
        return render(request, 'users/forgot_password.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                # Create password reset token
                token = PasswordResetToken.create_for_user(user)
                # Send email with verification code
                if EmailService.send_password_reset_email(user, token.code):
                    return render(request, 'users/forgot_password_sent.html', {'email': email})
                else:
                    form.add_error(None, 'Failed to send email. Please try again later.')
            except User.DoesNotExist:
                # Don't reveal if email exists (security)
                return render(request, 'users/forgot_password_sent.html', {'email': email})

        return render(request, 'users/forgot_password.html', {'form': form})


class ResetPasswordView(View):
    """View for resetting password with verification code."""

    def get(self, request, *args, **kwargs):
        form = ResetPasswordForm()
        context = {'form': form}
        return render(request, 'users/reset_password.html', context)

    def post(self, request, *args, **kwargs):
        form = ResetPasswordForm(request.POST)
        context = {'form': form}

        if form.is_valid():
            code = form.cleaned_data['code'].strip()
            new_password = form.cleaned_data['new_password']

            try:
                token = PasswordResetToken.objects.get(code=code)

                # Check if token is expired
                if token.is_expired():
                    form.add_error('code', 'Verification code has expired. Please request a new one.')
                    return render(request, 'users/reset_password.html', context)

                # Check if token is already used
                if token.is_used:
                    form.add_error('code', 'Verification code has already been used.')
                    return render(request, 'users/reset_password.html', context)

                # Update user password
                user = token.user
                user.set_password(new_password)
                user.save()

                # Mark token as used
                token.mark_as_used()

                # Redirect to success page
                return render(request, 'users/reset_password_success.html', {
                    'username': user.username
                })

            except PasswordResetToken.DoesNotExist:
                form.add_error('code', 'Invalid verification code.')
                return render(request, 'users/reset_password.html', context)

        return render(request, 'users/reset_password.html', context)
