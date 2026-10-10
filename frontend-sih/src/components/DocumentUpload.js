import React, { useState } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle2 } from 'lucide-react';
import { apiService } from '../services/api';
import { toast } from 'react-toastify';

const DocumentUpload = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [extractedData, setExtractedData] = useState(null);
  const [ocrResult, setOcrResult] = useState(null);

  const handleFileSelect = (selectedFile) => {
    if (selectedFile && selectedFile.type.startsWith('image/')) {
      setFile(selectedFile);
      setExtractedData(null);
      setOcrResult(null);
    } else {
      toast.error('Please select a valid image file (PNG, JPG, JPEG)');
    }
  };

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    handleFileSelect(selectedFile);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setDragOver(false);
    
    const droppedFile = event.dataTransfer.files[0];
    handleFileSelect(droppedFile);
  };

  const handleUpload = async () => {
    if (!file) {
      toast.error('Please select a file first');
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('document_type', 'marks_card');
      formData.append('title', `Marks Card - ${file.name}`);
      formData.append('description', 'Quick verification upload from landing page');

      const response = await apiService.uploadDocument(formData);
      
      if (response.document) {
        setExtractedData(response.document.ocr_data);
        setOcrResult(response);
        toast.success('Document processed successfully!');
      }
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Upload failed: ' + error.message);
    } finally {
      setUploading(false);
    }
  };

  const removeFile = () => {
    setFile(null);
    setExtractedData(null);
    setOcrResult(null);
  };

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragOver
            ? 'border-primary bg-primary/10'
            : 'border-gray-300 hover:border-primary'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-upload"
          className="hidden"
          accept="image/*"
          onChange={handleFileChange}
        />

        {!file ? (
          <>
            <Upload className="mx-auto mb-4 text-gray-400" size={48} />
            <h4 className="text-lg font-semibold mb-2">
              Upload Your Academic Document
            </h4>
            <p className="text-gray-600 mb-4">
              Drag and drop or click to select your marks card, certificate, or transcript
            </p>
            <label
              htmlFor="file-upload"
              className="btn btn-primary cursor-pointer inline-block"
            >
              Choose File
            </label>
            <p className="text-sm text-gray-500 mt-2">
              Supports: JPG, PNG, JPEG (Max 10MB)
            </p>
          </>
        ) : (
          <div className="space-y-4">
            <FileText className="mx-auto text-primary" size={48} />
            <div>
              <h4 className="text-lg font-semibold">{file.name}</h4>
              <p className="text-gray-600">
                Size: {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
            <div className="flex justify-center gap-2">
              <button
                onClick={handleUpload}
                disabled={uploading}
                className="btn btn-primary"
              >
                {uploading ? 'Processing...' : 'Process Document'}
              </button>
              <button
                onClick={removeFile}
                className="btn btn-outline"
                disabled={uploading}
              >
                Remove
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Processing Status */}
      {uploading && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
            <span className="text-blue-700">Processing document with OCR technology...</span>
          </div>
        </div>
      )}

      {/* OCR Results */}
      {extractedData && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle2 className="text-green-500" size={24} />
            <h4 className="text-lg font-semibold text-green-800">
              Document Processed Successfully
            </h4>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {extractedData.student_name && (
              <div>
                <label className="text-sm font-medium text-gray-700">Student Name</label>
                <p className="text-gray-900">{extractedData.student_name}</p>
              </div>
            )}
            
            {extractedData.roll_number && (
              <div>
                <label className="text-sm font-medium text-gray-700">Roll Number</label>
                <p className="text-gray-900">{extractedData.roll_number}</p>
              </div>
            )}
            
            {extractedData.college_name && (
              <div>
                <label className="text-sm font-medium text-gray-700">College</label>
                <p className="text-gray-900">{extractedData.college_name}</p>
              </div>
            )}
            
            {extractedData.examination && (
              <div>
                <label className="text-sm font-medium text-gray-700">Examination</label>
                <p className="text-gray-900">{extractedData.examination}</p>
              </div>
            )}
            
            {extractedData.total_marks && (
              <div>
                <label className="text-sm font-medium text-gray-700">Total Marks</label>
                <p className="text-gray-900">{extractedData.total_marks}</p>
              </div>
            )}
            
            {extractedData.percentage && (
              <div>
                <label className="text-sm font-medium text-gray-700">Percentage</label>
                <p className="text-gray-900">{extractedData.percentage}%</p>
              </div>
            )}
          </div>

          {extractedData.subjects && extractedData.subjects.length > 0 && (
            <div className="mt-4">
              <label className="text-sm font-medium text-gray-700 mb-2 block">Subjects & Marks</label>
              <div className="bg-white rounded border p-3">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
                  {extractedData.subjects.map((subject, index) => (
                    <div key={index} className="flex justify-between">
                      <span>{subject.name}</span>
                      <span className="font-medium">{subject.marks}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          <div className="mt-4 p-3 bg-white rounded border">
            <p className="text-sm text-gray-600">
              <AlertCircle className="inline w-4 h-4 mr-1" />
              This is a quick verification for demonstration. For official verification, 
              please register and upload through your student dashboard.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;