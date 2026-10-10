from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiParameter
import hashlib
import os
from django.core.files.storage import default_storage
from django.conf import settings
from django.core.paginator import Paginator

from .models import CustomUser, Certificate, VerificationAttempt, FailedVerificationLog
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, CertificateSerializer,
    CertificateUploadSerializer, VerificationAttemptSerializer,
    FailedVerificationLogSerializer, FileHashCheckSerializer,
    FileHashResponseSerializer
)
from .iota_service import IOTAService

# Health check endpoint
@extend_schema(
    operation_id='health_check',
    summary='Health Check',
    description='Simple health check endpoint',
    responses={200: {'description': 'API is healthy'}}
)
@api_view(['GET'])
def health_check(request):
    """
    Simple health check endpoint
    """
    return Response({
        'status': 'healthy',
        'message': 'SIH Backend is running successfully!'
    }, status=status.HTTP_200_OK)


@extend_schema(
    operation_id='api_info',
    summary='API Information',
    description='API information endpoint',
    responses={200: {'description': 'API information'}}
)
@api_view(['GET'])
def api_info(request):
    """
    API information endpoint
    """
    return Response({
        'name': 'SIH Backend API',
        'version': '1.0.0',
        'description': 'Certificate Verification System API',
        'endpoints': {
            'health': '/api/health/',
            'info': '/api/info/',
            'auth': {
                'register': '/api/auth/register/',
                'login': '/api/auth/login/',
                'logout': '/api/auth/logout/',
            },
            'certificates': {
                'hash_check': '/api/certificates/check-hash/',
                'upload': '/api/certificates/upload/',
                'verify': '/api/certificates/verify/',
                'list': '/api/certificates/',
            }
        }
    }, status=status.HTTP_200_OK)


# Authentication Views
@extend_schema(
    operation_id='register_user',
    summary='Register User',
    description='Register a new user (College or Company)',
    request=UserRegistrationSerializer,
    responses={201: {'description': 'User created successfully'}, 400: {'description': 'Bad request'}}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user (College or Company)
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'User created successfully',
            'user_id': user.id,
            'user_type': user.user_type,
            'token': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    operation_id='login_user',
    summary='User Login',
    description='Login with JWT authentication',
    request=UserLoginSerializer,
    responses={200: {'description': 'Login successful'}, 401: {'description': 'Invalid credentials'}}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login with JWT authentication
    """
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Login successful',
            'user_id': user.id,
            'user_type': user.user_type,
            'organization_name': user.organization_name,
            'token': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


@extend_schema(
    operation_id='logout_user',
    summary='User Logout',
    description='Simple logout endpoint',
    responses={200: {'description': 'Logout successful'}}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Simple logout endpoint
    """
    return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


# Certificate Views
@extend_schema(
    operation_id='check_file_hash',
    summary='Check File Hash',
    description='Check if a file with given SHA256 hash exists in the database',
    request=FileHashCheckSerializer,
    responses={200: FileHashResponseSerializer}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def check_file_hash(request):
    """
    Check if a file with given SHA256 hash exists in the database
    """
    serializer = FileHashCheckSerializer(data=request.data)
    if serializer.is_valid():
        file_hash = serializer.validated_data['file_hash']
        
        try:
            certificate = Certificate.objects.get(file_hash=file_hash)
            return Response({
                'exists': True,
                'certificate': CertificateSerializer(certificate).data,
                'message': 'Certificate found in database'
            }, status=status.HTTP_200_OK)
        except Certificate.DoesNotExist:
            return Response({
                'exists': False,
                'certificate': None,
                'message': 'Certificate not found in database'
            }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def calculate_file_hash(file):
    """Calculate SHA256 hash of a file"""
    hash_sha256 = hashlib.sha256()
    for chunk in file.chunks():
        hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def extract_text_from_file(file):
    """
    Extract text from uploaded file (PDF or image)
    This is a placeholder for OCR implementation
    """
    # Reset file pointer to beginning
    file.seek(0)
    
    file_extension = os.path.splitext(file.name)[1].lower()
    
    if file_extension == '.pdf':
        # TODO: Implement PDF text extraction using PyPDF2 or similar
        return "PDF text extraction not implemented yet"
    elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
        # TODO: Implement OCR using pytesseract or similar
        return "Image OCR not implemented yet"
    else:
        return f"Unsupported file type: {file_extension}"


@extend_schema(
    operation_id='upload_certificate',
    summary='Upload Certificate',
    description='Upload certificate files (individual or bulk) with optional metadata',
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'files': {
                    'type': 'array',
                    'items': {'type': 'string', 'format': 'binary'}
                },
                'student_name': {'type': 'string'},
                'course_name': {'type': 'string'},
                'institution_name': {'type': 'string'},
                'issue_date': {'type': 'string', 'format': 'date'},
                'grade_score': {'type': 'string'}
            }
        }
    },
    responses={201: CertificateSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_certificate(request):
    """
    Upload certificate files (individual or bulk) with optional metadata
    Only colleges can upload certificates
    """
    if request.user.user_type != 'college':
        return Response({'error': 'Only colleges can upload certificates'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    files = request.FILES.getlist('files')
    if not files:
        return Response({'error': 'No files provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Handle bulk upload
    if len(files) > 1:
        uploaded_certificates = []
        for file in files:
            try:
                # Calculate file hash
                file_hash = calculate_file_hash(file)
                
                # Extract text (placeholder for OCR)
                extracted_text = extract_text_from_file(file)
                
                # Save file
                file_path = default_storage.save(
                    f'certificates/{request.user.id}/{file.name}',
                    file
                )
                
                # Create certificate record
                certificate = Certificate.objects.create(
                    college=request.user,
                    file=file_path,
                    file_hash=file_hash,
                    original_filename=file.name,
                    extracted_text=extracted_text,
                    student_name=f"Bulk upload - {file.name}",
                    course_name="Not specified",
                    institution_name=request.user.organization_name,
                )
                
                uploaded_certificates.append(CertificateSerializer(certificate).data)
                
            except Exception as e:
                return Response({
                    'error': f'Failed to upload {file.name}: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': f'Successfully uploaded {len(uploaded_certificates)} certificates',
            'certificates': uploaded_certificates
        }, status=status.HTTP_201_CREATED)
    
    # Handle single file upload with metadata
    file = files[0]
    file_hash = calculate_file_hash(file)
    extracted_text = extract_text_from_file(file)
    
    # Save file
    file_path = default_storage.save(
        f'certificates/{request.user.id}/{file.name}',
        file
    )
    
    # Get metadata from request
    student_name = request.data.get('student_name', '')
    course_name = request.data.get('course_name', '')
    institution_name = request.data.get('institution_name', request.user.organization_name)
    
    # Create certificate record
    certificate = Certificate.objects.create(
        college=request.user,
        file=file_path,
        file_hash=file_hash,
        original_filename=file.name,
        extracted_text=extracted_text,
        student_name=student_name,
        course_name=course_name,
        institution_name=institution_name,
        issue_date=request.data.get('issue_date') or None,
        grade_score=request.data.get('grade_score', ''),
    )
    certificate.save()
    
    # Store certificate on IOTA (individual, non-bulk)
    try:
        iota_result = IOTAService.store_certificate_on_iota(certificate)
        if iota_result and iota_result.get('success'):
            certificate.iota_block_id = iota_result.get('block_id')
            certificate.iota_message_id = iota_result.get('message_id')
            certificate.iota_stored = True
            certificate.iota_timestamp = iota_result.get('timestamp')
            certificate.save()
    except Exception as e:
        # Continue even if IOTA storage fails
        print(f"IOTA storage failed: {str(e)}")
    
    return Response({
        'message': 'Certificate uploaded successfully',
        'certificate': CertificateSerializer(certificate).data
    }, status=status.HTTP_201_CREATED)


@extend_schema(
    operation_id='verify_certificate',
    summary='Verify Certificate',
    description='Verify a certificate by uploading a file',
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'file': {'type': 'string', 'format': 'binary'},
                'student_name': {'type': 'string'},
                'course_name': {'type': 'string'}
            }
        }
    },
    responses={200: VerificationAttemptSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def verify_certificate(request):
    """
    Verify a certificate by uploading a file
    Both companies and colleges can verify certificates
    """
    file = request.FILES.get('file')
    if not file:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Calculate file hash
    file_hash = calculate_file_hash(file)
    
    # Check if certificate exists
    try:
        certificate = Certificate.objects.get(file_hash=file_hash)
        
        # Create verification attempt record
        verification_attempt = VerificationAttempt.objects.create(
            certificate=certificate,
            verifier=request.user,
            company=request.user if request.user.user_type == 'company' else None,
            college=request.user if request.user.user_type == 'college' else None,
            verification_status='verified',
            verification_method='file_hash'
        )
        
        # Verify certificate against IOTA if stored
        iota_verification = None
        if certificate.iota_stored and certificate.iota_block_id:
            iota_verification = IOTAService.verify_certificate_on_iota(certificate)
        
        return Response({
            'verification_id': verification_attempt.id,
            'status': 'verified',
            'message': 'Certificate found and verified',
            'certificate_details': CertificateSerializer(certificate).data,
            'metadata_match': {
                'student_name': request.data.get('student_name', '') == certificate.student_name,
                'course_name': request.data.get('course_name', '') == certificate.course_name,
            },
            'iota_verification': iota_verification
        }, status=status.HTTP_200_OK)
        
    except Certificate.DoesNotExist:
        # Create failed verification attempt
        failed_log = FailedVerificationLog.objects.create(
            verifier=request.user,
            company=request.user if request.user.user_type == 'company' else None,
            college=None,  # Will be set when we can identify the issuing college
            file_hash=file_hash,
            reason='certificate_not_found',
            additional_data={
                'original_filename': file.name,
                'student_name': request.data.get('student_name', ''),
                'course_name': request.data.get('course_name', ''),
            }
        )
        
        return Response({
            'verification_id': None,
            'status': 'failed',
            'message': 'Certificate not found in database',
            'failed_log_id': failed_log.id,
            'reason': 'certificate_not_found'
        }, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    operation_id='failed_verification_attempts',
    summary='Failed Verification Attempts',
    description='Get failed verification attempts for a college',
    responses={200: FailedVerificationLogSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def failed_verification_attempts(request):
    """
    Get failed verification attempts for a college
    """
    if request.user.user_type != 'college':
        return Response({'error': 'Only colleges can view failed verification attempts'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    failed_attempts = FailedVerificationLog.objects.filter(
        college=request.user
    ).order_by('-created_at')
    
    serializer = FailedVerificationLogSerializer(failed_attempts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    operation_id='get_user_profile',
    summary='Get User Profile',
    description='Get current user profile information',
    responses={200: {'description': 'User profile information'}}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    Get current user profile information
    """
    return Response({
        'id': request.user.id,
        'email': request.user.email,
        'organization_name': request.user.organization_name,
        'user_type': request.user.user_type,
        'date_joined': request.user.date_joined
    }, status=status.HTTP_200_OK)


@extend_schema(
    operation_id='update_user_profile',
    summary='Update User Profile',
    description='Update user profile information',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'organization_name': {'type': 'string'},
                'email': {'type': 'string', 'format': 'email'}
            }
        }
    },
    responses={200: {'description': 'Profile updated successfully'}}
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """
    Update user profile information
    """
    user = request.user
    
    # Update allowed fields
    if 'organization_name' in request.data:
        user.organization_name = request.data['organization_name']
    if 'email' in request.data:
        user.email = request.data['email']
    
    user.save()
    
    return Response({
        'message': 'Profile updated successfully',
        'user': {
            'id': user.id,
            'email': user.email,
            'organization_name': user.organization_name,
            'user_type': user.user_type,
        }
    }, status=status.HTTP_200_OK)


@extend_schema(
    operation_id='list_certificates',
    summary='List Certificates',
    description='List certificates with pagination and search',
    parameters=[
        OpenApiParameter('page', int, description="Page number"),
        OpenApiParameter('limit', int, description="Items per page"),
        OpenApiParameter('search', str, description="Search by student name"),
    ],
    responses={200: CertificateSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_certificates(request):
    """
    List certificates with pagination and search
    Colleges see their uploaded certificates
    Companies see certificates they've verified
    """
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    search = request.GET.get('search', '')
    
    if request.user.user_type == 'college':
        queryset = Certificate.objects.filter(college=request.user)
    else:  # company
        # Get certificates that this company has verification attempts for
        queryset = Certificate.objects.filter(
            verificationattempt__company=request.user
        ).distinct()
    
    if search:
        queryset = queryset.filter(student_name__icontains=search)
    
    paginator = Paginator(queryset.order_by('-created_at'), limit)
    page_obj = paginator.get_page(page)
    
    serializer = CertificateSerializer(page_obj.object_list, many=True)
    
    return Response({
        'certificates': serializer.data,
        'pagination': {
            'current_page': page,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
    }, status=status.HTTP_200_OK)


@extend_schema(
    operation_id='list_verification_attempts',
    summary='List Verification Attempts',
    description='List verification attempts with pagination',
    parameters=[
        OpenApiParameter('page', int, description="Page number"),
        OpenApiParameter('limit', int, description="Items per page"),
    ],
    responses={200: VerificationAttemptSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_verification_attempts(request):
    """
    List verification attempts with pagination
    """
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    
    if request.user.user_type == 'college':
        # Colleges see attempts to verify their certificates
        queryset = VerificationAttempt.objects.filter(
            certificate__college=request.user
        )
    else:  # company
        # Companies see their own verification attempts
        queryset = VerificationAttempt.objects.filter(
            company=request.user
        )
    
    paginator = Paginator(queryset.order_by('-verified_at'), limit)
    page_obj = paginator.get_page(page)
    
    serializer = VerificationAttemptSerializer(page_obj.object_list, many=True)
    
    return Response({
        'verification_attempts': serializer.data,
        'pagination': {
            'current_page': page,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
    }, status=status.HTTP_200_OK)


@extend_schema(
    operation_id='company_dashboard',
    summary='Company Dashboard',
    description='Get dashboard data for companies',
    responses={200: {'description': 'Company dashboard data'}}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def company_dashboard(request):
    """
    Get dashboard data for companies
    """
    if request.user.user_type != 'company':
        return Response({'error': 'Only companies can access this endpoint'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    total_verifications = VerificationAttempt.objects.filter(company=request.user).count()
    successful_verifications = VerificationAttempt.objects.filter(
        company=request.user, 
        verification_status='verified'
    ).count()
    
    return Response({
        'total_verifications': total_verifications,
        'successful_verifications': successful_verifications,
        'failed_verifications': total_verifications - successful_verifications,
        'success_rate': (successful_verifications / total_verifications * 100) if total_verifications > 0 else 0,
    }, status=status.HTTP_200_OK)


@extend_schema(
    operation_id='college_dashboard',
    summary='College Dashboard',
    description='Get dashboard data for colleges',
    responses={200: {'description': 'College dashboard data'}}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def college_dashboard(request):
    """
    Get dashboard data for colleges
    """
    if request.user.user_type != 'college':
        return Response({'error': 'Only colleges can access this endpoint'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    total_certificates = Certificate.objects.filter(college=request.user).count()
    total_verifications = VerificationAttempt.objects.filter(
        certificate__college=request.user
    ).count()
    
    return Response({
        'total_certificates_uploaded': total_certificates,
        'total_verification_requests': total_verifications,
        'certificates_with_iota': Certificate.objects.filter(
            college=request.user, 
            iota_stored=True
        ).count(),
    }, status=status.HTTP_200_OK)


@extend_schema(
    operation_id='verify_iota_certificate',
    summary='Verify IOTA Certificate',
    description='Verify a specific certificate against IOTA blockchain',
    responses={200: {'description': 'IOTA verification result'}}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_iota_certificate(request, certificate_id):
    """
    Verify a specific certificate against IOTA blockchain
    """
    try:
        if request.user.user_type == 'college':
            certificate = Certificate.objects.get(
                id=certificate_id,
                college=request.user
            )
        else:  # company
            certificate = Certificate.objects.get(
                id=certificate_id,
                verificationattempt__company=request.user
            )
        
        iota_verification = IOTAService.verify_certificate_on_iota(certificate)
        
        return Response({
            'certificate_id': certificate.id,
            'iota_stored': certificate.iota_stored,
            'iota_block_id': certificate.iota_block_id,
            'verification_result': iota_verification
        }, status=status.HTTP_200_OK)
        
    except Certificate.DoesNotExist:
        return Response({
            'error': 'Certificate not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)
