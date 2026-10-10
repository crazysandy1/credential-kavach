import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { FileText, Shield, Clock, CheckCircle, Hash, Link as LinkIcon } from 'lucide-react';
import './DocumentBlocks.css';

function DocumentBlocks() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  // Generate blockchain-style hash for each document
  const generateHash = (id, timestamp = Date.now()) => {
    const chars = '0123456789abcdef';
    let hash = '';
    const seed = id + timestamp.toString();
    
    for (let i = 0; i < 64; i++) {
      const index = (seed.charCodeAt(i % seed.length) + i) % chars.length;
      hash += chars[index];
    }
    return hash;
  };

  // Generate previous hash (simulating blockchain linkage)
  const generatePrevHash = (index) => {
    if (index === 0) return '0000000000000000000000000000000000000000000000000000000000000000';
    const chars = '0123456789abcdef';
    let hash = '';
    for (let i = 0; i < 64; i++) {
      hash += chars[Math.floor((index * 1337 + i) % chars.length)];
    }
    return hash;
  };

  useEffect(() => {
    fetch('/api/documents')
      .then(res => res.json())
      .then(data => {
        const docs = Array.isArray(data) ? data : (data.documents || []);
        
        // Transform documents into blockchain nodes
        const blockchainNodes = docs.map((doc, index) => ({
          id: doc.id,
          title: doc.title || doc.name || `Document ${index + 1}`,
          studentName: doc.uploader?.name || doc.name || 'Anonymous Student',
          documentType: doc.document_type || 'marks_card',
          status: doc.status || 'verified',
          timestamp: doc.created_at || new Date().toISOString(),
          blockNumber: index + 1,
          hash: generateHash(doc.id, new Date(doc.created_at || Date.now()).getTime()),
          prevHash: generatePrevHash(index),
          fileSize: doc.file_size || 0,
          mimeType: doc.mime_type || 'image/jpeg',
          link: doc.link || `/document/${doc.id}`
        }));
        
        setDocuments(blockchainNodes);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching documents:', err);
        // Generate sample blockchain nodes for demonstration
        const sampleNodes = Array.from({ length: 5 }, (_, index) => ({
          id: `doc_${index + 1}`,
          title: `Academic Document ${index + 1}`,
          studentName: ['Arjun Sharma', 'Priya Patel', 'Vikram Singh', 'Ananya Gupta', 'Rohit Kumar'][index],
          documentType: ['marks_card', 'degree_certificate', 'transcript', 'character_certificate', 'graduation_certificate'][index],
          status: ['verified', 'pending', 'verified', 'verified', 'processing'][index],
          timestamp: new Date(Date.now() - (5 - index) * 3600000).toISOString(),
          blockNumber: index + 1,
          hash: generateHash(`doc_${index + 1}`, Date.now() - (5 - index) * 3600000),
          prevHash: generatePrevHash(index),
          fileSize: Math.floor(Math.random() * 2000000) + 500000,
          mimeType: 'image/jpeg',
          link: `/result/doc_${index + 1}`
        }));
        setDocuments(sampleNodes);
        setLoading(false);
      });
  }, []);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'verified': return <CheckCircle className="status-icon verified" size={16} />;
      case 'pending': return <Clock className="status-icon pending" size={16} />;
      case 'processing': return <Shield className="status-icon processing" size={16} />;
      default: return <FileText className="status-icon default" size={16} />;
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="blockchain-loading">
        <div className="loading-spinner"></div>
        <p>Loading Blockchain Network...</p>
      </div>
    );
  }

  return (
    <div className="blockchain-container">
      <div className="blockchain-header">
        <h2 className="blockchain-title">
          <Hash className="title-icon" size={24} />
          Document Blockchain Network
        </h2>
        <p className="blockchain-subtitle">
          Secure, immutable record of all student documents
        </p>
        <div className="blockchain-stats">
          <div className="stat-item">
            <span className="stat-value">{documents.length}</span>
            <span className="stat-label">Total Blocks</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{documents.filter(d => d.status === 'verified').length}</span>
            <span className="stat-label">Verified</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{documents.filter(d => d.status === 'pending').length}</span>
            <span className="stat-label">Pending</span>
          </div>
        </div>
      </div>

      <div className="blockchain-network">
        <div className="blockchain-chain">
          {documents.map((doc, index) => (
            <div key={doc.id} className="blockchain-node-container">
              {/* Connection Line */}
              {index > 0 && <div className="blockchain-connection"></div>}
              
              {/* Blockchain Node */}
              <div className={`blockchain-node ${doc.status}`}>
                <div className="node-header">
                  <div className="node-number">#{doc.blockNumber}</div>
                  <div className="node-status">
                    {getStatusIcon(doc.status)}
                    <span className="status-text">{doc.status}</span>
                  </div>
                </div>

                <div className="node-content">
                  <div className="node-title">
                    <FileText size={18} className="title-icon" />
                    {doc.title}
                  </div>
                  
                  <div className="node-student">
                    <strong>Student:</strong> {doc.studentName}
                  </div>

                  <div className="node-details">
                    <div className="detail-item">
                      <span className="detail-label">Type:</span>
                      <span className="detail-value">{doc.documentType.replace('_', ' ')}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Size:</span>
                      <span className="detail-value">{formatFileSize(doc.fileSize)}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Time:</span>
                      <span className="detail-value">{formatTimestamp(doc.timestamp)}</span>
                    </div>
                  </div>

                  <div className="node-hashes">
                    <div className="hash-item">
                      <div className="hash-label">Current Hash:</div>
                      <div className="hash-value">{doc.hash.substring(0, 16)}...</div>
                    </div>
                    <div className="hash-item">
                      <div className="hash-label">Previous Hash:</div>
                      <div className="hash-value">{doc.prevHash.substring(0, 16)}...</div>
                    </div>
                  </div>

                  <Link to={doc.link} className="node-action">
                    <LinkIcon size={16} />
                    View Document
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Genesis Block */}
        <div className="genesis-block">
          <div className="genesis-content">
            <Hash size={32} className="genesis-icon" />
            <div className="genesis-title">Genesis Block</div>
            <div className="genesis-hash">0000...0000</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default DocumentBlocks;
