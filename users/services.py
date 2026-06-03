from rest_framework_simplejwt.tokens import RefreshToken


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
