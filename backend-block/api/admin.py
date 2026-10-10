from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Certificate, VerificationAttempt, FailedVerificationLog


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'user_type', 'organization_name', 'is_active', 'created_at']
    list_filter = ['user_type', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'organization_name']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'organization_name', 'contact_email')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'organization_name', 'contact_email')
        }),
    )


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'student_name', 'course_name', 'institution_name', 
                    'uploaded_by', 'ocr_processed', 'created_at']
    list_filter = ['file_type', 'ocr_processed', 'metadata_extracted', 'created_at']
    search_fields = ['file_name', 'student_name', 'course_name', 'institution_name', 'file_hash']
    readonly_fields = ['file_hash', 'file_name']


@admin.register(VerificationAttempt)
class VerificationAttemptAdmin(admin.ModelAdmin):
    list_display = ['candidate_name', 'company', 'status', 'name_match', 
                    'course_match', 'institution_match', 'created_at']
    list_filter = ['status', 'name_match', 'course_match', 'institution_match', 'created_at']
    search_fields = ['candidate_name', 'candidate_email', 'expected_course', 'expected_institution']
    readonly_fields = ['file_hash']


@admin.register(FailedVerificationLog)
class FailedVerificationLogAdmin(admin.ModelAdmin):
    list_display = ['college', 'verification_attempt', 'created_at']
    list_filter = ['created_at']
    search_fields = ['reason', 'verification_attempt__candidate_name']
