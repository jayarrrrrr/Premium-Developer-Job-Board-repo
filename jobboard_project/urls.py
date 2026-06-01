from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from jobs.views import JobPostingViewSet
from users.views import LoginView, LogoutView, SignupView, SignupAPIView, PremiumTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from jobs.api import JobViewSet, ApplicationViewSet
from users.api import UserProfileAPIView, DeveloperDashboardAPIView, EmployerDashboardAPIView, DebugPremiumAPIView
try:
    from rest_framework.schemas import get_schema_view
    from rest_framework.documentation import include_docs_urls
    _HAS_REST_DOCS = True
except Exception:
    # If djangorestframework isn't installed in the environment, avoid import-time crash.
    _HAS_REST_DOCS = False
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'jobs', JobPostingViewSet, basename='jobposting')
router.register(r'v2/jobs', JobViewSet, basename='api-jobs')
router.register(r'v2/applications', ApplicationViewSet, basename='api-applications')

urlpatterns = [
    path('', RedirectView.as_view(url='/jobs/', permanent=False)),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/signup/', SignupAPIView.as_view(), name='api-signup'),
    path('api/token/', PremiumTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]

# Optionally include DRF schema/docs if available
if _HAS_REST_DOCS:
    urlpatterns += [
        path('api/openapi/', get_schema_view(title='Job Board API', description='API for Premium Developer Job Board', version='1.0.0'), name='openapi-schema'),
        path('api/docs/', include_docs_urls(title='Job Board API Documentation')),
    ]

# user APIs and standard routes
urlpatterns += [
    path('api/v2/profile/', UserProfileAPIView.as_view(), name='api-profile'),
    path('api/v2/dashboard/developer/', DeveloperDashboardAPIView.as_view(), name='api-developer-dashboard'),
    path('api/v2/dashboard/employer/', EmployerDashboardAPIView.as_view(), name='api-employer-dashboard'),
    path('api/debug/premium/', UserProfileAPIView.as_view(), name='api-debug-profile'),
    path('api/debug/premium-flags/', DebugPremiumAPIView.as_view(), name='api-debug-premium-flags'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('jobs/', include('jobs.urls')),
    path('', include('users.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
