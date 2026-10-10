import React, { useState, useEffect } from 'react';
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
  Building2,
  Shield,
  Phone,
  Mail,
  MapPin,
  Search,
  Filter,
  Settings,
  BarChart3,
  Activity,
  Database,
  TrendingUp,
  Globe,
  Zap,
  AlertTriangle,
  Monitor,
  Server,
  Crown,
  Bell,
  Gauge,
  Target
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import './GovernmentDashboard.css';

const GovernmentDashboard = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [colleges, setColleges] = useState([]);
  const [students, setStudents] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [selectedCollege, setSelectedCollege] = useState(null);
  const [showCollegeModal, setShowCollegeModal] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      // Mock data for government dashboard
      const mockColleges = [
        {
          id: '1',
          name: 'National Institute of Technology',
          code: 'NIT001',
          address: 'College Street, Academic City',
          university: 'Central University',
          contact_email: 'admin@nit.edu',
          contact_phone: '9876543210',
          admin_name: 'Dr. Admin',
          studentsCount: 1250,
          documentsCount: 3750,
          verifiedCount: 3200,
          pendingCount: 450,
          rejectedCount: 100,
          is_approved: true,
          is_active: true,
          created_at: '2024-01-10T09:00:00Z'
        },
        {
          id: '2',
          name: 'Government Engineering College',
          code: 'GEC001',
          address: 'Engineering Road, Tech Hub',
          university: 'State Technical University',
          contact_email: 'office@gec.edu',
          contact_phone: '9876543211',
          admin_name: 'Prof. Director',
          studentsCount: 800,
          documentsCount: 2400,
          verifiedCount: 2100,
          pendingCount: 250,
          rejectedCount: 50,
          is_approved: true,
          is_active: true,
          created_at: '2024-01-15T10:30:00Z'
        },
        {
          id: '3',
          name: 'Regional Technical Institute',
          code: 'RTI001',
          address: 'Innovation Campus, New City',
          university: 'Regional University',
          contact_email: 'info@rti.edu',
          contact_phone: '9876543212',
          admin_name: 'Dr. Principal',
          studentsCount: 600,
          documentsCount: 1800,
          verifiedCount: 1500,
          pendingCount: 200,
          rejectedCount: 100,
          is_approved: false,
          is_active: true,
          created_at: '2024-01-20T14:15:00Z'
        }
      ];

      const mockStudents = [
        {
          id: '1',
          name: 'Raj Kumar',
          email: 'raj@student.com',
          rollNumber: 'CS001',
          course: 'Computer Science',
          semester: '6',
          college_name: 'National Institute of Technology',
          college_id: '1',
          documentsCount: 3,
          verifiedCount: 2,
          pendingCount: 1,
          created_at: '2024-01-25T11:00:00Z'
        },
        {
          id: '2',
          name: 'Priya Sharma',
          email: 'priya@student.com',
          rollNumber: 'CS002',
          course: 'Computer Science',
          semester: '6',
          college_name: 'National Institute of Technology',
          college_id: '1',
          documentsCount: 4,
          verifiedCount: 3,
          pendingCount: 1,
          created_at: '2024-01-26T09:30:00Z'
        },
        {
          id: '3',
          name: 'Amit Singh',
          email: 'amit@student.com',
          rollNumber: 'EE001',
          course: 'Electrical Engineering',
          semester: '8',
          college_name: 'Government Engineering College',
          college_id: '2',
          documentsCount: 5,
          verifiedCount: 4,
          pendingCount: 1,
          created_at: '2024-01-27T15:20:00Z'
        }
      ];

      const mockDocuments = [
        {
          id: '1',
          studentName: 'Raj Kumar',
          rollNumber: 'CS001',
          college_name: 'National Institute of Technology',
          title: '10th Marksheet',
          document_type: 'marksheet',
          status: 'pending',
          created_at: '2024-01-28T10:30:00Z',
          uploaded_by: '1'
        },
        {
          id: '2',
          studentName: 'Priya Sharma',
          rollNumber: 'CS002',
          college_name: 'National Institute of Technology',
          title: '12th Certificate',
          document_type: 'certificate',
          status: 'verified',
          created_at: '2024-01-29T09:15:00Z',
          verification_date: '2024-01-30T14:20:00Z',
          uploaded_by: '2'
        }
      ];

      setColleges(mockColleges);
      setStudents(mockStudents);
      setDocuments(mockDocuments);
      setLoading(false);
    } catch (error) {
      console.error('Error loading data:', error);
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handleApproveCollege = (collegeId) => {
    setColleges(colleges.map(college => 
      college.id === collegeId 
        ? { ...college, is_approved: true }
        : college
    ));
  };

  const handleSuspendCollege = (collegeId) => {
    setColleges(colleges.map(college => 
      college.id === collegeId 
        ? { ...college, is_active: false }
        : college
    ));
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

  const filteredColleges = colleges.filter(college => 
    college.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    college.code.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredStudents = students.filter(student => 
    student.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    student.rollNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
    student.college_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const systemStats = {
    totalColleges: colleges.length,
    approvedColleges: colleges.filter(c => c.is_approved).length,
    pendingColleges: colleges.filter(c => !c.is_approved).length,
    totalStudents: students.length,
    totalDocuments: documents.length,
    verifiedDocuments: documents.filter(d => d.status === 'verified').length,
    pendingDocuments: documents.filter(d => d.status === 'pending').length
  };

  return (
    <div className="government-dashboard">
      {/* Enhanced Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <div className="header-left">
            <div className="logo-section">
              <div className="logo-icon">
                <Crown size={32} />
              </div>
              <div className="logo-text">
                <h1>Government Dashboard</h1>
                <p>New India Credential Kavach - Administrative Control</p>
              </div>
            </div>
          </div>
          <div className="header-right">
            <div className="header-notifications">
              <div className="notification-bell">
                <Bell size={20} />
                <span className="notification-badge">3</span>
              </div>
            </div>
            <div className="system-status">
              <div className="status-indicator">
                <div className="status-dot success"></div>
                <span>All Systems Operational</span>
              </div>
            </div>
            <div className="user-info">
              <div className="user-avatar">
                <Shield size={20} />
              </div>
              <div className="user-details">
                <span className="user-name">
                  {user?.email === 'admin@credentialkavach.gov.in' 
                    ? 'System Administrator' 
                    : user?.full_name || 'Government Official'
                  }
                </span>
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
          {/* Sidebar */}
          <aside className="dashboard-sidebar">
            <nav className="sidebar-nav">
              <button 
                className={`nav-item ${activeTab === 'overview' ? 'active' : ''}`}
                onClick={() => setActiveTab('overview')}
              >
                <BarChart3 size={18} />
                Overview
              </button>
              <button 
                className={`nav-item ${activeTab === 'colleges' ? 'active' : ''}`}
                onClick={() => setActiveTab('colleges')}
              >
                <Building2 size={18} />
                Colleges Management
              </button>
              <button 
                className={`nav-item ${activeTab === 'students' ? 'active' : ''}`}
                onClick={() => setActiveTab('students')}
              >
                <Users size={18} />
                Students Overview
              </button>
              <button 
                className={`nav-item ${activeTab === 'documents' ? 'active' : ''}`}
                onClick={() => setActiveTab('documents')}
              >
                <FileText size={18} />
                System Monitoring
              </button>
            </nav>
          </aside>

          {/* Content Area */}
          <section className="dashboard-content">
            {activeTab === 'overview' && (
              <div className="overview-tab">
                {/* Enhanced Welcome Section */}
                <div className="welcome-section">
                  <div className="welcome-content">
                    <h2>National Credential System Dashboard</h2>
                    <p className="welcome-subtitle">Real-time monitoring and control of India's digital credential verification infrastructure</p>
                  </div>
                  <div className="welcome-actions">
                    <button className="action-btn primary">
                      <TrendingUp size={18} />
                      View Analytics
                    </button>
                    <button className="action-btn secondary">
                      <Settings size={18} />
                      System Settings
                    </button>
                  </div>
                </div>

                {/* Critical Metrics Dashboard */}
                <div className="critical-metrics">
                  <h3>Critical System Metrics</h3>
                  <div className="metrics-row">
                    <div className="metric-card primary">
                      <div className="metric-header">
                        <div className="metric-icon">
                          <Globe size={24} />
                        </div>
                        <span className="metric-trend up">+12.5%</span>
                      </div>
                      <div className="metric-data">
                        <span className="metric-number">{systemStats.totalDocuments.toLocaleString()}</span>
                        <span className="metric-label">Documents Verified</span>
                      </div>
                    </div>
                    
                    <div className="metric-card success">
                      <div className="metric-header">
                        <div className="metric-icon">
                          <CheckCircle size={24} />
                        </div>
                        <span className="metric-trend up">+8.2%</span>
                      </div>
                      <div className="metric-data">
                        <span className="metric-number">84.5%</span>
                        <span className="metric-label">OCR Accuracy</span>
                      </div>
                    </div>

                    <div className="metric-card warning">
                      <div className="metric-header">
                        <div className="metric-icon">
                          <Clock size={24} />
                        </div>
                        <span className="metric-trend down">-15.3%</span>
                      </div>
                      <div className="metric-data">
                        <span className="metric-number">{systemStats.pendingDocuments}</span>
                        <span className="metric-label">Pending Reviews</span>
                      </div>
                    </div>

                    <div className="metric-card info">
                      <div className="metric-header">
                        <div className="metric-icon">
                          <Building2 size={24} />
                        </div>
                        <span className="metric-trend up">+2</span>
                      </div>
                      <div className="metric-data">
                        <span className="metric-number">{systemStats.totalColleges}</span>
                        <span className="metric-label">Active Institutions</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* System Statistics */}
                <div className="stats-grid">
                  <div className="stat-card">
                    <div className="stat-icon">
                      <Building2 size={24} color="#1e3a8a" />
                    </div>
                    <div className="stat-info">
                      <h3>{systemStats.totalColleges}</h3>
                      <p>Total Colleges</p>
                    </div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-icon">
                      <CheckCircle size={24} color="#22c55e" />
                    </div>
                    <div className="stat-info">
                      <h3>{systemStats.approvedColleges}</h3>
                      <p>Approved Colleges</p>
                    </div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-icon">
                      <Users size={24} color="#8b5cf6" />
                    </div>
                    <div className="stat-info">
                      <h3>{systemStats.totalStudents}</h3>
                      <p>Total Students</p>
                    </div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-icon">
                      <FileText size={24} color="#f59e0b" />
                    </div>
                    <div className="stat-info">
                      <h3>{systemStats.totalDocuments}</h3>
                      <p>Total Documents</p>
                    </div>
                  </div>
                </div>

                {/* Enhanced System Performance Card */}
                <div className="enhanced-performance-card">
                  <div className="performance-header">
                    <div className="performance-title">
                      <h3>System Performance</h3>
                      <div className="performance-indicator">
                        <div className="status-dot success"></div>
                        <span>Optimal</span>
                      </div>
                    </div>
                    <div className="performance-actions">
                      <button className="action-btn secondary">
                        <Monitor size={16} />
                        View Details
                      </button>
                    </div>
                  </div>

                  <div className="performance-metrics">
                    <div className="metric-item">
                      <div className="metric-icon">
                        <Gauge size={20} />
                      </div>
                      <div className="metric-info">
                        <span className="metric-value">84.5%</span>
                        <span className="metric-label">OCR Accuracy</span>
                      </div>
                    </div>
                    <div className="metric-item">
                      <div className="metric-icon">
                        <Server size={20} />
                      </div>
                      <div className="metric-info">
                        <span className="metric-value">99.9%</span>
                        <span className="metric-label">Uptime</span>
                      </div>
                    </div>
                    <div className="metric-item">
                      <div className="metric-icon">
                        <Zap size={20} />
                      </div>
                      <div className="metric-info">
                        <span className="metric-value">2.3s</span>
                        <span className="metric-label">Avg Response</span>
                      </div>
                    </div>
                    <div className="metric-item">
                      <div className="metric-icon">
                        <Target size={20} />
                      </div>
                      <div className="metric-info">
                        <span className="metric-value">0.1%</span>
                        <span className="metric-label">Error Rate</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Recent Activity */}
                <div className="activity-section">
                  <h3>Recent System Activity</h3>
                  <div className="activity-list">
                    <div className="activity-item">
                      <div className="activity-icon">
                        <CheckCircle size={16} color="#22c55e" />
                      </div>
                      <div className="activity-content">
                        <p><strong>National Institute of Technology</strong> verified 25 documents</p>
                        <span>2 hours ago</span>
                      </div>
                    </div>
                    <div className="activity-item">
                      <div className="activity-icon">
                        <Building2 size={16} color="#1e3a8a" />
                      </div>
                      <div className="activity-content">
                        <p><strong>Regional Technical Institute</strong> pending approval</p>
                        <span>4 hours ago</span>
                      </div>
                    </div>
                    <div className="activity-item">
                      <div className="activity-icon">
                        <Users size={16} color="#8b5cf6" />
                      </div>
                      <div className="activity-content">
                        <p><strong>150 new students</strong> registered across all colleges</p>
                        <span>6 hours ago</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'colleges' && (
              <div className="colleges-tab">
                <div className="tab-header">
                  <div>
                    <h2>College Management</h2>
                    <p>Manage and approve educational institutions</p>
                  </div>
                  <div className="tab-controls">
                    <div className="search-box">
                      <Search size={16} />
                      <input
                        type="text"
                        placeholder="Search colleges..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                      />
                    </div>
                  </div>
                </div>

                {loading ? (
                  <div className="loading">Loading colleges...</div>
                ) : (
                  <div className="colleges-list">
                    {filteredColleges.map(college => (
                      <div key={college.id} className="college-card">
                        <div className="college-header">
                          <div className="college-info">
                            <div className="college-avatar">
                              <Building2 size={24} color="#1e3a8a" />
                            </div>
                            <div>
                              <h3>{college.name}</h3>
                              <p>{college.code} • {college.university}</p>
                              <p className="college-contact">{college.contact_email}</p>
                            </div>
                          </div>
                          <div className="college-status">
                            <div className={`status-badge ${college.is_approved ? 'approved' : 'pending'}`}>
                              {college.is_approved ? 'Approved' : 'Pending Approval'}
                            </div>
                            <div className={`status-badge ${college.is_active ? 'active' : 'inactive'}`}>
                              {college.is_active ? 'Active' : 'Suspended'}
                            </div>
                          </div>
                        </div>

                        <div className="college-details">
                          <div className="detail-item">
                            <MapPin size={16} />
                            <span>{college.address}</span>
                          </div>
                          <div className="detail-item">
                            <User size={16} />
                            <span>Admin: {college.admin_name}</span>
                          </div>
                          <div className="detail-item">
                            <Phone size={16} />
                            <span>{college.contact_phone}</span>
                          </div>
                        </div>

                        <div className="college-stats">
                          <div className="stat-item">
                            <Users size={16} />
                            <span>{college.studentsCount} Students</span>
                          </div>
                          <div className="stat-item">
                            <FileText size={16} />
                            <span>{college.documentsCount} Documents</span>
                          </div>
                          <div className="stat-item">
                            <CheckCircle size={16} color="#22c55e" />
                            <span>{college.verifiedCount} Verified</span>
                          </div>
                          <div className="stat-item">
                            <Clock size={16} color="#f59e0b" />
                            <span>{college.pendingCount} Pending</span>
                          </div>
                        </div>

                        <div className="college-actions">
                          <button 
                            className="action-btn view-btn"
                            onClick={() => {
                              setSelectedCollege(college);
                              setShowCollegeModal(true);
                            }}
                          >
                            <Eye size={16} />
                            View Details
                          </button>
                          {!college.is_approved && (
                            <button 
                              className="action-btn approve-btn"
                              onClick={() => handleApproveCollege(college.id)}
                            >
                              <CheckCircle size={16} />
                              Approve
                            </button>
                          )}
                          {college.is_active && (
                            <button 
                              className="action-btn suspend-btn"
                              onClick={() => handleSuspendCollege(college.id)}
                            >
                              <XCircle size={16} />
                              Suspend
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'students' && (
              <div className="students-tab">
                <div className="tab-header">
                  <div>
                    <h2>Students Overview</h2>
                    <p>Monitor all students across the system</p>
                  </div>
                  <div className="tab-controls">
                    <div className="search-box">
                      <Search size={16} />
                      <input
                        type="text"
                        placeholder="Search students..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                      />
                    </div>
                  </div>
                </div>

                {loading ? (
                  <div className="loading">Loading students...</div>
                ) : (
                  <div className="students-list">
                    {filteredStudents.map(student => (
                      <div key={student.id} className="student-card">
                        <div className="student-header">
                          <div className="student-info">
                            <div className="student-avatar">
                              <User size={24} color="#8b5cf6" />
                            </div>
                            <div>
                              <h3>{student.name}</h3>
                              <p>{student.rollNumber} • {student.course}</p>
                              <p className="college-name">{student.college_name}</p>
                            </div>
                          </div>
                          <div className="student-contact">
                            <p>{student.email}</p>
                            <p className="semester">Semester {student.semester}</p>
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
                <h2>System Monitoring</h2>
                <p>Monitor document verification across all institutions</p>

                <div className="monitoring-stats">
                  <div className="monitoring-card">
                    <h4>Document Processing</h4>
                    <div className="processing-stats">
                      <div className="process-item">
                        <span className="process-label">Verified Today</span>
                        <span className="process-value">147</span>
                      </div>
                      <div className="process-item">
                        <span className="process-label">Pending Review</span>
                        <span className="process-value">{systemStats.pendingDocuments}</span>
                      </div>
                      <div className="process-item">
                        <span className="process-label">Average Processing Time</span>
                        <span className="process-value">2.3 hours</span>
                      </div>
                    </div>
                  </div>

                  <div className="monitoring-card">
                    <h4>System Health</h4>
                    <div className="health-stats">
                      <div className="health-item">
                        <span className="health-label">Server Uptime</span>
                        <span className="health-value success">99.9%</span>
                      </div>
                      <div className="health-item">
                        <span className="health-label">OCR Accuracy</span>
                        <span className="health-value success">84.5%</span>
                      </div>
                      <div className="health-item">
                        <span className="health-label">Error Rate</span>
                        <span className="health-value warning">0.1%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </section>
        </div>
      </main>

      {/* College Details Modal */}
      {showCollegeModal && selectedCollege && (
        <div className="modal-overlay" onClick={() => setShowCollegeModal(false)}>
          <div className="modal-content college-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>College Details: {selectedCollege.name}</h3>
              <button
                onClick={() => setShowCollegeModal(false)}
                className="close-btn"
              >
                ×
              </button>
            </div>

            <div className="college-modal-content">
              <div className="modal-section">
                <h4>Basic Information</h4>
                <div className="info-grid">
                  <div><strong>College Name:</strong> {selectedCollege.name}</div>
                  <div><strong>College Code:</strong> {selectedCollege.code}</div>
                  <div><strong>University:</strong> {selectedCollege.university}</div>
                  <div><strong>Address:</strong> {selectedCollege.address}</div>
                  <div><strong>Contact Email:</strong> {selectedCollege.contact_email}</div>
                  <div><strong>Contact Phone:</strong> {selectedCollege.contact_phone}</div>
                  <div><strong>Admin Name:</strong> {selectedCollege.admin_name}</div>
                  <div><strong>Registration Date:</strong> {formatDate(selectedCollege.created_at)}</div>
                </div>
              </div>

              <div className="modal-section">
                <h4>Statistics</h4>
                <div className="stats-row">
                  <div className="stat-box">
                    <span className="stat-number">{selectedCollege.studentsCount}</span>
                    <span className="stat-label">Students</span>
                  </div>
                  <div className="stat-box">
                    <span className="stat-number">{selectedCollege.documentsCount}</span>
                    <span className="stat-label">Documents</span>
                  </div>
                  <div className="stat-box">
                    <span className="stat-number">{selectedCollege.verifiedCount}</span>
                    <span className="stat-label">Verified</span>
                  </div>
                  <div className="stat-box">
                    <span className="stat-number">{selectedCollege.pendingCount}</span>
                    <span className="stat-label">Pending</span>
                  </div>
                </div>
              </div>

              <div className="modal-section">
                <h4>Status & Actions</h4>
                <div className="status-actions">
                  <div className="status-row">
                    <span>Approval Status:</span>
                    <span className={`status-indicator ${selectedCollege.is_approved ? 'approved' : 'pending'}`}>
                      {selectedCollege.is_approved ? 'Approved' : 'Pending Approval'}
                    </span>
                  </div>
                  <div className="status-row">
                    <span>Activity Status:</span>
                    <span className={`status-indicator ${selectedCollege.is_active ? 'active' : 'inactive'}`}>
                      {selectedCollege.is_active ? 'Active' : 'Suspended'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GovernmentDashboard;