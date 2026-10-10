from flask import Blueprint, request, jsonify, send_from_directory, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from werkzeug.utils import secure_filename
from models import User, Document, db, AuditLog
from final_ocr_system import MarksCardOCRSystem
import os
import uuid
from datetime import datetime, timedelta

api_bp = Blueprint('api', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'tiff', 'bmp'}

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def log_user_action(user_id, action, details=None, resource_type=None, resource_id=None):
    """Log user actions for audit trail"""
    try:
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        print(f"Error logging user action: {e}")

@api_bp.route('/documents', methods=['GET'])
@jwt_required(optional=True)
def get_documents():
    """Get user's documents"""
    try:
        current_user_id = get_jwt_identity()
        
        # If no authentication, return data for visualization
        if not current_user_id:
            import random, string
            names = ['Arjun Sharma', 'Priya Patel', 'Vikram Singh', 'Ananya Gupta', 'Rohit Kumar']
            docs = []
            for i in range(5):
                block_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                docs.append({
                    'id': block_id,
                    'run_id': f'20240917_12345{i}_document',
                    'name': names[i],
                    'link': f'/result/{block_id}'
                })
            return jsonify(docs), 200
            
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get documents based on user role
        if user.role == 'student':
            documents = Document.query.filter_by(uploaded_by=current_user_id).all()
        elif user.role in ['college', 'government', 'employer']:
            # Colleges, government and employers can see all documents
            documents = Document.query.all()
        else:
            documents = []
        
        documents_data = []
        for doc in documents:
            doc_data = {
                'id': doc.id,
                'title': doc.title,
                'document_type': doc.document_type,
                'status': doc.status,
                'description': doc.description,
                'created_at': doc.created_at.isoformat(),
                'file_size': doc.file_size,
                'mime_type': doc.mime_type
            }
            
            # Add uploader info if viewing others' documents
            if user.role in ['college', 'government', 'employer']:
                uploader = User.query.get(doc.uploaded_by)
                doc_data['uploader'] = {
                    'name': uploader.full_name,
                    'email': uploader.email,
                    'role': uploader.role
                } if uploader else None
            
            documents_data.append(doc_data)
        
        return jsonify({'documents': documents_data}), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get documents', 'error': str(e)}), 500

@api_bp.route('/documents/upload', methods=['POST'])
@jwt_required()
def upload_document():
    """Upload a new document"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'message': 'No file uploaded'}), 400
        
        file = request.files['file']
        document_type = request.form.get('document_type', 'marksheet')
        title = request.form.get('title', file.filename)
        description = request.form.get('description', '')
        
        if file.filename == '':
            return jsonify({'message': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'message': 'File type not allowed'}), 400
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{str(uuid.uuid4())}_{filename}"
        
        # Create user-specific upload directory
        user_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], current_user_id)
        os.makedirs(user_upload_dir, exist_ok=True)
        
        file_path = os.path.join(user_upload_dir, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Process with OCR if it's an image
        ocr_data = None
        extracted_text = ""
        
        if file.mimetype and file.mimetype.startswith('image/'):
            try:
                ocr_system = MarksCardOCRSystem(confidence_threshold=0.5)
                marks_data = ocr_system.process_marks_card(file_path, preprocess=True)
                
                # Convert to serializable format
                ocr_data = {
                    'university': marks_data.university,
                    'student_name': marks_data.student_info.name,
                    'roll_number': marks_data.student_info.roll_number,
                    'subjects': [
                        {
                            'course_code': s.course_code,
                            'course_title': s.course_title,
                            'marks': s.total_marks
                        } for s in marks_data.subjects
                    ],
                    'result': marks_data.result,
                    'total_elements': len(marks_data.all_extracted_text)
                }
                
                extracted_text = ' '.join([item['text'] for item in marks_data.all_extracted_text])
                
            except Exception as ocr_error:
                print(f"OCR processing failed: {ocr_error}")
                # Continue without OCR data
        
        # Create document record
        document = Document(
            id=str(uuid.uuid4()),
            title=title,
            document_type=document_type,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            mime_type=file.mimetype,
            description=description,
            uploaded_by=current_user_id,
            ocr_data=ocr_data,
            extracted_text=extracted_text
        )
        
        db.session.add(document)
        db.session.commit()
        
        # Log upload action
        log_user_action(current_user_id, 'document_upload', 
                       {'document_id': document.id, 'document_type': document_type}, 
                       'document', document.id)
        
        return jsonify({
            'message': 'Document uploaded successfully',
            'document': {
                'id': document.id,
                'title': document.title,
                'document_type': document.document_type,
                'status': document.status,
                'created_at': document.created_at.isoformat(),
                'ocr_processed': ocr_data is not None
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Upload failed', 'error': str(e)}), 500

@api_bp.route('/documents/<document_id>', methods=['GET'])
@jwt_required()
def get_document(document_id):
    """Get specific document details"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        document = Document.query.get(document_id)
        
        if not document:
            return jsonify({'message': 'Document not found'}), 404
        
        # Check permissions
        if user.role == 'student' and document.uploaded_by != current_user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        doc_data = {
            'id': document.id,
            'title': document.title,
            'document_type': document.document_type,
            'status': document.status,
            'description': document.description,
            'created_at': document.created_at.isoformat(),
            'file_size': document.file_size,
            'mime_type': document.mime_type,
            'ocr_data': document.ocr_data,
            'extracted_text': document.extracted_text,
            'verification_notes': document.verification_notes
        }
        
        # Add uploader info if user has permission
        if user.role in ['college', 'government']:
            uploader = User.query.get(document.uploaded_by)
            doc_data['uploader'] = {
                'name': uploader.full_name,
                'email': uploader.email,
                'role': uploader.role,
                'college_name': uploader.college_name
            } if uploader else None
        
        return jsonify({'document': doc_data}), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get document', 'error': str(e)}), 500

@api_bp.route('/documents/<document_id>/verify', methods=['POST'])
@jwt_required()
def verify_document(document_id):
    """Verify a document (college/government only)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['college', 'government']:
            return jsonify({'message': 'Access denied'}), 403
        
        document = Document.query.get(document_id)
        
        if not document:
            return jsonify({'message': 'Document not found'}), 404
        
        data = request.get_json()
        status = data.get('status')  # 'verified', 'rejected'
        notes = data.get('notes', '')
        
        if status not in ['verified', 'rejected']:
            return jsonify({'message': 'Invalid status'}), 400
        
        # Update document
        document.status = status
        document.verification_notes = notes
        document.verified_by = current_user_id
        document.verification_date = datetime.utcnow()
        
        db.session.commit()
        
        # Log verification action
        log_user_action(current_user_id, 'document_verify', 
                       {'document_id': document_id, 'status': status}, 
                       'document', document_id)
        
        return jsonify({'message': f'Document {status} successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Verification failed', 'error': str(e)}), 500

@api_bp.route('/documents/<document_id>/download', methods=['GET'])
@jwt_required()
def download_document(document_id):
    """Download document file"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        document = Document.query.get(document_id)
        
        if not document:
            return jsonify({'message': 'Document not found'}), 404
        
        # Check permissions
        if user.role == 'student' and document.uploaded_by != current_user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        if not os.path.exists(document.file_path):
            return jsonify({'message': 'File not found'}), 404
        
        # Log download action
        log_user_action(current_user_id, 'document_download', 
                       {'document_id': document_id}, 
                       'document', document_id)
        
        return send_from_directory(
            os.path.dirname(document.file_path),
            os.path.basename(document.file_path),
            as_attachment=True,
            download_name=document.title
        )
        
    except Exception as e:
        return jsonify({'message': 'Download failed', 'error': str(e)}), 500

@api_bp.route('/documents/<document_id>/ocr', methods=['GET'])
@jwt_required()
def get_document_ocr(document_id):
    """Get OCR extracted data for a specific document"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        document = Document.query.get(document_id)
        
        if not document:
            return jsonify({'message': 'Document not found'}), 404
        
        # Check permissions
        if user.role == 'student' and document.uploaded_by != current_user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        # Return OCR data
        response_data = {
            'document_id': document.id,
            'title': document.title,
            'document_type': document.document_type,
            'ocr_data': document.ocr_data,
            'extracted_text': document.extracted_text,
            'has_ocr_data': document.ocr_data is not None
        }
        
        # Log OCR view action
        log_user_action(current_user_id, 'document_ocr_view', 
                       {'document_id': document_id}, 
                       'document', document_id)
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get OCR data', 'error': str(e)}), 500

@api_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get dashboard statistics"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        stats = {}
        
        if user.role == 'student':
            # Student stats
            total_docs = Document.query.filter_by(uploaded_by=current_user_id).count()
            verified_docs = Document.query.filter_by(uploaded_by=current_user_id, status='verified').count()
            pending_docs = Document.query.filter_by(uploaded_by=current_user_id, status='pending').count()
            
            stats = {
                'total_documents': total_docs,
                'verified_documents': verified_docs,
                'pending_documents': pending_docs,
                'rejected_documents': total_docs - verified_docs - pending_docs
            }
            
        elif user.role in ['college', 'government']:
            # Admin stats
            total_users = User.query.count()
            total_docs = Document.query.count()
            pending_approvals = User.query.filter_by(is_approved=False, role='college').count()
            
            stats = {
                'total_usCreaers': total_users,
                'total_documents': total_docs,
                'pending_approvals': pending_approvals,
                'verified_documents': Document.query.filter_by(status='verified').count(),
                'pending_documents': Document.query.filter_by(status='pending').count()
            }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get stats', 'error': str(e)}), 500

@api_bp.route('/verify-document', methods=['POST'])
@jwt_required()
def employer_verify_document():
    """Verify document authenticity for employers"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'employer':
            return jsonify({'message': 'Access denied. Employer role required.'}), 403
        
        data = request.get_json()
        student_email = data.get('student_email')
        document_type = data.get('document_type', 'marks_card')
        
        if not student_email:
            return jsonify({'message': 'Student email is required'}), 400
        
        # Find student by email
        student = User.query.filter_by(email=student_email, role='student').first()
        if not student:
            return jsonify({
                'verified': False,
                'status': 'STUDENT_NOT_FOUND',
                'message': 'No student found with this email address'
            }), 200
        
        # Find student's documents
        documents = Document.query.filter_by(
            uploaded_by=student.id,
            document_type=document_type
        ).order_by(Document.created_at.desc()).all()
        
        if not documents:
            return jsonify({
                'verified': False,
                'status': 'NO_DOCUMENTS',
                'message': 'No documents found for this student',
                'student_info': {
                    'name': student.full_name,
                    'email': student.email,
                    'college': student.college_name,
                    'course': student.course
                }
            }), 200
        
        # Check latest document for fraud indicators
        latest_doc = documents[0]
        
        # Fraud detection logic
        fraud_indicators = []
        is_fraud = False
        
        # Check for multiple uploads of same document type in short time
        recent_docs = Document.query.filter_by(
            uploaded_by=student.id,
            document_type=document_type
        ).filter(
            Document.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        if recent_docs > 3:
            fraud_indicators.append('Multiple uploads in short time period')
            is_fraud = True
        
        # Check if document status is suspicious
        if latest_doc.status in ['rejected', 'flagged']:
            fraud_indicators.append('Document previously flagged or rejected')
            is_fraud = True
        
        # Check file size anomalies (too small might be fake)
        if latest_doc.file_size and latest_doc.file_size < 10000:  # Less than 10KB
            fraud_indicators.append('Unusually small file size')
        
        # Simulate OCR content verification (in real implementation, check against known patterns)
        if 'tampered' in (latest_doc.description or '').lower():
            fraud_indicators.append('Content analysis indicates tampering')
            is_fraud = True
        
        verification_result = {
            'verified': not is_fraud and latest_doc.status == 'verified',
            'status': 'FRAUD_DETECTED' if is_fraud else 'VERIFIED' if latest_doc.status == 'verified' else 'PENDING_VERIFICATION',
            'confidence_score': 95 if not is_fraud and latest_doc.status == 'verified' else 30 if is_fraud else 70,
            'student_info': {
                'name': student.full_name,
                'email': student.email,
                'college': student.college_name,
                'course': student.course,
                'roll_number': student.roll_number
            },
            'document_info': {
                'id': latest_doc.id,
                'title': latest_doc.title,
                'upload_date': latest_doc.created_at.isoformat(),
                'status': latest_doc.status,
                'file_size': latest_doc.file_size
            },
            'fraud_indicators': fraud_indicators,
            'verification_timestamp': datetime.utcnow().isoformat(),
            'verified_by': user.company_name or user.full_name
        }
        
        # Log the verification attempt
        log_user_action(
            user_id=current_user_id,
            action='document_verification',
            details=f'Verified document for {student_email}',
            resource_type='document',
            resource_id=latest_doc.id
        )
        
        return jsonify(verification_result), 200
        
    except Exception as e:
        return jsonify({'message': 'Verification failed', 'error': str(e)}), 500

@api_bp.route('/employer/profile', methods=['PUT'])
@jwt_required()
def update_employer_profile():
    """Update employer profile information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'employer':
            return jsonify({'message': 'Access denied. Employer role required.'}), 403
        
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = ['full_name', 'phone', 'company_name', 'company_registration', 'industry', 'hr_contact']
        
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        # Update timestamp
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log the action
        log_user_action(
            user_id=current_user_id,
            action='profile_update',
            details='Updated employer profile information',
            resource_type='user',
            resource_id=user.id
        )
        
        # Return updated user data
        user_data = {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'phone': user.phone,
            'company_name': user.company_name,
            'company_registration': user.company_registration,
            'industry': user.industry,
            'hr_contact': user.hr_contact,
            'is_verified': user.is_verified,
            'is_approved': user.is_approved,
            'is_active': user.is_active,
            'updated_at': user.updated_at.isoformat()
        }
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user_data
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update profile', 'error': str(e)}), 500

@api_bp.route('/employer/verify-document', methods=['POST'])
@jwt_required()
def employer_submit_verification():
    """Submit employer verification result for a document"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'employer':
            return jsonify({'message': 'Access denied. Employer role required.'}), 403
        
        data = request.get_json()
        document_id = data.get('document_id')
        verification_status = data.get('verification_status')  # 'verified', 'rejected', 'suspicious'
        notes = data.get('notes', '')
        confidence_score = data.get('confidence_score', 0)
        
        if not document_id or not verification_status:
            return jsonify({'message': 'Document ID and verification status are required'}), 400
        
        # Find the document
        document = Document.query.get(document_id)
        if not document:
            return jsonify({'message': 'Document not found'}), 404
        
        # Update document verification status
        document.status = verification_status
        document.verification_notes = f"Employer Verification by {user.company_name}: {notes}"
        document.verification_date = datetime.utcnow()
        document.verified_by = user.id
        
        # Add employer-specific verification data to ocr_data
        if not document.ocr_data:
            document.ocr_data = {}
        
        document.ocr_data['employer_verification'] = {
            'employer_company': user.company_name,
            'verifier_name': user.full_name,
            'verification_date': datetime.utcnow().isoformat(),
            'confidence_score': confidence_score,
            'status': verification_status,
            'notes': notes
        }
        
        db.session.commit()
        
        # Log the verification action
        log_user_action(
            user_id=current_user_id,
            action='document_verification',
            details=f'Verified document {document_id} with status: {verification_status}',
            resource_type='document',
            resource_id=document_id
        )
        
        return jsonify({
            'message': 'Verification submitted successfully',
            'document_id': document_id,
            'verification_status': verification_status,
            'confidence_score': confidence_score
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to submit verification', 'error': str(e)}), 500