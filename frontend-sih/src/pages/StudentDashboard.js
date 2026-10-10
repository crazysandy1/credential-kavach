import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Upload, 
  FileText, 
  Clock, 
  CheckCircle, 
  XCircle, 
  Eye, 
  LogOut, 
  User, 
  GraduationCap,
  Calendar,
  Phone,
  Mail,
  IdCard,
  Camera,
  Edit3,
  Save,
  X,
  AlertCircle,
  FileCheck,
  Settings,
  BookOpen,
  Award,
  TrendingUp,
  Shield,
  Hash
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import './StudentDashboard.css';

const StudentDashboard = () => {
  const navigate = useNavigate();
  const { user, logout, updateUser } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [viewingDocument, setViewingDocument] = useState(null);
  const [ocrData, setOcrData] = useState(null);
  const [ocrLoading, setOcrLoading] = useState(false);
  
  // New states for enhanced features
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [profileData, setProfileData] = useState({});
  const [isCheckingDuplicate, setIsCheckingDuplicate] = useState(false);
  const [duplicateFound, setDuplicateFound] = useState(null);
  const [profilePicture, setProfilePicture] = useState(null);
  const [showMyDocuments, setShowMyDocuments] = useState(false);

  useEffect(() => {
    loadDocuments();
    initializeProfile();
  }, []);

  const initializeProfile = () => {
    if (user) {
      setProfileData({
        full_name: user.full_name || '',
        roll_number: user.roll_number || '',
        college_name: user.college_name || '',
        course: user.course || '',
        year_of_study: user.year_of_study || ''
      });
    }
  };

  const loadDocuments = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5001/api/documents', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setDocuments(data.documents || []);
      } else {
        console.error('Failed to load documents');
        setDocuments([]);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error loading documents:', error);
      setDocuments([]);
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handleFileSelect = async (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      await checkForDuplicate(file);
    }
  };

  const checkForDuplicate = async (file) => {
    setIsCheckingDuplicate(true);
    setDuplicateFound(null);

    try {
      // Check if a document with similar name already exists
      const existingDocument = documents.find(doc => 
        doc.title.toLowerCase().includes(file.name.toLowerCase().split('.')[0]) ||
        file.name.toLowerCase().includes(doc.title.toLowerCase().split('.')[0])
      );

      if (existingDocument) {
        setDuplicateFound(existingDocument);
        
        // Show processing message and redirect to My Documents
        toast.success('Processing... Redirecting to your documents');
        
        // Simulate processing time then redirect
        setTimeout(() => {
          setSelectedFile(null);
          setDuplicateFound(null);
          setActiveTab('documents');
          setShowMyDocuments(true);
          // toast(`Similar document "${existingDocument.title}" already exists`, {
          //   icon: 'ℹ️',
          //   style: {
          //     background: '#e0f2fe',
          //     color: '#0c4a6e',
          //   },
          // });
        }, 2000);
        
      } else {
        toast.success('Document is ready for upload');
      }
    } catch (error) {
      console.error('Error checking for duplicates:', error);
    } finally {
      setIsCheckingDuplicate(false);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setDragActive(false);
  };

  const handleDrop = async (event) => {
    event.preventDefault();
    event.stopPropagation();
    setDragActive(false);
    
    const files = event.dataTransfer.files;
    if (files && files[0]) {
      setSelectedFile(files[0]);
      await checkForDuplicate(files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    // If duplicate found, show My Documents section instead
    if (duplicateFound) {
      setShowMyDocuments(true);
      setActiveTab('documents');
      toast('Similar document exists. Opening My Documents...', {
        icon: 'ℹ️',
        style: {
          background: '#e0f2fe',
          color: '#0c4a6e',
        },
      });
      return;
    }

    try {
      setUploadProgress(10);
      toast.loading('Processing document...', { id: 'upload' });
      
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('title', selectedFile.name);
      formData.append('document_type', getDocumentType(selectedFile.name));
      formData.append('description', `Uploaded ${selectedFile.name}`);

      const token = localStorage.getItem('token');
      
      setUploadProgress(50);
      
      const response = await fetch('http://localhost:5001/api/documents/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      setUploadProgress(80);

      if (response.ok) {
        const data = await response.json();
        console.log('Upload successful:', data);
        
        // Reload documents to get the updated list
        await loadDocuments();
        
        setUploadProgress(100);
        toast.success('Document uploaded successfully!', { id: 'upload' });
        
        setTimeout(() => {
          setSelectedFile(null);
          setUploadProgress(0);
          setDuplicateFound(null);
          setActiveTab('documents');
          setShowMyDocuments(true);
        }, 1000);
      } else {
        const errorData = await response.json();
        console.error('Upload failed:', errorData);
        toast.error(`Upload failed: ${errorData.message}`, { id: 'upload' });
        setUploadProgress(0);
      }
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Upload failed. Please try again.', { id: 'upload' });
      setUploadProgress(0);
    }
  };

  const getDocumentType = (filename) => {
    const name = filename.toLowerCase();
    if (name.includes('marksheet') || name.includes('marks')) return 'marksheet';
    if (name.includes('certificate') || name.includes('cert')) return 'certificate';
    if (name.includes('diploma')) return 'diploma';
    return 'document';
  };

  const viewDocument = async (document) => {
    setViewingDocument(document);
    setOcrLoading(true);
    setOcrData(null);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:5001/api/documents/${document.id}/ocr`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setOcrData(data);
      } else {
        console.error('Failed to load OCR data');
        setOcrData({ error: 'Failed to load OCR data' });
      }
    } catch (error) {
      console.error('Error loading OCR data:', error);
      setOcrData({ error: 'Error loading OCR data' });
    } finally {
      setOcrLoading(false);
    }
  };

  const closeDocumentView = () => {
    setViewingDocument(null);
    setOcrData(null);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'verified':
        return '#22c55e';
      case 'pending':
        return '#f59e0b';
      case 'rejected':
        return '#ef4444';
      default:
        return '#6b7280';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'verified':
        return <CheckCircle size={20} color="#22c55e" />;
      case 'pending':
        return <Clock size={20} color="#f59e0b" />;
      case 'rejected':
        return <XCircle size={20} color="#ef4444" />;
      default:
        return <FileText size={20} color="#6b7280" />;
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Profile management functions
  const handleProfileEdit = () => {
    setIsEditingProfile(true);
  };

  const handleProfileSave = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5001/api/auth/profile', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(profileData)
      });

      if (response.ok) {
        const updatedUser = await response.json();
        updateUser(updatedUser);
        setIsEditingProfile(false);
        toast.success('Profile updated successfully!');
      } else {
        const errorData = await response.json();
        toast.error(`Update failed: ${errorData.message}`);
      }
    } catch (error) {
      console.error('Profile update error:', error);
      toast.error('Profile update failed. Please try again.');
    }
  };

  const handleProfileCancel = () => {
    initializeProfile();
    setIsEditingProfile(false);
  };

  const handleProfileChange = (field, value) => {
    setProfileData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleProfilePictureChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setProfilePicture(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const getProfileCompletionPercentage = () => {
    if (!user) return 0;
    
    // Only academic fields now (removed personal info fields)
    const fields = [
      'roll_number',
      'course',
      'college_name',
      'year_of_study'
    ];
    
    const filledFields = fields.filter(field => user[field] && user[field].trim() !== '');
    const completionPercentage = (filledFields.length / fields.length) * 100;
    
    // Add bonus for profile picture
    const profilePictureBonus = profilePicture ? 20 : 0;
    
    return Math.min(completionPercentage + profilePictureBonus, 100);
  };

  return (
    <div className="student-dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <div className="header-left">
            <div className="logo-section">
              <div className="logo-icon">
                <GraduationCap size={32} color="#FF6B35" />
              </div>
              <div className="logo-text">
                <h1>Student Dashboard</h1>
                <p>New India Credential Kavach</p>
              </div>
            </div>
          </div>
          <div className="header-right">
            <div className="user-info">
              <User size={20} />
              <span>{user?.full_name || 'Student'}</span>
            </div>
            <button className="logout-btn" onClick={handleLogout}>
              <LogOut size={18} />
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="dashboard-main">
        <div className="dashboard-container">
          {/* Enhanced Sidebar */}
          <aside className="dashboard-sidebar modern">
            <div className="sidebar-header">
              <div className="sidebar-logo">
                <Shield size={24} />
                <span>Credential Kavach</span>
              </div>
            </div>
            
            <nav className="sidebar-nav">
              <button 
                className={`nav-item ${activeTab === 'overview' ? 'active' : ''}`}
                onClick={() => setActiveTab('overview')}
              >
                <User size={18} />
                <span>Overview</span>
                {activeTab === 'overview' && <div className="active-indicator"></div>}
              </button>
              <button 
                className={`nav-item ${activeTab === 'upload' ? 'active' : ''}`}
                onClick={() => setActiveTab('upload')}
              >
                <Upload size={18} />
                <span>Upload Document</span>
                {activeTab === 'upload' && <div className="active-indicator"></div>}
              </button>
              <button 
                className={`nav-item ${activeTab === 'documents' ? 'active' : ''}`}
                onClick={() => setActiveTab('documents')}
              >
                <FileText size={18} />
                <span>My Documents</span>
                {/* <div className="document-count">{documents.length}</div> */}
                {activeTab === 'documents' && <div className="active-indicator"></div>}
              </button>
            </nav>

            <div className="sidebar-footer">
              <div className="user-profile-mini">
                <div className="mini-avatar">
                  {profilePicture ? (
                    <img src={profilePicture} alt="Profile" />
                  ) : (
                    <User size={16} />
                  )}
                </div>
                <div className="mini-info">
                  <span className="mini-name">{user?.full_name?.split(' ')[0] || 'Student'}</span>
                  <span className="mini-role">Student</span>
                </div>
              </div>
            </div>
          </aside>

          {/* Content Area */}
          <section className="dashboard-content">
            {activeTab === 'overview' && (
              <div className="overview-tab">
                <div className="welcome-section">
                  <div className="welcome-text">
                    <h2>Welcome back, {user?.full_name || 'Student'}! 👋</h2>
                    <p>Manage your academic credentials with New India Credential Kavach</p>
                  </div>
                  <div className="welcome-actions">
                    <button 
                      className="btn-primary"
                      onClick={() => setActiveTab('upload')}
                    >
                      <Upload size={18} />
                      Upload Document
                    </button>
                  </div>
                </div>
                
                {/* Enhanced Profile Card */}
                <div className="profile-card modern">
                  <div className="profile-header">
                    <div className="profile-picture-section">
                      <div className="profile-picture">
                        {profilePicture ? (
                          <img src={profilePicture} alt="Profile" />
                        ) : (
                          <User size={32} />
                        )}
                        <input
                          type="file"
                          id="profile-pic"
                          accept="image/*"
                          onChange={handleProfilePictureChange}
                          style={{ display: 'none' }}
                        />
                        <label htmlFor="profile-pic" className="camera-btn">
                          <Camera size={14} />
                        </label>
                      </div>
                      <div className="profile-basic">
                        <h3>{user?.full_name || 'Student Name'}</h3>
                        <p className="profile-role">
                          <Shield size={16} />
                          Verified Student
                        </p>
                      </div>
                    </div>
                    <div className="profile-actions">
                      {!isEditingProfile ? (
                        <button className="btn-secondary" onClick={handleProfileEdit}>
                          <Edit3 size={16} />
                          Edit Profile
                        </button>
                      ) : (
                        <div className="edit-actions">
                          <button className="btn-success" onClick={handleProfileSave}>
                            <Save size={16} />
                            Save
                          </button>
                          <button className="btn-outline" onClick={handleProfileCancel}>
                            <X size={16} />
                            Cancel
                          </button>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="profile-completion">
                    <div className="completion-header">
                      <h4>Profile Completion</h4>
                      <div className="completion-percentage">
                        {Math.round(getProfileCompletionPercentage())}%
                      </div>
                    </div>
                    <div className="completion-bar">
                      <div 
                        className="completion-fill" 
                        style={{ width: `${getProfileCompletionPercentage()}%` }}
                      ></div>
                    </div>
                    <p className="completion-message">
                      {getProfileCompletionPercentage() < 100 
                        ? 'Complete your profile to enhance credibility' 
                        : 'Your profile is complete! 🎉'}
                    </p>
                  </div>

                  <div className="profile-details">
                    <div className="profile-grid enhanced">
                      <div className="profile-group academic-only">
                        <h4>🎓 Academic Information</h4>
                        <div className="profile-item">
                          <IdCard size={18} />
                          <div className="item-content">
                            <label>Roll Number</label>
                            {!isEditingProfile ? (
                              <span className={!user?.roll_number ? 'empty-field' : ''}>
                                {user?.roll_number || (
                                  <span className="add-info-prompt">
                                    <Edit3 size={14} />
                                    Click edit to add roll number
                                  </span>
                                )}
                              </span>
                            ) : (
                              <input
                                type="text"
                                value={profileData.roll_number}
                                onChange={(e) => handleProfileChange('roll_number', e.target.value)}
                                className="edit-input"
                                placeholder="Enter your roll number"
                              />
                            )}
                          </div>
                        </div>
                        <div className="profile-item">
                          <GraduationCap size={18} />
                          <div className="item-content">
                            <label>Course</label>
                            {!isEditingProfile ? (
                              <span className={!user?.course ? 'empty-field' : ''}>
                                {user?.course || (
                                  <span className="add-info-prompt">
                                    <Edit3 size={14} />
                                    Click edit to add course
                                  </span>
                                )}
                              </span>
                            ) : (
                              <input
                                type="text"
                                value={profileData.course}
                                onChange={(e) => handleProfileChange('course', e.target.value)}
                                className="edit-input"
                                placeholder="e.g., B.Tech Computer Science"
                              />
                            )}
                          </div>
                        </div>
                        <div className="profile-item">
                          <BookOpen size={18} />
                          <div className="item-content">
                            <label>College Name</label>
                            {!isEditingProfile ? (
                              <span className={!user?.college_name ? 'empty-field' : ''}>
                                {user?.college_name || (
                                  <span className="add-info-prompt">
                                    <Edit3 size={14} />
                                    Click edit to add college name
                                  </span>
                                )}
                              </span>
                            ) : (
                              <input
                                type="text"
                                value={profileData.college_name}
                                onChange={(e) => handleProfileChange('college_name', e.target.value)}
                                className="edit-input"
                                placeholder="Enter your college name"
                              />
                            )}
                          </div>
                        </div>
                        <div className="profile-item">
                          <TrendingUp size={18} />
                          <div className="item-content">
                            <label>Year of Study</label>
                            {!isEditingProfile ? (
                              <span className={!user?.year_of_study ? 'empty-field' : ''}>
                                {user?.year_of_study || (
                                  <span className="add-info-prompt">
                                    <Edit3 size={14} />
                                    Click edit to add year of study
                                  </span>
                                )}
                              </span>
                            ) : (
                              <select
                                value={profileData.year_of_study}
                                onChange={(e) => handleProfileChange('year_of_study', e.target.value)}
                                className="edit-input"
                              >
                                <option value="">Select Year</option>
                                <option value="1st Year">1st Year</option>
                                <option value="2nd Year">2nd Year</option>
                                <option value="3rd Year">3rd Year</option>
                                <option value="4th Year">4th Year</option>
                                <option value="Final Year">Final Year</option>
                              </select>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Statistics */}
                <div className="stats-grid">
                  <div className="stat-card">
                    <div className="stat-icon">
                      <FileText size={24} color="#FF6B35" />
                    </div>
                    <div className="stat-info">
                      <h3>{documents.length}</h3>
                      <p>Total Documents</p>
                    </div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-icon">
                      <CheckCircle size={24} color="#22c55e" />
                    </div>
                    <div className="stat-info">
                      <h3>{documents.filter(doc => doc.status === 'verified').length}</h3>
                      <p>Verified</p>
                    </div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-icon">
                      <Clock size={24} color="#f59e0b" />
                    </div>
                    <div className="stat-info">
                      <h3>{documents.filter(doc => doc.status === 'pending').length}</h3>
                      <p>Pending</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'upload' && (
              <div className="upload-tab">
                <div className="upload-header">
                  <h2>Upload Document</h2>
                  <p>Upload your academic documents for secure verification and blockchain storage</p>
                </div>

                <div className="upload-section enhanced">
                  <div 
                    className={`upload-area ${dragActive ? 'drag-active' : ''} ${duplicateFound ? 'duplicate-warning' : ''}`}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                  >
                    <div className="upload-icon">
                      <Upload size={48} color="#FF6B35" />
                    </div>
                    <h3>Drag & Drop your document here</h3>
                    <p>Supports PDF, JPG, PNG files up to 16MB</p>
                    <div className="upload-actions">
                      <input
                        type="file"
                        onChange={handleFileSelect}
                        accept=".pdf,.jpg,.jpeg,.png"
                        style={{ display: 'none' }}
                        id="file-input"
                      />
                      <label htmlFor="file-input" className="browse-btn">
                        <FileText size={18} />
                        Browse Files
                      </label>
                    </div>
                  </div>

                  {(isCheckingDuplicate || duplicateFound) && (
                    <div className="processing-status">
                      <div className="processing-content">
                        <div className="processing-spinner"></div>
                        <div className="processing-text">
                          <h4>
                            {isCheckingDuplicate ? 'Checking Documents...' : 'Processing Request...'}
                          </h4>
                          <p>
                            {isCheckingDuplicate 
                              ? 'Scanning your uploaded documents for duplicates' 
                              : 'Redirecting to My Documents section'}
                          </p>
                        </div>
                      </div>
                      <div className="processing-progress">
                        <div className="progress-dot active"></div>
                        <div className="progress-dot active"></div>
                        <div className="progress-dot"></div>
                      </div>
                    </div>
                  )}

                  {selectedFile && !duplicateFound && (
                    <div className="selected-file enhanced">
                      <FileCheck size={20} />
                      <div className="file-info">
                        <h4>{selectedFile.name}</h4>
                        <p>Size: {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</p>
                        <p>Type: {getDocumentType(selectedFile.name)}</p>
                      </div>
                      <button 
                        className="remove-file"
                        onClick={() => {
                          setSelectedFile(null);
                          setDuplicateFound(null);
                        }}
                      >
                        <X size={16} />
                      </button>
                    </div>
                  )}

                  {uploadProgress > 0 && (
                    <div className="upload-progress enhanced">
                      <div className="progress-header">
                        <span>Uploading Document...</span>
                        <span>{uploadProgress}%</span>
                      </div>
                      <div className="progress-bar">
                        <div 
                          className="progress-fill" 
                          style={{ width: `${uploadProgress}%` }}
                        ></div>
                      </div>
                      <div className="progress-stages">
                        <div className={`stage ${uploadProgress >= 10 ? 'completed' : ''}`}>
                          Preparing
                        </div>
                        <div className={`stage ${uploadProgress >= 50 ? 'completed' : ''}`}>
                          Uploading
                        </div>
                        <div className={`stage ${uploadProgress >= 80 ? 'completed' : ''}`}>
                          Processing
                        </div>
                        <div className={`stage ${uploadProgress >= 100 ? 'completed' : ''}`}>
                          Complete
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="upload-controls">
                    <button 
                      className="upload-btn enhanced"
                      onClick={handleUpload}
                      disabled={!selectedFile || uploadProgress > 0}
                    >
                      {duplicateFound ? (
                        <>
                          <Eye size={18} />
                          View My Documents
                        </>
                      ) : uploadProgress > 0 ? (
                        <>
                          <div className="button-spinner"></div>
                          Processing...
                        </>
                      ) : (
                        <>
                          <Upload size={18} />
                          Upload & Verify Document
                        </>
                      )}
                    </button>
                  </div>

                  <div className="upload-guidelines">
                    <h4>📋 Upload Guidelines</h4>
                    <ul>
                      <li>✅ Ensure document is clear and readable</li>
                      <li>✅ File size should not exceed 16MB</li>
                      <li>✅ Supported formats: PDF, JPG, PNG</li>
                      <li>✅ Original documents are preferred</li>
                      <li>🔒 All documents are encrypted and stored securely</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'documents' && (
              <div className="documents-tab enhanced">
                <div className="documents-header">
                  <div className="header-content">
                    <h2>My Documents</h2>
                    <p>Secure blockchain-verified academic credentials</p>
                  </div>
                  <div className="header-actions">
                    <button 
                      className="btn-primary"
                      onClick={() => setActiveTab('upload')}
                    >
                      <Upload size={18} />
                      Add New Document
                    </button>
                  </div>
                </div>

                {showMyDocuments && (
                  <div className="session-banner">
                    <div className="banner-content">
                      <Award size={20} />
                      <span>My Documents Session - View and manage your verified credentials</span>
                    </div>
                    <button 
                      className="close-session"
                      onClick={() => setShowMyDocuments(false)}
                    >
                      <X size={16} />
                    </button>
                  </div>
                )}

                <div className="documents-stats">
                  <div className="stat-item">
                    <div className="stat-value">{documents.length}</div>
                    <div className="stat-label">Total Documents</div>
                  </div>
                  <div className="stat-item verified">
                    <div className="stat-value">{documents.filter(doc => doc.status === 'verified').length}</div>
                    <div className="stat-label">Verified</div>
                  </div>
                  <div className="stat-item pending">
                    <div className="stat-value">{documents.filter(doc => doc.status === 'pending').length}</div>
                    <div className="stat-label">Pending</div>
                  </div>
                  <div className="stat-item rejected">
                    <div className="stat-value">{documents.filter(doc => doc.status === 'rejected').length}</div>
                    <div className="stat-label">Rejected</div>
                  </div>
                </div>

                {loading ? (
                  <div className="loading-state">
                    <div className="loading-spinner large"></div>
                    <p>Loading documents...</p>
                  </div>
                ) : documents.length === 0 ? (
                  <div className="empty-state enhanced">
                    <div className="empty-icon">
                      <FileText size={64} color="#9ca3af" />
                    </div>
                    <h3>No documents uploaded yet</h3>
                    <p>Start building your digital credential portfolio by uploading your first academic document.</p>
                    <div className="empty-actions">
                      <button 
                        className="btn-primary large"
                        onClick={() => setActiveTab('upload')}
                      >
                        <Upload size={20} />
                        Upload Your First Document
                      </button>
                    </div>
                    <div className="upload-benefits">
                      <div className="benefit">
                        <Shield size={16} />
                        <span>Blockchain Security</span>
                      </div>
                      <div className="benefit">
                        <CheckCircle size={16} />
                        <span>Instant Verification</span>
                      </div>
                      <div className="benefit">
                        <Award size={16} />
                        <span>Employer Recognition</span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="documents-grid">
                    {documents.map(doc => (
                      <div key={doc.id} className="document-card modern">
                        <div className="card-header">
                          <div className="doc-icon">
                            {doc.document_type === 'marksheet' && <BookOpen size={24} />}
                            {doc.document_type === 'certificate' && <Award size={24} />}
                            {doc.document_type === 'diploma' && <GraduationCap size={24} />}
                            {!['marksheet', 'certificate', 'diploma'].includes(doc.document_type) && <FileText size={24} />}
                          </div>
                          <div className="doc-status-badge">
                            <div className={`status-indicator ${doc.status}`}>
                              {getStatusIcon(doc.status)}
                            </div>
                          </div>
                        </div>
                        
                        <div className="card-body">
                          <h3 className="doc-title">{doc.title}</h3>
                          <p className="doc-type">{doc.document_type}</p>
                          
                          <div className="doc-metadata">
                            <div className="meta-item">
                              <Calendar size={14} />
                              <span>Uploaded: {new Date(doc.created_at).toLocaleDateString()}</span>
                            </div>
                            {doc.verification_date && (
                              <div className="meta-item">
                                <CheckCircle size={14} />
                                <span>Verified: {new Date(doc.verification_date).toLocaleDateString()}</span>
                              </div>
                            )}
                          </div>

                          {doc.verification_notes && (
                            <div className="verification-notes">
                              <p>{doc.verification_notes}</p>
                            </div>
                          )}
                          
                          <div className="blockchain-hash">
                            <Hash size={14} />
                            <span>Hash: {doc.id.substring(0, 16)}...</span>
                          </div>
                        </div>
                        
                        <div className="card-footer">
                          <div className={`status-text ${doc.status}`}>
                            {doc.status.charAt(0).toUpperCase() + doc.status.slice(1)}
                          </div>
                          <div className="card-actions">
                            <button 
                              className="action-btn view"
                              onClick={() => viewDocument(doc)}
                            >
                              <Eye size={16} />
                              View Details
                            </button>
                            <button 
                              className="action-btn share"
                              onClick={() => {
                                navigator.clipboard.writeText(doc.id);
                                toast.success('Document ID copied to clipboard!');
                              }}
                            >
                              <FileCheck size={16} />
                              Share
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </section>
        </div>
      </main>

      {/* OCR Data Modal */}
      {viewingDocument && (
        <div className="modal-overlay" onClick={closeDocumentView}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>OCR Extracted Data - {viewingDocument.title}</h3>
              <button className="modal-close" onClick={closeDocumentView}>×</button>
            </div>
            
            <div className="modal-body">
              {ocrLoading ? (
                <div className="loading-ocr">
                  <div className="loading-spinner"></div>
                  <p>Processing OCR data...</p>
                </div>
              ) : ocrData?.error ? (
                <div className="ocr-error">
                  <XCircle size={48} color="#ef4444" />
                  <h4>Error Loading OCR Data</h4>
                  <p>{ocrData.error}</p>
                </div>
              ) : ocrData?.has_ocr_data ? (
                <div className="ocr-results">
                  <div className="ocr-section">
                    <h4>Document Information</h4>
                    <div className="ocr-grid">
                      <div className="ocr-item">
                        <strong>Document Type:</strong>
                        <span>{viewingDocument.document_type}</span>
                      </div>
                      <div className="ocr-item">
                        <strong>Status:</strong>
                        <span className={`status ${viewingDocument.status}`}>
                          {viewingDocument.status}
                        </span>
                      </div>
                    </div>
                  </div>

                  {ocrData.ocr_data && (
                    <div className="ocr-section">
                      <h4>Extracted Information</h4>
                      <div className="ocr-grid">
                        {ocrData.ocr_data.university && (
                          <div className="ocr-item">
                            <strong>University:</strong>
                            <span>{ocrData.ocr_data.university}</span>
                          </div>
                        )}
                        {ocrData.ocr_data.student_name && (
                          <div className="ocr-item">
                            <strong>Student Name:</strong>
                            <span>{ocrData.ocr_data.student_name}</span>
                          </div>
                        )}
                        {ocrData.ocr_data.roll_number && (
                          <div className="ocr-item">
                            <strong>Roll Number:</strong>
                            <span>{ocrData.ocr_data.roll_number}</span>
                          </div>
                        )}
                        {ocrData.ocr_data.result && (
                          <div className="ocr-item">
                            <strong>Result:</strong>
                            <span>{ocrData.ocr_data.result}</span>
                          </div>
                        )}
                      </div>

                      {ocrData.ocr_data.subjects && ocrData.ocr_data.subjects.length > 0 && (
                        <div className="subjects-section">
                          <h5>Subjects & Marks</h5>
                          <div className="subjects-table">
                            {ocrData.ocr_data.subjects.map((subject, index) => (
                              <div key={index} className="subject-row">
                                <span className="subject-code">{subject.course_code}</span>
                                <span className="subject-title">{subject.course_title}</span>
                                <span className="subject-marks">{subject.marks}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {ocrData.extracted_text && (
                    <div className="ocr-section">
                      <h4>Extracted Text</h4>
                      <div className="extracted-text">
                        {ocrData.extracted_text}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="no-ocr-data">
                  <FileText size={48} color="#9ca3af" />
                  <h4>No OCR Data Available</h4>
                  <p>This document hasn't been processed through OCR yet, or OCR processing failed.</p>
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button className="secondary-btn" onClick={closeDocumentView}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StudentDashboard;