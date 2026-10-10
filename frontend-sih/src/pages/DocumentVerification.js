import React, { useState, useEffect } from 'react';
import { Search, FileText, CheckCircle2, XCircle, AlertTriangle, Eye, Upload, FileCheck, AlertCircle } from 'lucide-react';
import { apiService } from '../services/api';
import { toast } from 'react-toastify';

const DocumentVerification = () => {
  const [searchEmail, setSearchEmail] = useState('');
  const [searchResult, setSearchResult] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const [verificationHistory, setVerificationHistory] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState(null);
  
  // Upload states
  const [uploadFile, setUploadFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  useEffect(() => {
    loadVerificationHistory();
  }, []);

  const loadVerificationHistory = async () => {
    try {
      // This would be an API call to get employer's verification history
      // For now, we'll use mock data
      setVerificationHistory([
        {
          id: '1',
          student_email: 'student1@example.com',
          document_type: 'marks_card',
          verified_at: '2025-09-17T10:30:00Z',
          status: 'verified',
          confidence_score: 95
        },
        {
          id: '2',
          student_email: 'student2@example.com',
          document_type: 'degree_certificate',
          verified_at: '2025-09-16T14:15:00Z',
          status: 'suspicious',
          confidence_score: 65
        }
      ]);
    } catch (error) {
      console.error('Error loading verification history:', error);
    }
  };

  const handleSearch = async () => {
    if (!searchEmail.trim()) {
      toast.error('Please enter a student email address');
      return;
    }

    setIsSearching(true);
    try {
      const response = await apiService.verifyStudentDocument({
        student_email: searchEmail,
        document_type: 'marks_card'
      });
      
      setSearchResult(response);
      
      if (response.verified) {
        toast.success('Student documents found and verified!');
      } else {
        toast.warning('Student not found or documents unavailable');
      }
    } catch (error) {
      toast.error('Search failed: ' + error.message);
      setSearchResult(null);
    } finally {
      setIsSearching(false);
    }
  };

  const handleVerificationAction = async (action, documentId, notes = '') => {
    try {
      const response = await apiService.submitVerification({
        document_id: documentId,
        verification_status: action,
        notes: notes,
        confidence_score: searchResult?.confidence_score || 0
      });
      
      toast.success(`Document ${action} successfully!`);
      
      // Refresh history
      loadVerificationHistory();
      
      // Clear current search
      setSearchResult(null);
      setSearchEmail('');
    } catch (error) {
      toast.error('Verification action failed: ' + error.message);
    }
  };

  // File upload handlers
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (file) => {
    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
    if (!allowedTypes.includes(file.type)) {
      toast.error('Please upload a valid image (JPG, PNG) or PDF file');
      return;
    }
    
    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      toast.error('File size must be less than 10MB');
      return;
    }
    
    setUploadFile(file);
    setUploadResult(null);
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const handleUploadDocument = async () => {
    if (!uploadFile) {
      toast.error('Please select a file to upload');
      return;
    }
    
    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', uploadFile);
      formData.append('document_type', 'verification_document');
      formData.append('title', uploadFile.name);
      formData.append('description', 'Document uploaded by employer for verification');
      
      const response = await apiService.uploadDocument(formData);
      
      // Transform the response to match our expected format
      const ocrData = response.document?.ocr_data || null;
      const transformedResult = {
        is_verified: response.document?.ocr_processed || false,
        confidence_score: ocrData ? 90 : 0, // High confidence if OCR processed successfully
        ocr_data: ocrData ? {
          university: ocrData.university,
          student_name: ocrData.student_name,
          roll_number: ocrData.roll_number,
          result: ocrData.result,
          total_subjects: ocrData.subjects?.length || 0
        } : null,
        subjects_data: ocrData?.subjects || [],
        fraud_indicators: [],
        database_match: null,
        message: response.message,
        document_id: response.document?.id
      };
      
      setUploadResult(transformedResult);
      
      toast.success('Document processed successfully!');
      
      // Add to verification history
      loadVerificationHistory();
    } catch (error) {
      toast.error('Upload failed: ' + error.message);
      setUploadResult(null);
    } finally {
      setIsUploading(false);
    }
  };

  const clearUpload = () => {
    setUploadFile(null);
    setUploadResult(null);
  };

  const getStatusBadge = (status, score) => {
    if (status === 'verified' || score >= 90) {
      return (
        <span className="status-badge status-success flex items-center gap-1">
          <CheckCircle2 size={16} />
          Verified
        </span>
      );
    } else if (status === 'rejected' || score < 50) {
      return (
        <span className="status-badge status-error flex items-center gap-1">
          <XCircle size={16} />
          Rejected
        </span>
      );
    } else {
      return (
        <span className="status-badge status-warning flex items-center gap-1">
          <AlertTriangle size={16} />
          Suspicious
        </span>
      );
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Document Verification</h2>
          <p className="card-subtitle">
            Upload and verify documents through OCR processing and database verification
          </p>
        </div>
      </div>

      {/* Document Upload Section */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Upload size={20} />
            Upload Document for Verification
          </h3>
          <p className="text-sm text-gray-600">
            Upload a student document to verify its authenticity through OCR analysis
          </p>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Upload Area */}
            <div>
              <div
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                  dragActive
                    ? 'border-primary bg-blue-50'
                    : uploadFile
                    ? 'border-green-400 bg-green-50'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                {uploadFile ? (
                  <div className="space-y-3">
                    <FileCheck className="mx-auto text-green-500" size={48} />
                    <div>
                      <p className="font-medium text-green-700">{uploadFile.name}</p>
                      <p className="text-sm text-gray-600">
                        {(uploadFile.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                    <div className="flex gap-2 justify-center">
                      <button
                        onClick={handleUploadDocument}
                        disabled={isUploading}
                        className="btn btn-primary flex items-center gap-2"
                      >
                        {isUploading ? (
                          <div className="spinner"></div>
                        ) : (
                          <Upload size={16} />
                        )}
                        {isUploading ? 'Processing...' : 'Verify Document'}
                      </button>
                      <button
                        onClick={clearUpload}
                        disabled={isUploading}
                        className="btn btn-outline"
                      >
                        Clear
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <Upload className="mx-auto text-gray-400" size={48} />
                    <div>
                      <p className="text-lg font-medium text-gray-700">
                        Drop document here or click to browse
                      </p>
                      <p className="text-sm text-gray-500">
                        Supports JPG, PNG, PDF up to 10MB
                      </p>
                    </div>
                    <input
                      type="file"
                      className="hidden"
                      id="file-upload"
                      accept=".jpg,.jpeg,.png,.pdf"
                      onChange={handleFileChange}
                      disabled={isUploading}
                    />
                    <label
                      htmlFor="file-upload"
                      className="btn btn-primary cursor-pointer"
                    >
                      Select File
                    </label>
                  </div>
                )}
              </div>
            </div>

            {/* Upload Result */}
            <div>
              {uploadResult ? (
                <div className="space-y-4">
                  <h4 className="font-semibold flex items-center gap-2">
                    <FileCheck size={18} className="text-green-500" />
                    OCR Analysis Results
                  </h4>
                  
                  {/* Verification Status */}
                  <div className="bg-light rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <span className="font-medium">Verification Status:</span>
                      <div className="flex items-center gap-2">
                        {uploadResult.is_verified ? (
                          <>
                            <CheckCircle2 className="text-green-500" size={16} />
                            <span className="status-badge status-success">Verified in Database</span>
                          </>
                        ) : (
                          <>
                            <AlertCircle className="text-yellow-500" size={16} />
                            <span className="status-badge status-pending">Not Found in Database</span>
                          </>
                        )}
                      </div>
                    </div>
                    
                    {/* Confidence Score */}
                    <div className="mb-3">
                      <div className="flex justify-between text-sm mb-1">
                        <span>OCR Confidence Score</span>
                        <span>{uploadResult.confidence_score || 0}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            (uploadResult.confidence_score || 0) >= 90
                              ? 'bg-green-500'
                              : (uploadResult.confidence_score || 0) >= 70
                              ? 'bg-yellow-500'
                              : 'bg-red-500'
                          }`}
                          style={{ width: `${uploadResult.confidence_score || 0}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>

                  {/* Extracted Data */}
                  {uploadResult.ocr_data && (
                    <div className="space-y-4">
                      <div className="bg-light rounded-lg p-4">
                        <h5 className="font-medium mb-3">Extracted Information:</h5>
                        <div className="grid grid-cols-1 gap-2 text-sm">
                          {Object.entries(uploadResult.ocr_data).map(([key, value]) => (
                            <div key={key} className="flex justify-between">
                              <span className="font-medium capitalize">
                                {key.replace('_', ' ')}:
                              </span>
                              <span className="text-gray-700">
                                {typeof value === 'object' ? JSON.stringify(value) : value}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Subjects Breakdown */}
                      {uploadResult.subjects_data && uploadResult.subjects_data.length > 0 && (
                        <div className="bg-light rounded-lg p-4">
                          <h5 className="font-medium mb-3">Subjects & Marks:</h5>
                          <div className="space-y-2">
                            {uploadResult.subjects_data.map((subject, index) => (
                              <div key={index} className="flex justify-between items-center p-2 bg-white rounded border-l-4 border-blue-400">
                                <div>
                                  <div className="font-medium text-sm">{subject.course_title}</div>
                                  <div className="text-xs text-gray-500">{subject.course_code}</div>
                                </div>
                                <div className="text-right">
                                  <div className="font-bold text-primary">{subject.marks}</div>
                                  <div className="text-xs text-gray-500">marks</div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Fraud Detection */}
                  {uploadResult.fraud_indicators && uploadResult.fraud_indicators.length > 0 && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                      <h5 className="font-medium text-red-800 mb-2 flex items-center gap-2">
                        <AlertTriangle size={16} />
                        Fraud Indicators Detected:
                      </h5>
                      <ul className="text-sm text-red-700 space-y-1">
                        {uploadResult.fraud_indicators.map((indicator, index) => (
                          <li key={index}>• {indicator}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Verification Actions */}
                  {uploadResult.ocr_data && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <h5 className="font-medium text-blue-800 mb-3">Verification Actions:</h5>
                      <div className="flex gap-2 flex-wrap">
                        <button
                          onClick={() => {
                            if (uploadResult.ocr_data.student_name) {
                              setSearchEmail('');
                              toast.info(`Search for student: ${uploadResult.ocr_data.student_name}`);
                            }
                          }}
                          className="btn btn-primary btn-sm"
                        >
                          <Search size={14} />
                          Search in Database
                        </button>
                        <button
                          onClick={() => {
                            toast.success('Document marked as verified for employment');
                          }}
                          className="btn btn-success btn-sm"
                        >
                          <CheckCircle2 size={14} />
                          Mark as Verified
                        </button>
                        <button
                          onClick={() => {
                            toast.error('Document flagged as suspicious');
                          }}
                          className="btn btn-warning btn-sm"
                        >
                          <AlertTriangle size={14} />
                          Flag as Suspicious
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Database Match */}
                  {uploadResult.database_match && (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <h5 className="font-medium text-green-800 mb-2">Database Match Found:</h5>
                      <div className="text-sm text-green-700 space-y-1">
                        <div>Student: {uploadResult.database_match.student_name}</div>
                        <div>Email: {uploadResult.database_match.student_email}</div>
                        <div>College: {uploadResult.database_match.college_name}</div>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <FileText size={48} className="mx-auto mb-3 opacity-50" />
                  <p>Upload a document to see OCR analysis results</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Search Section */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold">Search Student Documents</h3>
        </div>
        <div className="card-body">
          <div className="flex gap-4 items-end">
            <div className="form-group flex-1">
              <label className="form-label">Student Email Address</label>
              <input
                type="email"
                value={searchEmail}
                onChange={(e) => setSearchEmail(e.target.value)}
                className="form-input"
                placeholder="Enter student's email address"
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>
            <button
              onClick={handleSearch}
              disabled={isSearching}
              className="btn btn-primary flex items-center gap-2"
            >
              <Search size={16} />
              {isSearching ? 'Searching...' : 'Search'}
            </button>
          </div>
        </div>
      </div>

      {/* Search Results */}
      {searchResult && (
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold">Verification Results</h3>
          </div>
          <div className="card-body">
            {searchResult.verified ? (
              <div className="space-y-4">
                {/* Student Info */}
                <div className="bg-light rounded-lg p-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-700">Student Name</label>
                      <p className="text-gray-900">{searchResult.student_name}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700">Email</label>
                      <p className="text-gray-900">{searchResult.student_email}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700">Verification Status</label>
                      {getStatusBadge(searchResult.status, searchResult.confidence_score)}
                    </div>
                  </div>
                </div>

                {/* Document Details */}
                {searchResult.documents && searchResult.documents.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-3">Available Documents</h4>
                    <div className="space-y-3">
                      {searchResult.documents.map((doc, index) => (
                        <div key={index} className="border rounded-lg p-4">
                          <div className="flex justify-between items-start mb-3">
                            <div className="flex items-center gap-2">
                              <FileText className="text-primary" size={20} />
                              <div>
                                <h5 className="font-medium">{doc.title}</h5>
                                <p className="text-sm text-gray-600">{doc.document_type}</p>
                              </div>
                            </div>
                            {getStatusBadge(doc.status, doc.confidence_score || 0)}
                          </div>

                          {doc.ocr_data && (
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm mb-4">
                              {doc.ocr_data.roll_number && (
                                <div>
                                  <span className="font-medium">Roll No:</span> {doc.ocr_data.roll_number}
                                </div>
                              )}
                              {doc.ocr_data.college_name && (
                                <div>
                                  <span className="font-medium">College:</span> {doc.ocr_data.college_name}
                                </div>
                              )}
                              {doc.ocr_data.percentage && (
                                <div>
                                  <span className="font-medium">Percentage:</span> {doc.ocr_data.percentage}%
                                </div>
                              )}
                              {doc.ocr_data.year && (
                                <div>
                                  <span className="font-medium">Year:</span> {doc.ocr_data.year}
                                </div>
                              )}
                            </div>
                          )}

                          {/* Fraud Indicators */}
                          {searchResult.fraud_indicators && searchResult.fraud_indicators.length > 0 && (
                            <div className="bg-yellow-50 border border-yellow-200 rounded p-3 mb-3">
                              <h6 className="font-medium text-yellow-800 mb-1">Fraud Indicators Detected:</h6>
                              <ul className="text-sm text-yellow-700">
                                {searchResult.fraud_indicators.map((indicator, i) => (
                                  <li key={i}>• {indicator}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {/* Confidence Score */}
                          <div className="mb-4">
                            <div className="flex justify-between text-sm mb-1">
                              <span>Confidence Score</span>
                              <span>{searchResult.confidence_score || 0}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div
                                className={`h-2 rounded-full ${
                                  (searchResult.confidence_score || 0) >= 90
                                    ? 'bg-green-500'
                                    : (searchResult.confidence_score || 0) >= 70
                                    ? 'bg-yellow-500'
                                    : 'bg-red-500'
                                }`}
                                style={{ width: `${searchResult.confidence_score || 0}%` }}
                              ></div>
                            </div>
                          </div>

                          {/* Action Buttons */}
                          <div className="flex gap-2">
                            <button
                              onClick={() => handleVerificationAction('verified', doc.id, 'Document verified for employment')}
                              className="btn btn-success btn-sm"
                            >
                              <CheckCircle2 size={16} />
                              Verify Document
                            </button>
                            <button
                              onClick={() => handleVerificationAction('rejected', doc.id, 'Document rejected due to inconsistencies')}
                              className="btn btn-error btn-sm"
                            >
                              <XCircle size={16} />
                              Reject Document
                            </button>
                            <button
                              onClick={() => setSelectedDocument(doc)}
                              className="btn btn-outline btn-sm"
                            >
                              <Eye size={16} />
                              View Details
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <XCircle className="mx-auto text-red-500 mb-4" size={48} />
                <h4 className="text-lg font-semibold mb-2">No Documents Found</h4>
                <p className="text-gray-600">
                  {searchResult.message || 'No verified documents found for this student email.'}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Verification History */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold">Recent Verifications</h3>
        </div>
        <div className="card-body">
          {verificationHistory.length > 0 ? (
            <div className="space-y-3">
              {verificationHistory.map((record) => (
                <div key={record.id} className="flex justify-between items-center p-3 border rounded-lg">
                  <div>
                    <p className="font-medium">{record.student_email}</p>
                    <p className="text-sm text-gray-600">
                      {record.document_type} • {new Date(record.verified_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="text-right">
                    {getStatusBadge(record.status, record.confidence_score)}
                    <p className="text-sm text-gray-600 mt-1">
                      Confidence: {record.confidence_score}%
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <FileText className="mx-auto mb-4" size={48} />
              <p>No verification history available</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DocumentVerification;