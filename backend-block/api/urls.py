from django.urls import path
from . import views

urlpatterns = [
    # General endpoints
    path('health/', views.health_check, name='health_check'),
    path('info/', views.api_info, name='api_info'),
    
    # Authentication endpoints
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('auth/logout/', views.logout, name='logout'),
    path('auth/profile/', views.user_profile, name='user_profile'),
    path('auth/profile/update/', views.update_profile, name='update_profile'),
    
    # Certificate endpoints
    path('certificates/check-hash/', views.check_file_hash, name='check_file_hash'),
    path('certificates/upload/', views.upload_certificate, name='upload_certificate'),
    path('certificates/', views.list_certificates, name='list_certificates'),
    path('certificates/<int:certificate_id>/', views.certificate_detail, name='certificate_detail'),
    path('certificates/<int:certificate_id>/delete/', views.delete_certificate, name='delete_certificate'),
    path('certificates/<int:certificate_id>/verify-iota/', views.verify_certificate_iota, name='verify_certificate_iota'),
    
    # Verification endpoints
    path('verification/verify/', views.verify_certificate, name='verify_certificate'),
    path('verification/attempts/', views.list_verification_attempts, name='list_verification_attempts'),
    path('verification/failed-attempts/', views.failed_verification_attempts, name='failed_verification_attempts'),
    
    # Dashboard
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
]
