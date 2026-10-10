from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Document, AuditLog, db
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

def require_government_role():
    """Decorator to require government role"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'government':
        return jsonify({'message': 'Access denied. Government role required.'}), 403
    
    return user

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """Get all users (government only)"""
    try:
        user = require_government_role()
        if not isinstance(user, User):
            return user  # Return error response
        
        role_filter = request.args.get('role')
        status_filter = request.args.get('status')
        
        query = User.query
        
        if role_filter:
            query = query.filter_by(role=role_filter)
        
        if status_filter == 'pending':
            query = query.filter_by(is_approved=False)
        elif status_filter == 'approved':
            query = query.filter_by(is_approved=True)
        
        users = query.all()
        
        users_data = []
        for u in users:
            user_data = {
                'id': u.id,
                'email': u.email,
                'full_name': u.full_name,
                'phone': u.phone,
                'role': u.role,
                'is_verified': u.is_verified,
                'is_approved': u.is_approved,
                'is_active': u.is_active,
                'created_at': u.created_at.isoformat()
            }
            
            # Add role-specific data
            if u.role == 'student':
                user_data.update({
                    'roll_number': u.roll_number,
                    'college_name': u.college_name,
                    'course': u.course
                })
            elif u.role == 'college':
                user_data.update({
                    'college_name': u.college_name,
                    'college_code': u.college_code,
                    'university': u.university
                })
            elif u.role == 'government':
                user_data.update({
                    'department_name': u.department_name,
                    'designation': u.designation
                })
            
            users_data.append(user_data)
        
        return jsonify({'users': users_data}), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get users', 'error': str(e)}), 500

@admin_bp.route('/users/<user_id>/approve', methods=['POST'])
@jwt_required()
def approve_user(user_id):
    """Approve a user account (government only)"""
    try:
        admin_user = require_government_role()
        if not isinstance(admin_user, User):
            return admin_user  # Return error response
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        approve = data.get('approve', True)
        notes = data.get('notes', '')
        
        user.is_approved = approve
        db.session.commit()
        
        # Log approval action
        from routes.auth import log_user_action
        log_user_action(admin_user.id, 'user_approve', 
                       {'target_user': user_id, 'approved': approve, 'notes': notes}, 
                       'user', user_id)
        
        status = 'approved' if approve else 'rejected'
        return jsonify({'message': f'User {status} successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Approval failed', 'error': str(e)}), 500

@admin_bp.route('/users/<user_id>/activate', methods=['POST'])
@jwt_required()
def toggle_user_activation(user_id):
    """Activate/Deactivate a user account (government only)"""
    try:
        admin_user = require_government_role()
        if not isinstance(admin_user, User):
            return admin_user  # Return error response
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        activate = data.get('activate', True)
        
        user.is_active = activate
        db.session.commit()
        
        # Log activation action
        from routes.auth import log_user_action
        log_user_action(admin_user.id, 'user_activate', 
                       {'target_user': user_id, 'activated': activate}, 
                       'user', user_id)
        
        status = 'activated' if activate else 'deactivated'
        return jsonify({'message': f'User {status} successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Activation failed', 'error': str(e)}), 500

@admin_bp.route('/audit-logs', methods=['GET'])
@jwt_required()
def get_audit_logs():
    """Get audit logs (government only)"""
    try:
        admin_user = require_government_role()
        if not isinstance(admin_user, User):
            return admin_user  # Return error response
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        user_id_filter = request.args.get('user_id')
        action_filter = request.args.get('action')
        
        query = AuditLog.query
        
        if user_id_filter:
            query = query.filter_by(user_id=user_id_filter)
        
        if action_filter:
            query = query.filter(AuditLog.action.contains(action_filter))
        
        # Order by most recent first
        query = query.order_by(AuditLog.created_at.desc())
        
        # Paginate results
        paginated_logs = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        logs_data = []
        for log in paginated_logs.items:
            user = User.query.get(log.user_id)
            log_data = {
                'id': log.id,
                'user_id': log.user_id,
                'user_name': user.full_name if user else 'Unknown',
                'user_email': user.email if user else 'Unknown',
                'action': log.action,
                'resource_type': log.resource_type,
                'resource_id': log.resource_id,
                'details': log.details,
                'ip_address': log.ip_address,
                'created_at': log.created_at.isoformat()
            }
            logs_data.append(log_data)
        
        return jsonify({
            'logs': logs_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated_logs.total,
                'pages': paginated_logs.pages,
                'has_next': paginated_logs.has_next,
                'has_prev': paginated_logs.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get audit logs', 'error': str(e)}), 500

@admin_bp.route('/stats/system', methods=['GET'])
@jwt_required()
def get_system_stats():
    """Get system-wide statistics (government only)"""
    try:
        admin_user = require_government_role()
        if not isinstance(admin_user, User):
            return admin_user  # Return error response
        
        # User statistics
        total_users = User.query.count()
        students = User.query.filter_by(role='student').count()
        colleges = User.query.filter_by(role='college').count()
        government = User.query.filter_by(role='government').count()
        
        verified_users = User.query.filter_by(is_verified=True).count()
        approved_users = User.query.filter_by(is_approved=True).count()
        active_users = User.query.filter_by(is_active=True).count()
        
        # Document statistics
        total_documents = Document.query.count()
        verified_documents = Document.query.filter_by(status='verified').count()
        pending_documents = Document.query.filter_by(status='pending').count()
        rejected_documents = Document.query.filter_by(status='rejected').count()
        
        # Recent activity
        recent_registrations = User.query.filter(
            User.created_at >= datetime.now().replace(day=1)
        ).count()
        
        recent_uploads = Document.query.filter(
            Document.created_at >= datetime.now().replace(day=1)
        ).count()
        
        stats = {
            'users': {
                'total': total_users,
                'students': students,
                'colleges': colleges,
                'government': government,
                'verified': verified_users,
                'approved': approved_users,
                'active': active_users
            },
            'documents': {
                'total': total_documents,
                'verified': verified_documents,
                'pending': pending_documents,
                'rejected': rejected_documents
            },
            'activity': {
                'recent_registrations': recent_registrations,
                'recent_uploads': recent_uploads
            }
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get system stats', 'error': str(e)}), 500