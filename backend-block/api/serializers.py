from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, Certificate, VerificationAttempt, FailedVerificationLog


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password_confirm', 'user_type', 
                 'organization_name', 'contact_email', 'first_name', 'last_name']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            data['user'] = user
        else:
            raise serializers.ValidationError('Must include username and password')
        
        return data


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ['id', 'file_path', 'file_name', 'file_hash', 'file_type',
                 'student_name', 'course_name', 'institution_name', 'issue_date',
                 'grade_score', 'ocr_processed', 'ocr_output', 'metadata_extracted',
                 'iota_message_id', 'iota_block_id', 'iota_transaction_id', 
                 'iota_stored', 'iota_timestamp', 'created_at', 'updated_at']
        read_only_fields = ['id', 'file_hash', 'file_name', 'ocr_processed', 
                           'ocr_output', 'metadata_extracted', 'iota_message_id',
                           'iota_block_id', 'iota_transaction_id', 'iota_stored',
                           'iota_timestamp', 'created_at', 'updated_at']


class CertificateUploadSerializer(serializers.ModelSerializer):
    files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True
    )
    
    class Meta:
        model = Certificate
        fields = ['files', 'student_name', 'course_name', 'institution_name', 
                 'issue_date', 'grade_score']


class VerificationAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationAttempt
        fields = ['id', 'candidate_name', 'candidate_email', 'expected_course',
                 'expected_institution', 'uploaded_file', 'file_hash', 'status',
                 'verification_notes', 'ocr_output', 'ocr_implemented',
                 'name_match', 'course_match', 'institution_match',
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'file_hash', 'status', 'verification_notes',
                           'ocr_output', 'ocr_implemented', 'name_match',
                           'course_match', 'institution_match', 'created_at', 'updated_at']


class FailedVerificationLogSerializer(serializers.ModelSerializer):
    verification_attempt = VerificationAttemptSerializer(read_only=True)
    
    class Meta:
        model = FailedVerificationLog
        fields = ['id', 'verification_attempt', 'reason', 'created_at']


class FileHashCheckSerializer(serializers.Serializer):
    file_hash = serializers.CharField(max_length=64)


class FileHashResponseSerializer(serializers.Serializer):
    exists = serializers.BooleanField()
    certificate = CertificateSerializer(required=False)
    message = serializers.CharField()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'user_type', 'organization_name', 'contact_email', 'date_joined']
        read_only_fields = ['id', 'username', 'user_type', 'date_joined']
