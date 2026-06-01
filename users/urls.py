from django.urls import path
from .views import DashboardView, DeveloperDashboardView, ProfileView, UpgradeView, PaymentView, PaymentConfirmationView
from .views import ProfileEditView

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('developer/dashboard/', DeveloperDashboardView.as_view(), name='developer_dashboard'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('upgrade/', UpgradeView.as_view(), name='upgrade'),
    path('payment/', PaymentView.as_view(), name='payment'),
    path('payment/confirmation/', PaymentConfirmationView.as_view(), name='payment_confirmation'),
]
