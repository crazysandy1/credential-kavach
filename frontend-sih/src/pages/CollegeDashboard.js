import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Users, 
  FileText, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Eye, 
  LogOut, 
  User, 
  GraduationCap,
  Building,
  Phone,
  Mail,
  MapPin,
  Search,
  Filter,
  Shield,
  Upload,
  UploadCloud,
  FileStack,
  Plus,
  X,
  AlertCircle,
  Database,
  BarChart3,
  Zap,
  Settings,
  Bell,
  Download
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import './CollegeDashboard.css';

const CollegeDashboard = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [students, setStudents] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [showVerificationModal, setShowVerificationModal] = useState(false);
  
  // Bulk upload related states
  const [showBulkUpload, setShowBulkUpload] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const [processingFiles, setProcessingFiles] = useState([]);
  const fileInputRef = useRef(null);
  
  // Profile editing state
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [editProfileData, setEditProfileData] = useState({});
  const [profileCompletion, setProfileCompletion] = useState(0);
  
  // Notification state
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    loadData();
    calculateProfileCompletion();
    loadNotifications();
  }, []);

  // Calculate profile completion
  const calculateProfileCompletion = () => {
    const fields = ['college_name', 'email', 'phone', 'address'];
    const completed = fields.filter(field => user?.[field] && user[field].trim() !== '').length;
    const percentage = Math.round((completed / fields.length) * 100);
    setProfileCompletion(percentage);
  };

  // Load notifications
  const loadNotifications = () => {
    const mockNotifications = [
      {
        id: '1',
        type: 'pending',
        title: 'New Document Pending',
        message: '3 new documents require verification',
        time: '5 minutes ago',
        unread: true
      },
      {
        id: '2',
        type: 'success',
        title: 'Bulk Upload Complete',
        message: 'Successfully processed 12 documents',
        time: '2 hours ago',
        unread: false
      }
    ];
    setNotifications(mockNotifications);
  };

  const loadData = async () => {
    try {
      // Mock data for college dashboard - Students specific to this college
      const collegeName = user?.college_name || 'National Institute of Technology';
      const mockStudents = [
        {
          id: '1',
          name: 'Raj Kumar',
          email: 'raj@student.com',
          rollNumber: 'CS001',
          course: 'Computer Science',
          semester: '6',
          college_name: collegeName,
          documentsCount: 3,
          verifiedCount: 2,
          pendingCount: 1
        },
        {
          id: '2',
          name: 'Priya Sharma',
          email: 'priya@student.com',
          rollNumber: 'CS002',
          course: 'Computer Science',
          semester: '6',
          college_name: collegeName,
          documentsCount: 4,
          verifiedCount: 3,
          pendingCount: 1
        },
        {
          id: '3',
          name: 'Amit Singh',
          email: 'amit@student.com',
          rollNumber: 'EE001',
          course: 'Electrical Engineering',
          semester: '8',
          college_name: collegeName,
          documentsCount: 5,
          verifiedCount: 4,
          pendingCount: 1
        },
        {
          id: '4',
          name: 'Sneha Patel',
          email: 'sneha@student.com',
          rollNumber: 'ME001',
          course: 'Mechanical Engineering',
          semester: '4',
          college_name: collegeName,
          documentsCount: 2,
          verifiedCount: 1,
          pendingCount: 1
        },
        {
          id: '5',
          name: 'Rohit Gupta',
          email: 'rohit@student.com',
          rollNumber: 'CE001',
          course: 'Civil Engineering',
          semester: '2',
          college_name: collegeName,
          documentsCount: 3,
          verifiedCount: 2,
          pendingCount: 1
        }
      ];

      const mockDocuments = [
        {
          id: '1',
          studentName: 'Raj Kumar',
          rollNumber: 'CS001',
          college_name: collegeName,
          title: '10th Marksheet',
          document_type: 'marksheet',
          status: 'pending',
          created_at: '2024-01-15T10:30:00Z',
          uploaded_by: '1'
        },
        {
          id: '2',
          studentName: 'Priya Sharma',
          rollNumber: 'CS002',
          college_name: collegeName,
          title: '12th Certificate',
          document_type: 'certificate',
          status: 'pending',
          created_at: '2024-01-20T09:15:00Z',
          uploaded_by: '2'
        },
        {
          id: '3',
          studentName: 'Amit Singh',
          rollNumber: 'EE001',
          college_name: collegeName,
          title: 'Graduation Certificate',
          document_type: 'certificate',
          status: 'verified',
          created_at: '2024-01-25T16:45:00Z',
          verification_date: '2024-01-26T10:20:00Z',
          verified_by: user?.id,
          verification_notes: 'Document verified successfully',
          uploaded_by: '3'
        },
        {
          id: '4',
          studentName: 'Sneha Patel',
          rollNumber: 'ME001',
          college_name: collegeName,
          title: 'Transfer Certificate',
          document_type: 'certificate',
          status: 'pending',
          created_at: '2024-01-28T11:30:00Z',
          uploaded_by: '4'
        },
        {
          id: '5',
          studentName: 'Rohit Gupta',
          rollNumber: 'CE001',
          college_name: collegeName,
          title: 'Character Certificate',
          document_type: 'certificate',
          status: 'verified',
          created_at: '2024-01-29T14:15:00Z',
          verification_date: '2024-01-30T09:45:00Z',
          verified_by: user?.id,
          verification_notes: 'All details verified and approved',
          uploaded_by: '5'
        }
      ];

      setStudents(mockStudents);
      setDocuments(mockDocuments);
      setLoading(false);
    } catch (error) {
      console.error('Error loading data:', error);
      setLoading(false);
    }
  };

  // Bulk upload functionality
  const handleFileSelect = (files) => {
    const fileArray = Array.from(files);
    const validFiles = fileArray.filter(file => {
      const isValidType = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'].includes(file.type);
      const isValidSize = file.size <= 10 * 1024 * 1024; // 10MB limit
      
      if (!isValidType) {
        toast.error(`${file.name}: Only PDF and image files are allowed`);
        return false;
      }
      
      if (!isValidSize) {
        toast.error(`${file.name}: File size must be less than 10MB`);
        return false;
      }
      
      return true;
    });

    if (validFiles.length > 0) {
      setSelectedFiles(prev => [...prev, ...validFiles]);
      toast.success(`${validFiles.length} files selected for upload`);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = e.dataTransfer.files;
    handleFileSelect(files);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const removeFile = (index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const checkForDuplicates = async (file) => {
    // Simulate duplicate detection
    const existingFiles = ['existing_document_1.pdf', 'student_marksheet.pdf'];
    return existingFiles.includes(file.name);
  };

  const processBulkUpload = async () => {
    if (selectedFiles.length === 0) {
      toast.error('Please select files to upload');
      return;
    }

    setProcessingFiles(selectedFiles.map(file => ({
      name: file.name,
      status: 'processing',
      progress: 0
    })));

    for (let i = 0; i < selectedFiles.length; i++) {
      const file = selectedFiles[i];
      
      try {
        // Check for duplicates
        const isDuplicate = await checkForDuplicates(file);
        
        if (isDuplicate) {
          setProcessingFiles(prev => 
            prev.map((pf, index) => 
              index === i 
                ? { ...pf, status: 'duplicate', message: 'Document already exists in system' }
                : pf
            )
          );
          
          toast(`${file.name} already exists`, {
            icon: '⚠️',
            style: {
              borderRadius: '10px',
              background: '#fff3cd',
              color: '#856404',
              border: '1px solid #ffeaa7'
            }
          });
          continue;
        }

        // Simulate upload progress
        for (let progress = 0; progress <= 100; progress += 20) {
          setProcessingFiles(prev => 
            prev.map((pf, index) => 
              index === i 
                ? { ...pf, progress: progress }
                : pf
            )
          );
          await new Promise(resolve => setTimeout(resolve, 200));
        }

        // Mark as completed
        setProcessingFiles(prev => 
          prev.map((pf, index) => 
            index === i 
              ? { ...pf, status: 'completed', message: 'Successfully uploaded and processed' }
              : pf
          )
        );

        // Add to documents list
        const newDoc = {
          id: `bulk_${Date.now()}_${i}`,
          studentName: 'Bulk Upload',
          rollNumber: 'BULK',
          college_name: user?.college_name,
          title: file.name,
          document_type: file.name.includes('marksheet') ? 'marksheet' : 'certificate',
          status: 'pending',
          created_at: new Date().toISOString(),
          uploaded_by: 'bulk'
        };

        setDocuments(prev => [newDoc, ...prev]);

      } catch (error) {
        setProcessingFiles(prev => 
          prev.map((pf, index) => 
            index === i 
              ? { ...pf, status: 'error', message: 'Upload failed' }
              : pf
          )
        );
      }
    }

    toast.success('Bulk upload completed!');
    
    // Clear after 3 seconds
    setTimeout(() => {
      setSelectedFiles([]);
      setProcessingFiles([]);
      setShowBulkUpload(false);
    }, 3000);
  };

  // Profile editing functions
  const handleProfileEdit = () => {
    setEditProfileData({
      college_name: user?.college_name || '',
      email: user?.email || '',
      phone: user?.phone || '',
      address: user?.address || ''
    });
    setIsEditingProfile(true);
  };

  const handleProfileSave = () => {
    // Here you would typically save to backend
    toast.success('Profile updated successfully!');
    setIsEditingProfile(false);
    calculateProfileCompletion();
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handleVerifyDocument = async (doc, action, notes = '') => {
    try {
      // Mock verification process
      const updatedDocuments = documents.map(document => {
        if (document.id === doc.id) {
          return {
            ...document,
            status: action,
            verification_date: new Date().toISOString(),
            verified_by: user?.id,
            verification_notes: notes
          };
        }
        return document;
      });

      setDocuments(updatedDocuments);
      setShowVerificationModal(false);
      setSelectedDocument(null);
    } catch (error) {
      console.error('Error verifying document:', error);
    }
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
        return <CheckCircle size={16} color="#22c55e" />;
      case 'pending':
        return <Clock size={16} color="#f59e0b" />;
      case 'rejected':
        return <XCircle size={16} color="#ef4444" />;
      default:
        return <FileText size={16} color="#6b7280" />;
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

  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = doc.studentName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.rollNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.title.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter = filterStatus === 'all' || doc.status === filterStatus;
    
    return matchesSearch && matchesFilter;
  });

  const stats = {
    totalStudents: students.length,
    totalDocuments: documents.length,
    pendingDocuments: documents.filter(doc => doc.status === 'pending').length,
    verifiedDocuments: documents.filter(doc => doc.status === 'verified').length,
    rejectedDocuments: documents.filter(doc => doc.status === 'rejected').length
  };

  return (
    <div className="college-dashboard">
      {/* Enhanced Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <div className="header-left">
            <div className="logo-section">
              <div className="logo-icon">
                <Building size={32} />
              </div>
              <div className="logo-text">
                <h1>College Dashboard</h1>
                <p>New India Credential Kavach</p>
              </div>
            </div>
          </div>
          <div className="header-right">
            <div className="header-notifications">
              <div className="notification-bell">
                <Bell size={20} />
                {notifications.filter(n => n.unread).length > 0 && (
                  <span className="notification-badge">
                    {notifications.filter(n => n.unread).length}
                  </span>
                )}
              </div>
            </div>
            <div className="user-info">
              <div className="user-avatar">
                <Building size={20} />
              </div>
              <div className="user-details">
                <span className="user-name">{user?.college_name || 'College Admin'}</span>
                <span className="user-role">Administrator</span>
              </div>
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
          <aside className="dashboard-sidebar">
            <nav className="sidebar-nav">
              <button 
                className={`nav-item ${activeTab === 'overview' ? 'active' : ''}`}
                onClick={() => setActiveTab('overview')}
              >
                <div className="nav-icon">
                  <BarChart3 size={18} />
                </div>
                <span>Overview</span>
              </button>
              <button 
                className={`nav-item ${activeTab === 'students' ? 'active' : ''}`}
                onClick={() => setActiveTab('students')}
              >
                <div className="nav-icon">
                  <Users size={18} />
                </div>
                <span>Students</span>
              </button>
              <button 
                className={`nav-item ${activeTab === 'documents' ? 'active' : ''}`}
                onClick={() => setActiveTab('documents')}
              >
                <div className="nav-icon">
                  <FileText size={18} />
                </div>
                <span>Document Verification</span>
                {stats.pendingDocuments > 0 && (
                  <div className="nav-badge">{stats.pendingDocuments}</div>
                )}
              </button>
              <button 
                className={`nav-item ${activeTab === 'bulk-upload' ? 'active' : ''}`}
                onClick={() => setActiveTab('bulk-upload')}
              >
                <div className="nav-icon">
                  <UploadCloud size={18} />
                </div>
                <span>Bulk Upload</span>
              </button>
            </nav>
            
            <div className="sidebar-footer">
              <div className="quick-stats">
                <div className="quick-stat">
                  <Database size={16} />
                  <div>
                    <span className="stat-number">{stats.totalDocuments}</span>
                    <span className="stat-label">Total Documents</span>
                  </div>
                </div>
                <div className="quick-stat">
                  <Zap size={16} />
                  <div>
                    <span className="stat-number">{stats.verifiedDocuments}</span>
                    <span className="stat-label">Verified Today</span>
                  </div>
                </div>
              </div>
            </div>
          </aside>

          {/* Content Area */}
          <section className="dashboard-content">
            {activeTab === 'overview' && (
              <div className="overview-tab">
                <div className="welcome-section">
                  <div className="welcome-content">
                    <h2>Welcome back, {user?.college_name || 'College Admin'}!</h2>
                    <p className="welcome-subtitle">Manage your institution's document verification efficiently</p>
                  </div>
                  <div className="welcome-actions">
                    <button 
                      className="action-btn primary"
                      onClick={() => setActiveTab('bulk-upload')}
                    >
                      <UploadCloud size={18} />
                      Bulk Upload
                    </button>
                  </div>
                </div>

                {/* Enhanced Profile Card */}
                <div className="enhanced-profile-card">
                  <div className="profile-header">
                    <div className="profile-title">
                      <h3>College Information</h3>
                      <div className="profile-completion">
                        <div className="completion-circle">
                          <svg className="completion-ring" width="40" height="40">
                            <circle 
                              cx="20" 
                              cy="20" 
                              r="16" 
                              fill="none" 
                              stroke="#e2e8f0" 
                              strokeWidth="3"
                            />
                            <circle 
                              cx="20" 
                              cy="20" 
                              r="16" 
                              fill="none" 
                              stroke="#22c55e" 
                              strokeWidth="3" 
                              strokeDasharray={`${profileCompletion * 1.005} 100`}
                              strokeLinecap="round"
                              transform="rotate(-90 20 20)"
                            />
                          </svg>
                          <span className="completion-text">{profileCompletion}%</span>
                        </div>
                        <span className="completion-label">Complete</span>
                      </div>
                    </div>
                    <button 
                      className="edit-profile-btn"
                      onClick={handleProfileEdit}
                    >
                      <Settings size={16} />
                      Edit Profile
                    </button>
                  </div>

                  {!isEditingProfile ? (
                    <div className="profile-grid">
                      <div className="profile-item">
                        <div className="profile-icon">
                          <Building size={18} />
                        </div>
                        <div className="profile-content">
                          <label>College Name</label>
                          {user?.college_name ? (
                            <span>{user.college_name}</span>
                          ) : (
                            <span className="empty-field" onClick={handleProfileEdit}>
                              Click to add college name
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="profile-item">
                        <div className="profile-icon">
                          <Mail size={18} />
                        </div>
                        <div className="profile-content">
                          <label>Email</label>
                          <span>{user?.email}</span>
                        </div>
                      </div>
                      <div className="profile-item">
                        <div className="profile-icon">
                          <Phone size={18} />
                        </div>
                        <div className="profile-content">
                          <label>Phone</label>
                          {user?.phone ? (
                            <span>{user.phone}</span>
                          ) : (
                            <span className="empty-field" onClick={handleProfileEdit}>
                              Click to add phone number
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="profile-item">
                        <div className="profile-icon">
                          <MapPin size={18} />
                        </div>
                        <div className="profile-content">
                          <label>Address</label>
                          {user?.address ? (
                            <span>{user.address}</span>
                          ) : (
                            <span className="empty-field" onClick={handleProfileEdit}>
                              Click to add address
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="profile-edit-form">
                      <div className="edit-grid">
                        <div className="edit-field">
                          <label>College Name</label>
                          <input
                            type="text"
                            value={editProfileData.college_name}
                            onChange={(e) => setEditProfileData({...editProfileData, college_name: e.target.value})}
                            placeholder="Enter college name"
                          />
                        </div>
                        <div className="edit-field">
                          <label>Email</label>
                          <input
                            type="email"
                            value={editProfileData.email}
                            onChange={(e) => setEditProfileData({...editProfileData, email: e.target.value})}
                            placeholder="Enter email"
                          />
                        </div>
                        <div className="edit-field">
                          <label>Phone</label>
                          <input
                            type="tel"
                            value={editProfileData.phone}
                            onChange={(e) => setEditProfileData({...editProfileData, phone: e.target.value})}
                            placeholder="Enter phone number"
                          />
                        </div>
                        <div className="edit-field">
                          <label>Address</label>
                          <textarea
                            value={editProfileData.address}
                            onChange={(e) => setEditProfileData({...editProfileData, address: e.target.value})}
                            placeholder="Enter address"
                            rows="3"
                          />
                        </div>
                      </div>
                      <div className="edit-actions">
                        <button className="save-btn" onClick={handleProfileSave}>
                          <CheckCircle size={16} />
                          Save Changes
                        </button>
                        <button className="cancel-btn" onClick={() => setIsEditingProfile(false)}>
                          <X size={16} />
                          Cancel
                        </button>
                      </div>
                    </div>
                  )}
                </div>

                {/* Statistics */}
                <div className="stats-grid">
                  <div className="stat-card">
                    <div className="stat-icon">
                      <Users size={24} color="#FF6B35" />
                    </div>
                    <div className="stat-info">
                      <h3>{stats.totalStudents}</h3>
                      <p>Total Students</p>
                    </div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-icon">
                      <FileText size={24} color="#3b82f6" />
                    </div>
                    <div className="stat-info">
                      <h3>{stats.totalDocuments}</h3>
                      <p>Total Documents</p>
                    </div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-icon">
                      <Clock size={24} color="#f59e0b" />
                    </div>
                    <div className="stat-info">
                      <h3>{stats.pendingDocuments}</h3>
                      <p>Pending Verification</p>
                    </div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-icon">
                      <CheckCircle size={24} color="#22c55e" />
                    </div>
                    <div className="stat-info">
                      <h3>{stats.verifiedDocuments}</h3>
                      <p>Verified</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'students' && (
              <div className="students-tab">
                <h2>Student Management</h2>
                <p>Manage students and their document verification status</p>

                {loading ? (
                  <div className="loading">Loading students...</div>
                ) : (
                  <div className="students-list">
                    {students.map(student => (
                      <div key={student.id} className="student-card">
                        <div className="student-header">
                          <div className="student-info">
                            <div className="student-avatar">
                              <GraduationCap size={24} color="#FF6B35" />
                            </div>
                            <div>
                              <h3>{student.name}</h3>
                              <p>{student.rollNumber} • {student.course}</p>
                              <p className="semester">Semester {student.semester}</p>
                            </div>
                          </div>
                          <div className="student-contact">
                            <p>{student.email}</p>
                          </div>
                        </div>
                        <div className="student-stats">
                          <div className="stat-item">
                            <FileText size={16} />
                            <span>{student.documentsCount} Documents</span>
                          </div>
                          <div className="stat-item">
                            <CheckCircle size={16} color="#22c55e" />
                            <span>{student.verifiedCount} Verified</span>
                          </div>
                          <div className="stat-item">
                            <Clock size={16} color="#f59e0b" />
                            <span>{student.pendingCount} Pending</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'documents' && (
              <div className="documents-tab">
                <div className="documents-header">
                  <div>
                    <h2>Document Verification</h2>
                    <p>Review and verify student documents</p>
                  </div>
                  <div className="documents-controls">
                    <div className="search-box">
                      <Search size={16} />
                      <input
                        type="text"
                        placeholder="Search documents..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                      />
                    </div>
                    <select
                      value={filterStatus}
                      onChange={(e) => setFilterStatus(e.target.value)}
                      className="filter-select"
                    >
                      <option value="all">All Status</option>
                      <option value="pending">Pending</option>
                      <option value="verified">Verified</option>
                      <option value="rejected">Rejected</option>
                    </select>
                  </div>
                </div>

                {loading ? (
                  <div className="loading">Loading documents...</div>
                ) : filteredDocuments.length === 0 ? (
                  <div className="empty-state">
                    <FileText size={48} color="#9ca3af" />
                    <h3>No documents found</h3>
                    <p>No documents match your current filter criteria</p>
                  </div>
                ) : (
                  <div className="documents-list">
                    {filteredDocuments.map(doc => (
                      <div key={doc.id} className="document-card">
                        <div className="doc-header">
                          <div className="doc-title">
                            <FileText size={20} />
                            <div>
                              <h3>{doc.title}</h3>
                              <p>{doc.studentName} • {doc.rollNumber}</p>
                            </div>
                          </div>
                          <div className="doc-status">
                            {getStatusIcon(doc.status)}
                            <span style={{ color: getStatusColor(doc.status) }}>
                              {doc.status.charAt(0).toUpperCase() + doc.status.slice(1)}
                            </span>
                          </div>
                        </div>
                        <div className="doc-details">
                          <div className="doc-meta">
                            <span>Type: {doc.document_type}</span>
                            <span>Uploaded: {formatDate(doc.created_at)}</span>
                            {doc.verification_date && (
                              <span>Verified: {formatDate(doc.verification_date)}</span>
                            )}
                          </div>
                          {doc.verification_notes && (
                            <div className="doc-notes">
                              <strong>Notes:</strong> {doc.verification_notes}
                            </div>
                          )}
                        </div>
                        <div className="doc-actions">
                          <button 
                            className="action-btn view-btn"
                            onClick={() => {
                              setSelectedDocument(doc);
                              setShowVerificationModal(true);
                            }}
                          >
                            <Eye size={16} />
                            {doc.status === 'pending' ? 'Review' : 'View'}
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'bulk-upload' && (
              <div className="bulk-upload-tab">
                <div className="tab-header">
                  <div>
                    <h2>Bulk Document Upload</h2>
                    <p>Upload multiple documents for batch processing</p>
                  </div>
                  <div className="bulk-stats">
                    <div className="bulk-stat">
                      <FileStack size={20} />
                      <span>{selectedFiles.length} files selected</span>
                    </div>
                  </div>
                </div>

                {/* File Upload Area */}
                <div 
                  className={`bulk-upload-area ${isDragOver ? 'drag-over' : ''}`}
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept=".pdf,.jpg,.jpeg,.png"
                    onChange={(e) => handleFileSelect(e.target.files)}
                    style={{ display: 'none' }}
                  />
                  
                  <div className="upload-content">
                    <div className="upload-icon">
                      <UploadCloud size={48} />
                    </div>
                    <h3>Drag & Drop files here</h3>
                    <p>or click to browse files</p>
                    <div className="upload-info">
                      <span>Supported formats: PDF, JPG, PNG</span>
                      <span>Maximum file size: 10MB</span>
                    </div>
                  </div>
                </div>

                {/* Selected Files */}
                {selectedFiles.length > 0 && (
                  <div className="selected-files-section">
                    <div className="section-header">
                      <h3>Selected Files ({selectedFiles.length})</h3>
                      <button 
                        className="clear-all-btn"
                        onClick={() => setSelectedFiles([])}
                      >
                        <X size={16} />
                        Clear All
                      </button>
                    </div>
                    
                    <div className="selected-files">
                      {selectedFiles.map((file, index) => (
                        <div key={index} className="file-item">
                          <div className="file-info">
                            <FileText size={20} />
                            <div className="file-details">
                              <span className="file-name">{file.name}</span>
                              <span className="file-size">
                                {(file.size / 1024 / 1024).toFixed(2)} MB
                              </span>
                            </div>
                          </div>
                          <button 
                            className="remove-file-btn"
                            onClick={() => removeFile(index)}
                          >
                            <X size={16} />
                          </button>
                        </div>
                      ))}
                    </div>

                    <div className="upload-actions">
                      <button 
                        className="upload-btn"
                        onClick={processBulkUpload}
                        disabled={processingFiles.length > 0}
                      >
                        <Upload size={16} />
                        {processingFiles.length > 0 ? 'Processing...' : 'Start Upload'}
                      </button>
                    </div>
                  </div>
                )}

                {/* Processing Status */}
                {processingFiles.length > 0 && (
                  <div className="processing-section">
                    <h3>Processing Files</h3>
                    <div className="processing-files">
                      {processingFiles.map((file, index) => (
                        <div key={index} className={`processing-item ${file.status}`}>
                          <div className="processing-info">
                            <FileText size={18} />
                            <div className="processing-details">
                              <span className="processing-name">{file.name}</span>
                              {file.message && (
                                <span className="processing-message">{file.message}</span>
                              )}
                            </div>
                          </div>
                          
                          <div className="processing-status">
                            {file.status === 'processing' && (
                              <div className="progress-indicator">
                                <div className="progress-bar">
                                  <div 
                                    className="progress-fill" 
                                    style={{ width: `${file.progress}%` }}
                                  />
                                </div>
                                <span>{file.progress}%</span>
                              </div>
                            )}
                            {file.status === 'completed' && (
                              <CheckCircle size={20} className="status-completed" />
                            )}
                            {file.status === 'duplicate' && (
                              <AlertCircle size={20} className="status-duplicate" />
                            )}
                            {file.status === 'error' && (
                              <XCircle size={20} className="status-error" />
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Upload Guidelines */}
                <div className="upload-guidelines">
                  <h4>Upload Guidelines</h4>
                  <div className="guidelines-grid">
                    <div className="guideline">
                      <CheckCircle size={16} />
                      <span>Ensure documents are clear and readable</span>
                    </div>
                    <div className="guideline">
                      <CheckCircle size={16} />
                      <span>Use descriptive filenames for easy identification</span>
                    </div>
                    <div className="guideline">
                      <CheckCircle size={16} />
                      <span>Group similar document types together</span>
                    </div>
                    <div className="guideline">
                      <CheckCircle size={16} />
                      <span>Verify document authenticity before upload</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </section>
        </div>
      </main>

      {/* Verification Modal */}
      {showVerificationModal && selectedDocument && (
        <div className="modal-overlay" onClick={() => setShowVerificationModal(false)}>
          <div className="modal-content verification-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Document Verification</h3>
              <button
                onClick={() => setShowVerificationModal(false)}
                className="close-btn"
              >
                ×
              </button>
            </div>

            <div className="verification-content">
              <div className="document-info">
                <h4>Document Information</h4>
                <div className="info-grid">
                  <div><strong>Student:</strong> {selectedDocument.studentName}</div>
                  <div><strong>Roll Number:</strong> {selectedDocument.rollNumber}</div>
                  <div><strong>Document:</strong> {selectedDocument.title}</div>
                  <div><strong>Type:</strong> {selectedDocument.document_type}</div>
                  <div><strong>Uploaded:</strong> {formatDate(selectedDocument.created_at)}</div>
                  <div><strong>Current Status:</strong> 
                    <span style={{ color: getStatusColor(selectedDocument.status) }}>
                      {selectedDocument.status.charAt(0).toUpperCase() + selectedDocument.status.slice(1)}
                    </span>
                  </div>
                </div>
              </div>

              {selectedDocument.status === 'pending' && (
                <div className="verification-actions">
                  <h4>Verification Actions</h4>
                  <div className="action-buttons">
                    <button
                      className="verify-btn approve"
                      onClick={() => handleVerifyDocument(selectedDocument, 'verified', 'Document verified successfully')}
                    >
                      <CheckCircle size={16} />
                      Approve Document
                    </button>
                    <button
                      className="verify-btn reject"
                      onClick={() => handleVerifyDocument(selectedDocument, 'rejected', 'Document rejected due to quality issues')}
                    >
                      <XCircle size={16} />
                      Reject Document
                    </button>
                  </div>
                  <div className="notes-section">
                    <label>Verification Notes (Optional)</label>
                    <textarea
                      placeholder="Add notes about this verification..."
                      rows={3}
                    />
                  </div>
                </div>
              )}

              {selectedDocument.verification_notes && (
                <div className="existing-notes">
                  <h4>Verification Notes</h4>
                  <p>{selectedDocument.verification_notes}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CollegeDashboard;