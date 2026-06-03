from rest_framework import serializers
from .models import User, Profile
from .services import EmailService


class SignupSerializer(serializers.ModelSerializer):
    honeypot = serializers.CharField(write_only=True, required=False, allow_blank=True)
    role = serializers.ChoiceField(write_only=True, required=False, choices=[('EMPLOYER', 'Employer'), ('JOB_SEEKER', 'Job Seeker')])

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'honeypot']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'username': {'required': True},
        }

    def validate(self, attrs):
        honeypot = attrs.get('honeypot')
        if honeypot:
            raise serializers.ValidationError('Honeypot field must be empty.')
        return attrs

    def create(self, validated_data):
        role = validated_data.pop('role', None)
        validated_data.pop('honeypot', None)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        # assign role if provided
        profile, created = Profile.objects.get_or_create(user=user)
        if role == 'EMPLOYER':
            profile.role = 'EMPLOYER'
        else:
            profile.role = 'JOB_SEEKER'
        profile.save()
        
        # Send welcome email
        try:
            EmailService.send_welcome_email(user)
        except Exception as e:
            print(f"Welcome email not sent: {str(e)}")
        
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['role', 'bio', 'location', 'website', 'phone', 'is_premium']


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    is_premium = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_premium']

    def get_role(self, obj):
        try:
            return obj.get_role()
        except Exception:
            return 'developer'

    def get_is_premium(self, obj):
        try:
            return bool(obj.get_or_create_profile().is_premium)
        except Exception:
            return False
