import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Shield, Eye, EyeOff, LogIn } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import Footer from '../components/Footer';

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    
    try {
      const user = await login(formData);
      toast.success(`Welcome back, ${user.name || user.email}!`);
      
      // Redirect based on user role
      switch (user.role) {
        case 'student':
          navigate('/student-dashboard');
          break;
        case 'college':
          navigate('/college-dashboard');
          break;
        case 'government':
          navigate('/government-dashboard');
          break;
        case 'employer':
          navigate('/employer-dashboard');
          break;
        default:
          navigate('/');
      }
    } catch (error) {
      console.error('Login error:', error);
      toast.error(error.message || 'Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-light flex flex-col justify-between">
      <div className="auth-hero">
        <div className="container">
          <div className="auth-grid">
            <div className="auth-info">
              <div className="logo-section mb-6">
                <Shield size={40} />
                <div>
                  <h1 className="logo-text">New India Credential Kavach</h1>
                  <p className="government-text">Government of Jharkhand</p>
                </div>
              </div>
              <h2 className="auth-title">Welcome Back</h2>
              <p className="auth-subtitle">Secure access to your credential dashboard</p>
              <ul className="auth-points">
                <li>Government-grade security</li>
                <li>Fast and accurate verification</li>
                <li>24/7 availability</li>
              </ul>
            </div>

            <div className="auth-card card">
              <div className="card-header text-center">
                <h2 className="card-title">Sign In</h2>
                <p className="card-subtitle">Use your registered email and password</p>
              </div>

              <form onSubmit={handleSubmit} noValidate>
                {/* Email Field */}
                <div className="form-group">
                  <label htmlFor="email" className="form-label">
                    Email Address
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className={`form-input ${errors.email ? 'border-red-500' : ''}`}
                    placeholder="Enter your email address"
                    required
                  />
                  {errors.email && (
                    <div className="form-error">{errors.email}</div>
                  )}
                </div>

                {/* Password Field */}
                <div className="form-group">
                  <label htmlFor="password" className="form-label">
                    Password
                  </label>
                  <div className="relative">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      id="password"
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      className={`form-input pr-12 ${errors.password ? 'border-red-500' : ''}`}
                      placeholder="Enter your password"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="password-toggle"
                    >
                      {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                    </button>
                  </div>
                  {errors.password && (
                    <div className="form-error">{errors.password}</div>
                  )}
                </div>

                {/* Login Button */}
                <button
                  type="submit"
                  disabled={isLoading}
                  className="btn btn-primary w-full"
                >
                  {isLoading ? (
                    <>
                      <div className="loading-spinner mr-2"></div>
                      Signing In...
                    </>
                  ) : (
                    <>
                      <LogIn size={20} />
                      Sign In
                    </>
                  )}
                </button>
              </form>

              {/* Footer Links */}
              <div className="mt-6 text-center">
                <p className="text-sm text-gray">
                  Don't have an account?{' '}
                  <Link 
                    to="/signup" 
                    className="text-primary hover:underline font-medium"
                  >
                    Sign up here
                  </Link>
                </p>
              </div>

              {/* Demo Credentials */}
              <div className="mt-6 p-4 bg-light rounded-lg">
                <h4 className="font-medium text-sm text-navy mb-2">Available Roles:</h4>
                <div className="text-xs text-gray space-y-2">
                  <div>
                    <strong>Student:</strong> Verify and manage academic documents
                  </div>
                  <div>
                    <strong>College:</strong> Institutional record management
                  </div>
                  <div>
                    <strong>Employer:</strong> Verify student credentials for hiring
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default Login;