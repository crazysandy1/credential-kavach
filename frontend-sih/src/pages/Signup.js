import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Shield, Eye, EyeOff, UserPlus } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import Footer from '../components/Footer';

const Signup = () => {
  const navigate = useNavigate();
  const { signup } = useAuth();
  const [searchParams] = useSearchParams();
  
  const [selectedRole, setSelectedRole] = useState(searchParams.get('role') || '');
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    role: selectedRole
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const [roleFields, setRoleFields] = useState({});

  useEffect(() => {
    if (selectedRole) {
      setFormData(prev => ({ ...prev, role: selectedRole }));
      initializeRoleFields(selectedRole);
    }
  }, [selectedRole]);

  const initializeRoleFields = (role) => {
    const fields = {};
    
    switch (role) {
      case 'student':
        fields.name = '';
        fields.enrollment_number = '';
        fields.institution = '';
        fields.program = '';
        fields.semester = '';
        fields.academic_year = '';
        break;
      case 'college':
        fields.college_name = '';
        fields.registration_number = '';
        fields.address = '';
        fields.contact_person = '';
        fields.designation = '';
        fields.affiliation = '';
        break;
      case 'employer':
        fields.name = '';
        fields.company_name = '';
        fields.company_registration = '';
        fields.industry = '';
        fields.hr_contact = '';
        fields.address = '';
        break;
      default:
        break;
    }
    
    setRoleFields(fields);
  };

  const handleRoleChange = (role) => {
    setSelectedRole(role);
    setFormData(prev => ({ ...prev, role }));
    initializeRoleFields(role);
    setErrors({});
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    
    if (Object.keys(roleFields).includes(name)) {
      setRoleFields(prev => ({ ...prev, [name]: value }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    // Common validation
    if (!formData.role) {
      newErrors.role = 'Please select a role';
    }
    

    
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters long';
    }
    
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    // Role-specific validation
    const requiredRoleFields = {
      student: ['name', 'enrollment_number', 'institution', 'program'],
      college: ['college_name', 'registration_number', 'contact_person', 'designation'],
      employer: ['name', 'company_name', 'company_registration', 'industry', 'hr_contact']
    };

    const required = requiredRoleFields[formData.role] || [];
    required.forEach(field => {
      if (!roleFields[field] || roleFields[field].trim() === '') {
        newErrors[field] = `${field.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} is required`;
      }
    });

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
      const submitData = {
        ...formData,
        ...roleFields
      };
      delete submitData.confirmPassword;

      await signup(submitData);
      toast.success('Account created successfully! Please log in to continue.');
      navigate('/login');
    } catch (error) {
      console.error('Signup error:', error);
      toast.error(error.message || 'Signup failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const renderRoleSpecificFields = () => {
    switch (selectedRole) {
      case 'student':
        return (
          <>
            <div className="form-group">
              <label className="form-label">Full Name *</label>
              <input
                type="text"
                name="name"
                value={roleFields.name || ''}
                onChange={handleChange}
                className={`form-input ${errors.name ? 'border-red-500' : ''}`}
                placeholder="Enter your full name"
              />
              {errors.name && <div className="form-error">{errors.name}</div>}
            </div>

            <div className="form-group">
              <label className="form-label">Enrollment Number *</label>
              <input
                type="text"
                name="enrollment_number"
                value={roleFields.enrollment_number || ''}
                onChange={handleChange}
                className={`form-input ${errors.enrollment_number ? 'border-red-500' : ''}`}
                placeholder="Enter your enrollment number"
              />
              {errors.enrollment_number && <div className="form-error">{errors.enrollment_number}</div>}
            </div>

            <div className="form-group">
              <label className="form-label">Institution *</label>
              <input
                type="text"
                name="institution"
                value={roleFields.institution || ''}
                onChange={handleChange}
                className={`form-input ${errors.institution ? 'border-red-500' : ''}`}
                placeholder="Enter your institution name"
              />
              {errors.institution && <div className="form-error">{errors.institution}</div>}
            </div>

            <div className="form-group">
              <label className="form-label">Program *</label>
              <input
                type="text"
                name="program"
                value={roleFields.program || ''}
                onChange={handleChange}
                className={`form-input ${errors.program ? 'border-red-500' : ''}`}
                placeholder="e.g., Bachelor of Computer Science"
              />
              {errors.program && <div className="form-error">{errors.program}</div>}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="form-group">
                <label className="form-label">Semester</label>
                <select
                  name="semester"
                  value={roleFields.semester || ''}
                  onChange={handleChange}
                  className="form-select"
                >
                  <option value="">Select Semester</option>
                  {[1,2,3,4,5,6,7,8].map(sem => (
                    <option key={sem} value={sem}>Semester {sem}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Academic Year</label>
                <input
                  type="text"
                  name="academic_year"
                  value={roleFields.academic_year || ''}
                  onChange={handleChange}
                  className="form-input"
                  placeholder="e.g., 2023-24"
                />
              </div>
            </div>
          </>
        );

      case 'college':
        return (
          <>
            <div className="form-group">
              <label className="form-label">College Name *</label>
              <input
                type="text"
                name="college_name"
                value={roleFields.college_name || ''}
                onChange={handleChange}
                className={`form-input ${errors.college_name ? 'border-red-500' : ''}`}
                placeholder="Enter college name"
              />
              {errors.college_name && <div className="form-error">{errors.college_name}</div>}
            </div>

            <div className="form-group">
              <label className="form-label">Registration Number *</label>
              <input
                type="text"
                name="registration_number"
                value={roleFields.registration_number || ''}
                onChange={handleChange}
                className={`form-input ${errors.registration_number ? 'border-red-500' : ''}`}
                placeholder="College registration number"
              />
              {errors.registration_number && <div className="form-error">{errors.registration_number}</div>}
            </div>

            <div className="form-group">
              <label className="form-label">College Address</label>
              <textarea
                name="address"
                value={roleFields.address || ''}
                onChange={handleChange}
                className="form-input"
                rows="3"
                placeholder="Enter college address"
              ></textarea>
            </div>

            <div className="form-group">
              <label className="form-label">Contact Person Name *</label>
              <input
                type="text"
                name="contact_person"
                value={roleFields.contact_person || ''}
                onChange={handleChange}
                className={`form-input ${errors.contact_person ? 'border-red-500' : ''}`}
                placeholder="Principal/Admin name"
              />
              {errors.contact_person && <div className="form-error">{errors.contact_person}</div>}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="form-group">
                <label className="form-label">Designation *</label>
                <input
                  type="text"
                  name="designation"
                  value={roleFields.designation || ''}
                  onChange={handleChange}
                  className={`form-input ${errors.designation ? 'border-red-500' : ''}`}
                  placeholder="e.g., Principal"
                />
                {errors.designation && <div className="form-error">{errors.designation}</div>}
              </div>

              <div className="form-group">
                <label className="form-label">Affiliation</label>
                <input
                  type="text"
                  name="affiliation"
                  value={roleFields.affiliation || ''}
                  onChange={handleChange}
                  className="form-input"
                  placeholder="University/Board affiliation"
                />
              </div>
            </div>
          </>
        );

      case 'employer':
        return (
          <>
            <div className="form-group">
              <label className="form-label">Full Name *</label>
              <input
                type="text"
                name="name"
                value={roleFields.name || ''}
                onChange={handleChange}
                className={`form-input ${errors.name ? 'border-red-500' : ''}`}
                placeholder="Enter your full name"
              />
              {errors.name && <div className="form-error">{errors.name}</div>}
            </div>

            <div className="form-group">
              <label className="form-label">Company Name *</label>
              <input
                type="text"
                name="company_name"
                value={roleFields.company_name || ''}
                onChange={handleChange}
                className={`form-input ${errors.company_name ? 'border-red-500' : ''}`}
                placeholder="Enter company name"
              />
              {errors.company_name && <div className="form-error">{errors.company_name}</div>}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="form-group">
                <label className="form-label">Company Registration *</label>
                <input
                  type="text"
                  name="company_registration"
                  value={roleFields.company_registration || ''}
                  onChange={handleChange}
                  className={`form-input ${errors.company_registration ? 'border-red-500' : ''}`}
                  placeholder="e.g., CIN, Registration No."
                />
                {errors.company_registration && <div className="form-error">{errors.company_registration}</div>}
              </div>

              <div className="form-group">
                <label className="form-label">Industry *</label>
                <select
                  name="industry"
                  value={roleFields.industry || ''}
                  onChange={handleChange}
                  className={`form-select ${errors.industry ? 'border-red-500' : ''}`}
                >
                  <option value="">Select Industry</option>
                  <option value="IT">Information Technology</option>
                  <option value="Banking">Banking & Finance</option>
                  <option value="Healthcare">Healthcare</option>
                  <option value="Manufacturing">Manufacturing</option>
                  <option value="Education">Education</option>
                  <option value="Retail">Retail</option>
                  <option value="Other">Other</option>
                </select>
                {errors.industry && <div className="form-error">{errors.industry}</div>}
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">HR Contact Person *</label>
              <input
                type="text"
                name="hr_contact"
                value={roleFields.hr_contact || ''}
                onChange={handleChange}
                className={`form-input ${errors.hr_contact ? 'border-red-500' : ''}`}
                placeholder="HR Manager name"
              />
              {errors.hr_contact && <div className="form-error">{errors.hr_contact}</div>}
            </div>

            <div className="form-group">
              <label className="form-label">Company Address</label>
              <textarea
                name="address"
                value={roleFields.office_address || ''}
                onChange={handleChange}
                className="form-input"
                rows="3"
                placeholder="Enter office address"
              ></textarea>
            </div>
          </>
        );

      default:
        return null;
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
              <h2 className="auth-title">Create Your Account</h2>
              <p className="auth-subtitle">Join the secure credential verification platform</p>
              <ul className="auth-points">
                <li>Role-based secure access</li>
                <li>Fast verification workflow</li>
                <li>Trusted by institutions</li>
              </ul>
            </div>

            <div className="auth-card card">
              <div className="card-header text-center">
                <h2 className="card-title">Sign Up</h2>
                <p className="card-subtitle">Choose your role and fill the details</p>
              </div>

              <form onSubmit={handleSubmit} noValidate>
                {/* Role Selection */}
                <div className="form-group">
                  <label className="form-label">Select Your Role *</label>
                  <div className="grid grid-cols-3 gap-3">
                    {[
                      { value: 'student', label: 'Student', desc: 'Verify your academic documents' },
                      { value: 'college', label: 'College', desc: 'Manage institutional records' },
                      { value: 'employer', label: 'Employer', desc: 'Verify student credentials' }
                    ].map((role) => (
                      <div
                        key={role.value}
                        onClick={() => handleRoleChange(role.value)}
                        className={`p-4 border-2 rounded-lg text-center transition-all cursor-pointer ${
                          selectedRole === role.value
                            ? 'border-primary bg-orange-50 text-primary cursor-pointer'
                            : 'border-gray-200 hover:border-gray-300 cursor-pointer'
                        }`}
                      >
                        <div className="font-medium">{role.label}</div>
                        <div className="text-xs text-gray mt-1">{role.desc}</div>
                      </div>
                    ))}
                  </div>
                  {errors.role && <div className="form-error">{errors.role}</div>}
                </div>

                {/* Email Field */}
                <div className="form-group">
                  <label htmlFor="email" className="form-label">Email Address *</label>
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
                  {errors.email && <div className="form-error">{errors.email}</div>}
                </div>

                {/* Password Fields */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="form-group">
                    <label htmlFor="password" className="form-label">Password *</label>
                    <div className="relative">
                      <input
                        type={showPassword ? 'text' : 'password'}
                        id="password"
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        className={`form-input pr-12 ${errors.password ? 'border-red-500' : ''}`}
                        placeholder="Enter password"
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
                    {errors.password && <div className="form-error">{errors.password}</div>}
                  </div>

                  <div className="form-group">
                    <label htmlFor="confirmPassword" className="form-label">Confirm Password *</label>
                    <div className="relative">
                      <input
                        type={showConfirmPassword ? 'text' : 'password'}
                        id="confirmPassword"
                        name="confirmPassword"
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        className={`form-input pr-12 ${errors.confirmPassword ? 'border-red-500' : ''}`}
                        placeholder="Confirm password"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        className="password-toggle"
                      >
                        {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                      </button>
                    </div>
                    {errors.confirmPassword && <div className="form-error">{errors.confirmPassword}</div>}
                  </div>
                </div>

                {/* Role-specific Fields */}
                {selectedRole && (
                  <div className="border-t pt-6 mt-6">
                    <h3 className="text-lg font-medium text-navy mb-4">
                      {selectedRole.charAt(0).toUpperCase() + selectedRole.slice(1)} Information
                    </h3>
                    {renderRoleSpecificFields()}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={isLoading || !selectedRole}
                  className="btn btn-primary w-full mt-6"
                >
                  {isLoading ? (
                    <>
                      <div className="loading-spinner mr-2"></div>
                      Creating Account...
                    </>
                  ) : (
                    <>
                      <UserPlus size={20} />
                      Create Account
                    </>
                  )}
                </button>

                <div className="mt-6 text-center">
                  <p className="text-sm text-gray">
                    Already have an account?{' '}
                    <Link 
                      to="/login" 
                      className="text-primary hover:underline font-medium"
                    >
                      Sign in here
                    </Link>
                  </p>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default Signup;