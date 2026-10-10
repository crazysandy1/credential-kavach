from django.db import models
from django.contrib.auth.models import AbstractUser
import hashlib
import os


class CustomUser(AbstractUser):
    USER_TYPES = (
        ('college', 'College'),
        ('company', 'Company'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    organization_name = models.CharField(max_length=255)
    contact_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.username} ({self.user_type})"


class Certificate(models.Model):
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='certificates')
    file_path = models.FileField(upload_to='certificates/')
    file_name = models.CharField(max_length=255)
    file_hash = models.CharField(max_length=64, unique=True)  # SHA256 hash
    file_type = models.CharField(max_length=10)  # pdf, jpg, png, etc.
    
    # Certificate metadata
    student_name = models.CharField(max_length=255, blank=True)
    course_name = models.CharField(max_length=255, blank=True)
    institution_name = models.CharField(max_length=255, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    grade_score = models.CharField(max_length=50, blank=True)
    
    # OCR and processing flags
    ocr_processed = models.BooleanField(default=False)
    ocr_output = models.TextField(blank=True)
    metadata_extracted = models.BooleanField(default=False)
    
    # IOTA blockchain fields
    iota_message_id = models.CharField(max_length=255, blank=True, null=True)
    iota_block_id = models.CharField(max_length=255, blank=True, null=True)
    iota_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    iota_stored = models.BooleanField(default=False)
    iota_timestamp = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if self.file_path and not self.file_hash:
            # Generate SHA256 hash of the file
            hasher = hashlib.sha256()
            for chunk in self.file_path.chunks():
                hasher.update(chunk)
            self.file_hash = hasher.hexdigest()
            
        if not self.file_name and self.file_path:
            self.file_name = os.path.basename(self.file_path.name)
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.file_name} - {self.student_name}"


class VerificationAttempt(models.Model):
    VERIFICATION_STATUS = (
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('failed', 'Failed'),
        ('ocr_pending', 'OCR Pending'),
    )
    
    company = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='verification_attempts')
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, null=True, blank=True)
    
    # Candidate information provided by company
    candidate_name = models.CharField(max_length=255)
    candidate_email = models.EmailField(blank=True)
    expected_course = models.CharField(max_length=255, blank=True)
    expected_institution = models.CharField(max_length=255, blank=True)
    
    # Uploaded file for verification
    uploaded_file = models.FileField(upload_to='verification_attempts/')
    file_hash = models.CharField(max_length=64)
    
    # Verification results
    status = models.CharField(max_length=15, choices=VERIFICATION_STATUS, default='pending')
    verification_notes = models.TextField(blank=True)
    ocr_output = models.TextField(blank=True)
    ocr_implemented = models.BooleanField(default=False)
    
    # Metadata matching results
    name_match = models.BooleanField(default=False)
    course_match = models.BooleanField(default=False)
    institution_match = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if self.uploaded_file and not self.file_hash:
            # Generate SHA256 hash of the file
            hasher = hashlib.sha256()
            for chunk in self.uploaded_file.chunks():
                hasher.update(chunk)
            self.file_hash = hasher.hexdigest()
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Verification: {self.candidate_name} by {self.company.username}"


class FailedVerificationLog(models.Model):
    college = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='failed_verifications')
    verification_attempt = models.ForeignKey(VerificationAttempt, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Failed verification for {self.verification_attempt.candidate_name}"
