import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { User, FileCheck, Search, BarChart3, Settings, Building } from 'lucide-react';
import EmployerProfile from './EmployerProfile';
import DocumentVerification from './DocumentVerification';
import './EmployerDashboard.css';

function EmployerDashboard() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'verification', label: 'Document Verification', icon: FileCheck },
    { id: 'profile', label: 'Company Profile', icon: Building },
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return <OverviewTab user={user} setActiveTab={setActiveTab} />;
      case 'verification':
        return <DocumentVerification />;
      case 'profile':
        return <EmployerProfile />;
      default:
        return <OverviewTab user={user} />;
    }
  };

  return (
    <div className="min-h-screen bg-light">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="container py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-navy">Employer Dashboard</h1>
              <p className="text-gray-600 mt-1">
                Welcome back, {user?.full_name} • {user?.company_name}
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className={`status-badge ${user?.is_approved ? 'status-success' : 'status-pending'}`}>
                  {user?.is_approved ? 'Approved' : 'Pending Approval'}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white border-b border-gray-200">
        <div className="container">
          <nav className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-4 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-primary text-primary'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon size={18} />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Tab Content */}
      <div className="container py-6">
        {renderTabContent()}
      </div>
    </div>
  );
}

// Overview Tab Component
const OverviewTab = ({ user, setActiveTab }) => {
  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Documents Verified</p>
                <p className="text-2xl font-bold text-primary">12</p>
              </div>
              <FileCheck className="text-primary" size={32} />
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Fraud Detected</p>
                <p className="text-2xl font-bold text-red-500">2</p>
              </div>
              <Search className="text-red-500" size={32} />
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Success Rate</p>
                <p className="text-2xl font-bold text-green-500">95%</p>
              </div>
              <BarChart3 className="text-green-500" size={32} />
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Quick Verification</h3>
            <p className="card-subtitle">Verify a student document instantly</p>
          </div>
          <div className="card-body">
            <p className="text-gray-600 mb-4">
              Enter a student's email address to quickly verify their academic documents for recruitment purposes.
            </p>
            <button className="btn btn-primary w-full" onClick={() => setActiveTab('verification')}>
              Start Verification
            </button>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Company Information</h3>
            <p className="card-subtitle">Manage your organization details</p>
          </div>
          <div className="card-body">
            <div className="space-y-2 mb-4">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Company:</span>
                <span className="font-medium">{user?.company_name}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Industry:</span>
                <span className="font-medium">{user?.industry}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Registration:</span>
                <span className="font-medium">{user?.company_registration}</span>
              </div>
            </div>
            <button className="btn btn-outline w-full" onClick={() => setActiveTab('profile')}>
              Update Profile
            </button>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Recent Activity</h3>
        </div>
        <div className="card-body">
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-light rounded">
              <div className="flex items-center gap-3">
                <FileCheck className="text-green-500" size={20} />
                <div>
                  <p className="font-medium">Document Verified</p>
                  <p className="text-sm text-gray-600">student@example.com • Marks Card</p>
                </div>
              </div>
              <span className="text-sm text-gray-500">2 hours ago</span>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-light rounded">
              <div className="flex items-center gap-3">
                <Search className="text-blue-500" size={20} />
                <div>
                  <p className="font-medium">Verification Search</p>
                  <p className="text-sm text-gray-600">candidate@college.edu • Degree Certificate</p>
                </div>
              </div>
              <span className="text-sm text-gray-500">1 day ago</span>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-light rounded">
              <div className="flex items-center gap-3">
                <User className="text-primary" size={20} />
                <div>
                  <p className="font-medium">Profile Updated</p>
                  <p className="text-sm text-gray-600">Company information updated</p>
                </div>
              </div>
              <span className="text-sm text-gray-500">3 days ago</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmployerDashboard;