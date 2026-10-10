import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiService } from '../services/api';
import { toast } from 'react-toastify';
import { User, Building2, Mail, Phone, FileText, CheckCircle, Clock, AlertCircle, Edit2, Save, X } from 'lucide-react';

const EmployerProfile = () => {
  const { user } = useAuth();
  const [profileData, setProfileData] = useState({
    full_name: '',
    email: '',
    phone: '',
    company_name: '',
    company_registration: '',
    industry: '',
    hr_contact: '',
    company_description: '',
    company_website: ''
  });
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (user) {
      setProfileData({
        full_name: user.full_name || '',
        email: user.email || '',
        phone: user.phone || '',
        company_name: user.company_name || '',
        company_registration: user.company_registration || '',
        industry: user.industry || '',
        hr_contact: user.hr_contact || '',
        company_description: user.company_description || '',
        company_website: user.company_website || ''
      });
    }
  }, [user]);

  const validateForm = () => {
    const newErrors = {};
    
    if (!profileData.full_name.trim()) {
      newErrors.full_name = 'Full name is required';
    }
    
    if (!profileData.phone.trim()) {
      newErrors.phone = 'Phone number is required';
    } else if (!/^\+?[\d\s-()]{10,}$/.test(profileData.phone)) {
      newErrors.phone = 'Please enter a valid phone number';
    }
    
    if (!profileData.company_name.trim()) {
      newErrors.company_name = 'Company name is required';
    }
    
    if (!profileData.company_registration.trim()) {
      newErrors.company_registration = 'Company registration is required';
    }
    
    if (!profileData.industry.trim()) {
      newErrors.industry = 'Industry is required';
    }
    
    if (profileData.hr_contact && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(profileData.hr_contact)) {
      newErrors.hr_contact = 'Please enter a valid email address';
    }
    
    if (profileData.company_website && !/^https?:\/\/.+\..+/.test(profileData.company_website)) {
      newErrors.company_website = 'Please enter a valid website URL (include http:// or https://)';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setProfileData(prev => ({
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

  const handleSave = async () => {
    if (!validateForm()) {
      toast.error('Please fix the errors before saving');
      return;
    }
    
    setIsLoading(true);
    try {
      const response = await apiService.updateEmployerProfile(profileData);
      toast.success('Profile updated successfully!');
      setIsEditing(false);
      setErrors({});
    } catch (error) {
      toast.error('Failed to update profile: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    // Reset to original user data
    if (user) {
      setProfileData({
        full_name: user.full_name || '',
        email: user.email || '',
        phone: user.phone || '',
        company_name: user.company_name || '',
        company_registration: user.company_registration || '',
        industry: user.industry || '',
        hr_contact: user.hr_contact || '',
        company_description: user.company_description || '',
        company_website: user.company_website || ''
      });
    }
    setIsEditing(false);
    setErrors({});
  };

  const getStatusInfo = (status, type) => {
    const configs = {
      verified: {
        true: { icon: CheckCircle, color: 'text-green-500', bg: 'bg-green-50', text: 'Verified' },
        false: { icon: AlertCircle, color: 'text-yellow-500', bg: 'bg-yellow-50', text: 'Unverified' }
      },
      approved: {
        true: { icon: CheckCircle, color: 'text-green-500', bg: 'bg-green-50', text: 'Approved' },
        false: { icon: Clock, color: 'text-yellow-500', bg: 'bg-yellow-50', text: 'Pending' }
      },
      active: {
        true: { icon: CheckCircle, color: 'text-green-500', bg: 'bg-green-50', text: 'Active' },
        false: { icon: AlertCircle, color: 'text-red-500', bg: 'bg-red-50', text: 'Inactive' }
      }
    };
    
    return configs[type][status.toString()] || configs[type]['false'];
  };

  return (
    <div className="profile-container">
      <div className="card">
        {/* Profile Header */}
        <div className="profile-header">
          <div className="profile-avatar">
            <Building2 size={32} />
          </div>
          <h1 className="text-2xl font-bold mb-2">{profileData.company_name || 'Company Profile'}</h1>
          <p className="text-lg opacity-90">{profileData.full_name}</p>
          <div className="flex items-center justify-center gap-4 mt-4">
            {/* Status indicators */}
            {['verified', 'approved', 'active'].map((status) => {
              const statusValue = user?.[`is_${status}`] || false;
              const config = getStatusInfo(statusValue, status);
              const Icon = config.icon;
              
              return (
                <div key={status} className={`flex items-center gap-2 px-3 py-1 rounded-full ${config.bg}`}>
                  <Icon size={16} className={config.color} />
                  <span className={`text-sm font-medium ${config.color}`}>
                    {config.text}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Profile Form */}
        <div className="profile-form">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-xl font-bold text-gray-900">Profile Information</h2>
              <p className="text-gray-600">Manage your company and contact details</p>
            </div>
            
            <div className="flex gap-2">
              {!isEditing ? (
                <button
                  onClick={() => setIsEditing(true)}
                  className="btn btn-primary flex items-center gap-2"
                >
                  <Edit2 size={16} />
                  Edit Profile
                </button>
              ) : (
                <>
                  <button
                    onClick={handleCancel}
                    className="btn btn-secondary flex items-center gap-2"
                    disabled={isLoading}
                  >
                    <X size={16} />
                    Cancel
                  </button>
                  <button
                    onClick={handleSave}
                    className={`btn btn-primary flex items-center gap-2 ${isLoading ? 'loading' : ''}`}
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <div className="spinner"></div>
                    ) : (
                      <Save size={16} />
                    )}
                    {isLoading ? 'Saving...' : 'Save Changes'}
                  </button>
                </>
              )}
            </div>
          </div>

          {/* Personal Information Section */}
          <div className="form-section">
            <h3 className="section-title">
              <User size={18} />
              Personal Information
            </h3>
            
            <div className="form-row">
              <div className="form-group">
                <label>Full Name *</label>
                <input
                  type="text"
                  name="full_name"
                  value={profileData.full_name}
                  onChange={handleInputChange}
                  disabled={!isEditing}
                  className={errors.full_name ? 'input-error' : ''}
                  placeholder="Enter your full name"
                />
                {errors.full_name && <div className="form-error">{errors.full_name}</div>}
              </div>

              <div className="form-group">
                <label>Email Address</label>
                <input
                  type="email"
                  name="email"
                  value={profileData.email}
                  disabled={true}
                  className="bg-gray-100 cursor-not-allowed"
                  placeholder="Email cannot be changed"
                />
                <div className="form-success">Email is verified and cannot be modified</div>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Phone Number *</label>
                <input
                  type="tel"
                  name="phone"
                  value={profileData.phone}
                  onChange={handleInputChange}
                  disabled={!isEditing}
                  className={errors.phone ? 'input-error' : ''}
                  placeholder="+1 (555) 123-4567"
                />
                {errors.phone && <div className="form-error">{errors.phone}</div>}
              </div>
            </div>
          </div>

          {/* Company Information Section */}
          <div className="form-section">
            <h3 className="section-title">
              <Building2 size={18} />
              Company Information
            </h3>
            
            <div className="form-row">
              <div className="form-group">
                <label>Company Name *</label>
                <input
                  type="text"
                  name="company_name"
                  value={profileData.company_name}
                  onChange={handleInputChange}
                  disabled={!isEditing}
                  className={errors.company_name ? 'input-error' : ''}
                  placeholder="Enter company name"
                />
                {errors.company_name && <div className="form-error">{errors.company_name}</div>}
              </div>

              <div className="form-group">
                <label>Company Registration *</label>
                <input
                  type="text"
                  name="company_registration"
                  value={profileData.company_registration}
                  onChange={handleInputChange}
                  disabled={!isEditing}
                  className={errors.company_registration ? 'input-error' : ''}
                  placeholder="Registration number"
                />
                {errors.company_registration && <div className="form-error">{errors.company_registration}</div>}
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Industry *</label>
                <select
                  name="industry"
                  value={profileData.industry}
                  onChange={handleInputChange}
                  disabled={!isEditing}
                  className={errors.industry ? 'input-error' : ''}
                >
                  <option value="">Select Industry</option>
                  <option value="Technology">Technology</option>
                  <option value="Finance">Finance</option>
                  <option value="Healthcare">Healthcare</option>
                  <option value="Education">Education</option>
                  <option value="Manufacturing">Manufacturing</option>
                  <option value="Consulting">Consulting</option>
                  <option value="Retail">Retail</option>
                  <option value="Transportation">Transportation</option>
                  <option value="Real Estate">Real Estate</option>
                  <option value="Other">Other</option>
                </select>
                {errors.industry && <div className="form-error">{errors.industry}</div>}
              </div>

              <div className="form-group">
                <label>Company Website</label>
                <input
                  type="url"
                  name="company_website"
                  value={profileData.company_website}
                  onChange={handleInputChange}
                  disabled={!isEditing}
                  className={errors.company_website ? 'input-error' : ''}
                  placeholder="https://company.com"
                />
                {errors.company_website && <div className="form-error">{errors.company_website}</div>}
              </div>
            </div>

            <div className="form-group">
              <label>Company Description</label>
              <textarea
                name="company_description"
                value={profileData.company_description}
                onChange={handleInputChange}
                disabled={!isEditing}
                placeholder="Brief description of your company..."
                rows="4"
              />
            </div>
          </div>

          {/* Contact Information Section */}
          <div className="form-section">
            <h3 className="section-title">
              <Mail size={18} />
              HR Contact Information
            </h3>
            
            <div className="form-group">
              <label>HR Contact Email</label>
              <input
                type="email"
                name="hr_contact"
                value={profileData.hr_contact}
                onChange={handleInputChange}
                disabled={!isEditing}
                className={errors.hr_contact ? 'input-error' : ''}
                placeholder="hr@company.com"
              />
              {errors.hr_contact && <div className="form-error">{errors.hr_contact}</div>}
              <div className="text-sm text-gray-500 mt-1">
                This email will be used for document verification communications
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmployerProfile;