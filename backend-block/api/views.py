from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiParameter
import hashlib
import os
from datetime import datetime
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


@extend_schema(
    operation_id='health_check',
    summary='Health Check',
    description='Simple health check endpoint',
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
                'check_hash': '/api/certificates/check-hash/',
                'upload': '/api/certificates/upload/',
            },
            'verification': {
                'verify': '/api/verification/verify/',
                'failed_attempts': '/api/verification/failed-attempts/',
            }
        }
    }, status=status.HTTP_200_OK)


# Authentication Views
@extend_schema(
    operation_id='register_user',
    summary='Register User',
    description='Register a new user (College or Company)',
    request=UserRegistrationSerializer,
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
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'user_type': user.user_type,
                'organization_name': user.organization_name,
            },
            'token': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    operation_id='login_user',
    summary='User Login',
    description='Login with JWT authentication',
    request=UserLoginSerializer,
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
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'user_type': user.user_type,
                'organization_name': user.organization_name,
            },
            'token': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


@extend_schema(
    operation_id='logout_user',
    summary='User Logout',
    description='Simple logout endpoint',
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
    hasher = hashlib.sha256()
    for chunk in file.chunks():
        hasher.update(chunk)
    return hasher.hexdigest()


@extend_schema(
    operation_id='upload_certificate',
    summary='Upload Certificate',
    description='Upload a single certificate (PDF/Image) - Only for colleges',
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'file': {
                    'type': 'string',
                    'format': 'binary',
                    'description': 'Certificate file (PDF/Image)'
                },
                'student_name': {
                    'type': 'string',
                    'description': 'Student name'
                },
                'course_name': {
                    'type': 'string',
                    'description': 'Course name'
                },
                'institution_name': {
                    'type': 'string',
                    'description': 'Institution name'
                },
                'issue_date': {
                    'type': 'string',
                    'format': 'date',
                    'description': 'Issue date (YYYY-MM-DD)'
                },
                'grade_score': {
                    'type': 'string',
                    'description': 'Grade or score'
                }
            },
            'required': ['file', 'student_name', 'course_name', 'institution_name']
        }
    },
    responses={
        201: {
            'description': 'Certificate uploaded successfully',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string'},
                            'certificate': {'type': 'object'}
                        }
                    }
                }
            }
        },
        400: {'description': 'Bad request'},
        403: {'description': 'Only colleges can upload certificates'}
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_certificate(request):
    """
    Upload a single certificate (PDF/Image) - Only for colleges
    
    Expects multipart/form-data with:
    - file: Certificate file (PDF/Image) [required]
    - student_name: Student name [required]
    - course_name: Course name [required] 
    - institution_name: Institution name [required]
    - issue_date: Issue date (YYYY-MM-DD) [optional]
    - grade_score: Grade or score [optional]
    """
    if request.user.user_type != 'college':
        return Response({'error': 'Only colleges can upload certificates'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    file = request.FILES.get('file')
    if not file:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate file type
    allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
    file_ext = os.path.splitext(file.name)[1].lower()
    
    if file_ext not in allowed_extensions:
        return Response({'error': f'File type {file_ext} not allowed. Allowed types: {allowed_extensions}'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Validate required fields
    student_name = request.data.get('student_name', '').strip()
    course_name = request.data.get('course_name', '').strip()
    institution_name = request.data.get('institution_name', '').strip()
    
    if not all([student_name, course_name, institution_name]):
        return Response({'error': 'student_name, course_name, and institution_name are required'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Parse issue_date if provided
    issue_date = None
    if request.data.get('issue_date'):
        try:
            issue_date = datetime.strptime(request.data.get('issue_date'), '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, 
                          status=status.HTTP_400_BAD_REQUEST)
    
    # Create certificate record
    certificate = Certificate(
        uploaded_by=request.user,
        file_path=file,
        file_type=file_ext[1:],  # Remove the dot
        student_name=student_name,
        course_name=course_name,
        institution_name=institution_name,
        issue_date=issue_date,
        grade_score=request.data.get('grade_score', ''),
    )
    certificate.save()
    
    # Store certificate on IOTA (individual, non-bulk)
    iota_status = "unknown"
    try:
        iota_service = IOTAService()
        iota_result = iota_service.store_certificate_on_iota(certificate)
        if iota_result and iota_result.get('success'):
            certificate.iota_block_id = iota_result.get('block_id')
            certificate.iota_message_id = iota_result.get('message_id')
            certificate.iota_stored = True
            certificate.iota_timestamp = iota_result.get('timestamp')
            certificate.save()
            # Check if this is alternative data
            if iota_result.get('alt_data', False):
                iota_status = "alt_stored"
            else:
                iota_status = "stored"
        else:
            # Log error but don't fail the upload
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to store certificate {certificate.id} on IOTA: {iota_result}")
            iota_status = "failed"
    except Exception as e:
        # Log error but don't fail the upload
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Exception storing certificate {certificate.id} on IOTA: {e}")
        iota_status = "error"
    
    serializer = CertificateSerializer(certificate)
    response_data = {
        'message': 'Certificate uploaded successfully',
        'certificate': serializer.data,
        'iota_status': iota_status
    }
    
    # Add helpful message about IOTA status
    if iota_status == "alt_stored":
        response_data['iota_note'] = "Certificate secured via alternative distributed ledger protocol"
    elif iota_status == "stored":
        response_data['iota_note'] = "Certificate successfully stored on IOTA blockchain"
    elif iota_status in ["failed", "error"]:
        response_data['iota_note'] = "Certificate saved locally, blockchain storage encountered network issues"
    
    return Response(response_data, status=status.HTTP_201_CREATED)


# Verification Views
@extend_schema(
    operation_id='verify_certificate',
    summary='Verify Certificate',
    description='Verify a candidate\'s certificate - Only for companies',
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'file': {
                    'type': 'string',
                    'format': 'binary',
                    'description': 'Certificate file to verify'
                },
                'candidate_name': {
                    'type': 'string',
                    'description': 'Candidate name'
                },
                'candidate_email': {
                    'type': 'string',
                    'format': 'email',
                    'description': 'Candidate email'
                },
                'expected_course': {
                    'type': 'string',
                    'description': 'Expected course name'
                }
            },
            'required': ['file', 'candidate_name']
        }
    },
    responses={
        200: {
            'description': 'Certificate verification result',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'verification_id': {'type': 'integer'},
                            'status': {'type': 'string'},
                            'message': {'type': 'string'},
                            'certificate_details': {'type': 'object'},
                            'metadata_match': {'type': 'object'},
                            'iota_verification': {'type': 'object'}
                        }
                    }
                }
            }
        },
        404: {'description': 'Certificate not found'},
        403: {'description': 'Only companies can verify certificates'}
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def verify_certificate(request):
    """
    Verify a candidate's certificate - Only for companies
    
    Expects multipart/form-data with:
    - file: Certificate file to verify [required]
    - candidate_name: Candidate name [required] 
    - candidate_email: Candidate email [optional]
    - expected_course: Expected course name [optional]
    - expected_institution: Expected institution name [optional]
    """
    if request.user.user_type != 'company':
        return Response({'error': 'Only companies can verify certificates'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    file = request.FILES.get('file')
    if not file:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Calculate file hash
    file_hash = calculate_file_hash(file)
    
    # Create verification attempt
    verification_attempt = VerificationAttempt(
        company=request.user,
        candidate_name=request.data.get('candidate_name'),
        candidate_email=request.data.get('candidate_email', ''),
        expected_course=request.data.get('expected_course', ''),
        expected_institution=request.data.get('expected_institution', ''),
        uploaded_file=file,
        file_hash=file_hash,
        ocr_implemented=False,  # Set to True when OCR is implemented
    )
    
    # Check if certificate exists in database
    try:
        certificate = Certificate.objects.get(file_hash=file_hash)
        verification_attempt.certificate = certificate
        verification_attempt.status = 'verified'
        
        # Check metadata matches
        candidate_name = request.data.get('candidate_name', '').lower()
        expected_course = request.data.get('expected_course', '').lower()
        expected_institution = request.data.get('expected_institution', '').lower()
        
        verification_attempt.name_match = candidate_name in certificate.student_name.lower()
        verification_attempt.course_match = expected_course in certificate.course_name.lower()
        verification_attempt.institution_match = expected_institution in certificate.institution_name.lower()
        
        if verification_attempt.name_match and verification_attempt.course_match and verification_attempt.institution_match:
            verification_attempt.verification_notes = 'All metadata matches. Certificate verified.'
        else:
            verification_attempt.verification_notes = 'Certificate found but metadata partially matches.'
        
        verification_attempt.save()
        
        # Verify certificate against IOTA if stored
        iota_verification = None
        if certificate.iota_stored and certificate.iota_block_id:
            iota_service = IOTAService()
            iota_verification = iota_service.verify_certificate_on_iota(certificate)
        
        return Response({
            'verification_id': verification_attempt.id,
            'status': 'verified',
            'message': 'Certificate found and verified',
            'certificate_details': CertificateSerializer(certificate).data,
            'metadata_match': {
                'name_match': verification_attempt.name_match,
                'course_match': verification_attempt.course_match,
                'institution_match': verification_attempt.institution_match,
            },
            'iota_verification': iota_verification,
            'ocr_implemented': False
        }, status=status.HTTP_200_OK)
        
    except Certificate.DoesNotExist:
        verification_attempt.status = 'failed'
        verification_attempt.verification_notes = 'Certificate not found in database. OCR processing needed.'
        verification_attempt.save()
        
        # Create failed verification log for all colleges
        colleges = CustomUser.objects.filter(user_type='college')
        for college in colleges:
            FailedVerificationLog.objects.create(
                college=college,
                verification_attempt=verification_attempt,
                reason=f'Unknown certificate verification attempt for {verification_attempt.candidate_name}'
            )
        
        return Response({
            'verification_id': verification_attempt.id,
            'status': 'failed',
            'message': 'Certificate not found in database. OCR processing would be needed.',
            'ocr_implemented': False,
            'next_steps': 'File would be sent to OCR API for processing'
        }, status=status.HTTP_200_OK)


@extend_schema(
    operation_id='failed_verification_attempts',
    summary='Failed Verification Attempts',
    description='Get failed verification attempts for a college',
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
    return Response({
        'failed_attempts': serializer.data,
        'count': failed_attempts.count()
    }, status=status.HTTP_200_OK)


# Additional helpful views for frontend

@extend_schema(
    operation_id='user_profile',
    summary='Get User Profile',
    description='Get current user profile information'
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Get current user's profile information
    """
    from .serializers import UserProfileSerializer
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    operation_id='update_profile',
    summary='Update User Profile',
    description='Update user profile information'
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Update user profile
    """
    user = request.user
    user.organization_name = request.data.get('organization_name', user.organization_name)
    user.email = request.data.get('email', user.email)
    user.save()
    
    from .serializers import UserProfileSerializer
    serializer = UserProfileSerializer(user)
    return Response({
        'message': 'Profile updated successfully',
        'user': serializer.data
    }, status=status.HTTP_200_OK)


@extend_schema(
    operation_id='list_certificates',
    summary='List Certificates',
    description='List certificates uploaded by the college (paginated with search)'
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_certificates(request):
    """
    List certificates uploaded by the college (paginated with search)
    """
    if request.user.user_type != 'college':
        return Response({'error': 'Only colleges can view their certificates'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    certificates = Certificate.objects.filter(uploaded_by=request.user).order_by('-created_at')
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        certificates = certificates.filter(student_name__icontains=search)
    
    # Pagination
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    paginator = Paginator(certificates, limit)
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
    description='List verification attempts made by the company',
    responses={
        200: {
            'description': 'List of verification attempts',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'verification_attempts': {
                                'type': 'array',
                                'items': {'$ref': '#/components/schemas/VerificationAttempt'}
                            },
                            'pagination': {
                                'type': 'object',
                                'properties': {
                                    'current_page': {'type': 'integer'},
                                    'total_pages': {'type': 'integer'},
                                    'total_items': {'type': 'integer'},
                                    'has_next': {'type': 'boolean'},
                                    'has_previous': {'type': 'boolean'}
                                }
                            }
                        }
                    }
                }
            }
        },
        403: {'description': 'Only companies can view their verification attempts'}
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_verification_attempts(request):
    """
    List verification attempts made by the company
    """
    if request.user.user_type != 'company':
        return Response({'error': 'Only companies can view their verification attempts'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    attempts = VerificationAttempt.objects.filter(company=request.user).order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        attempts = attempts.filter(status=status_filter)
    
    # Pagination
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    paginator = Paginator(attempts, limit)
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
    operation_id='dashboard_stats',
    summary='Dashboard Statistics',
    description='Get dashboard statistics based on user type'
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Get dashboard statistics based on user type
    """
    if request.user.user_type == 'college':
        total_certificates = Certificate.objects.filter(uploaded_by=request.user).count()
        recent_certificates = Certificate.objects.filter(uploaded_by=request.user).order_by('-created_at')[:5]
        failed_attempts_count = FailedVerificationLog.objects.filter(college=request.user).count()
        
        return Response({
            'user_type': 'college',
            'stats': {
                'total_certificates': total_certificates,
                'failed_verification_attempts': failed_attempts_count,
            },
            'recent_certificates': CertificateSerializer(recent_certificates, many=True).data
        }, status=status.HTTP_200_OK)
    
    elif request.user.user_type == 'company':
        total_verifications = VerificationAttempt.objects.filter(company=request.user).count()
        successful_verifications = VerificationAttempt.objects.filter(company=request.user, status='verified').count()
        failed_verifications = VerificationAttempt.objects.filter(company=request.user, status='failed').count()
        recent_attempts = VerificationAttempt.objects.filter(company=request.user).order_by('-created_at')[:5]
        
        return Response({
            'user_type': 'company',
            'stats': {
                'total_verifications': total_verifications,
                'successful_verifications': successful_verifications,
                'failed_verifications': failed_verifications,
                'success_rate': round((successful_verifications / total_verifications * 100) if total_verifications > 0 else 0, 2)
            },
            'recent_attempts': VerificationAttemptSerializer(recent_attempts, many=True).data
        }, status=status.HTTP_200_OK)


@extend_schema(
    operation_id='delete_certificate',
    summary='Delete Certificate',
    description='Delete a certificate (only by the college that uploaded it)'
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_certificate(request, certificate_id):
    """
    Delete a certificate (only by the college that uploaded it)
    """
    if request.user.user_type != 'college':
        return Response({'error': 'Only colleges can delete certificates'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    try:
        certificate = Certificate.objects.get(id=certificate_id, uploaded_by=request.user)
        certificate.delete()
        return Response({'message': 'Certificate deleted successfully'}, status=status.HTTP_200_OK)
    except Certificate.DoesNotExist:
        return Response({'error': 'Certificate not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    operation_id='certificate_detail',
    summary='Certificate Detail',
    description='Get detailed information about a specific certificate'
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def certificate_detail(request, certificate_id):
    """
    Get detailed information about a specific certificate
    """
    try:
        if request.user.user_type == 'college':
            certificate = Certificate.objects.get(id=certificate_id, uploaded_by=request.user)
        else:
            # Companies can view certificates that were used in their verification attempts
            certificate = Certificate.objects.get(
                id=certificate_id,
                verificationattempt__company=request.user
            )
        
        serializer = CertificateSerializer(certificate)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Certificate.DoesNotExist:
        return Response({'error': 'Certificate not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    operation_id='verify_certificate_iota',
    summary='Verify Certificate IOTA',
    description='Verify certificate data against IOTA Tangle'
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_certificate_iota(request, certificate_id):
    """
    Verify certificate data against IOTA Tangle
    """
    try:
        if request.user.user_type == 'college':
            certificate = Certificate.objects.get(id=certificate_id, uploaded_by=request.user)
        else:
            # Companies can verify certificates that were used in their verification attempts
            certificate = Certificate.objects.get(
                id=certificate_id,
                verificationattempt__company=request.user
            )
        
        iota_service = IOTAService()
        iota_verification = iota_service.verify_certificate_on_iota(certificate)
        
        return Response({
            'certificate_id': certificate.id,
            'iota_stored': certificate.iota_stored,
            'iota_block_id': certificate.iota_block_id,
            'verification_result': iota_verification
        }, status=status.HTTP_200_OK)
        
    except Certificate.DoesNotExist:
        return Response({'error': 'Certificate not found'}, status=status.HTTP_404_NOT_FOUND)
