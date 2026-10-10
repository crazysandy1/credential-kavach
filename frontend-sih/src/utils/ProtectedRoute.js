import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ children, requiredRole }) => {
  const { isAuthenticated, isLoading, hasRole, user } = useAuth();

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-gray">Checking authentication...</p>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Check role-based access if required role is specified
  if (requiredRole && !hasRole(requiredRole)) {
    // Redirect to appropriate dashboard based on user's actual role
    const dashboardMap = {
      'student': '/student-dashboard',
      'college': '/college-dashboard',
      'government': '/government-dashboard',
      'employer': '/employer-dashboard'
    };
    
    const userDashboard = dashboardMap[user?.role];
    return <Navigate to={userDashboard || '/'} replace />;
  }

  // Check if user account is approved (for college, government, and employer roles)
  // Skip approval check for the designated admin account
  if (user && ['college', 'government', 'employer'].includes(user.role)) {
    const isAdminAccount = user.email === 'admin@credentialkavach.gov.in';
    const isApproved = user.is_approved || isAdminAccount; // Admin is always approved
    
    console.log('User approval check:', { 
      email: user.email, 
      role: user.role, 
      is_approved: user.is_approved,
      isAdminAccount,
      finalApproval: isApproved 
    }); // Debug log
    
    if (!isApproved) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-light">
          <div className="card text-center max-w-md">
            <div className="card-header">
              <h2 className="card-title">Account Pending Approval</h2>
              <p className="card-subtitle">
                Your {user.role} account is currently under review by government administrators.
              </p>
            </div>
            <div className="mb-4">
              <div className="status-badge status-pending">
                Pending Approval
              </div>
            </div>
            <p className="text-sm text-gray mb-4">
              You will receive an email notification once your account has been approved.
              This process typically takes 1-2 business days.
            </p>
            <button
              onClick={() => window.location.href = '/login'}
              className="btn btn-primary w-full"
            >
              Back to Login
            </button>
          </div>
        </div>
      );
    }
  }

  // Check email verification (if implemented)
  if (user && !user.email_verified && process.env.REACT_APP_REQUIRE_EMAIL_VERIFICATION === 'true') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-light">
        <div className="card text-center max-w-md">
          <div className="card-header">
            <h2 className="card-title">Email Verification Required</h2>
            <p className="card-subtitle">
              Please verify your email address to continue.
            </p>
          </div>
          <p className="text-sm text-gray mb-4">
            We've sent a verification email to <strong>{user.email}</strong>. 
            Please check your inbox and click the verification link.
          </p>
          <div className="flex flex-col gap-2">
            <button className="btn btn-primary">
              Resend Verification Email
            </button>
            <button
              onClick={() => window.location.href = '/login'}
              className="btn btn-outline"
            >
              Back to Login
            </button>
          </div>
        </div>
      </div>
    );
  }

  return children;
};

export default ProtectedRoute;