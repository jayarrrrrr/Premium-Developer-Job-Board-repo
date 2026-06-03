from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


class AuthService:
    @staticmethod
    def get_access_token(user):
        refresh = RefreshToken.for_user(user)
        profile = user.get_or_create_profile()
        refresh['user_id'] = user.id
        refresh['role'] = profile.role
        refresh['is_premium'] = bool(profile.is_premium)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class SecurityService:
    HONEYPOT_FIELD = 'extra_info'

    @classmethod
    def is_bot_submission(cls, data):
        return bool(data.get(cls.HONEYPOT_FIELD))

    @classmethod
    def get_honeypot_field_name(cls):
        return cls.HONEYPOT_FIELD


class EmailService:
    """Service for sending emails to users."""

    @staticmethod
    def send_welcome_email(user):
        """Send welcome email to newly registered user."""
        try:
            subject = 'Welcome to Job Board! 🎉'
            context = {
                'user': user,
                'username': user.username,
                'email': user.email,
            }
            
            # Try to render HTML email, fallback to plain text
            try:
                html_message = render_to_string('emails/welcome.html', context)
            except:
                html_message = None

            plain_message = f"""
Hello {user.first_name or user.username},

Welcome to Job Board! Your account has been successfully created.

Your account details:
- Username: {user.username}
- Email: {user.email}

You can now log in and start exploring premium job opportunities or posting positions.

Visit: https://yourjobboard.com/login/

If you have any questions, feel free to contact our support team.

Best regards,
Job Board Team
"""

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Error sending welcome email: {str(e)}")
            return False

    @staticmethod
    def send_password_reset_email(user, code):
        """Send password reset email with verification code."""
        try:
            subject = 'Password Reset Request - Job Board'
            context = {
                'user': user,
                'code': code,
                'timeout_minutes': getattr(settings, 'PASSWORD_RESET_TIMEOUT', 3600) // 60,
            }
            
            # Try to render HTML email, fallback to plain text
            try:
                html_message = render_to_string('emails/password_reset.html', context)
            except:
                html_message = None

            plain_message = f"""
Hello {user.first_name or user.username},

You requested to reset your password. Use the following code to proceed:

CODE: {code}

This code will expire in {context['timeout_minutes']} minutes.

If you didn't request this, please ignore this email.

Best regards,
Job Board Team
"""

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Error sending password reset email: {str(e)}")
            return False
