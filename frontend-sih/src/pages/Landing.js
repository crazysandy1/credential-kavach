import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, FileCheck, Users, Database, Zap, Award } from 'lucide-react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import DocumentUpload from '../components/DocumentUpload';

const Landing = () => {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <Header />

      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <h2 className="hero-title">
            Instant Academic Certificate Verification
          </h2>
          <p className="hero-subtitle">
            Secure, transparent, and efficient credential verification system 
            for the digital age - powered by Government of Jharkhand
          </p>
          <div className="flex justify-center gap-4 mt-8">
            <a href="#features" className="btn btn-secondary">
              Explore Features
            </a>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-16 bg-white">
        <div className="container">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-navy mb-4">
              Revolutionizing Credential Verification
            </h3>
            <p className="text-lg text-gray max-w-2xl mx-auto">
              Our advanced platform combines OCR technology, blockchain security, 
              and government backing to ensure authentic credential verification.
            </p>
          </div>

          <div className="features-grid">
            <div className="feature-card card">
              <FileCheck className="feature-icon mx-auto" size={60} />
              <h4 className="feature-title">Instant OCR Processing</h4>
              <p className="text-gray">
                Advanced OCR technology automatically extracts and structures data 
                from uploaded certificates and mark sheets with 95%+ accuracy.
              </p>
            </div>

            <div className="feature-card card">
              <Shield className="feature-icon mx-auto" size={60} />
              <h4 className="feature-title">Government Verified</h4>
              <p className="text-gray">
                Official Government of Jharkhand platform ensuring highest 
                security standards and complete data protection.
              </p>
            </div>

            <div className="feature-card card">
              <Database className="feature-icon mx-auto" size={60} />
              <h4 className="feature-title">Cross-Reference Database</h4>
              <p className="text-gray">
                Real-time verification against institutional databases to 
                prevent fraud and ensure authenticity.
              </p>
            </div>

            <div className="feature-card card">
              <Users className="feature-icon mx-auto" size={60} />
              <h4 className="feature-title">Multi-Role Access</h4>
              <p className="text-gray">
                Separate interfaces for students, educational institutions, 
                and government officials with role-based permissions.
              </p>
            </div>

            <div className="feature-card card">
              <Zap className="feature-icon mx-auto" size={60} />
              <h4 className="feature-title">Lightning Fast</h4>
              <p className="text-gray">
                Get verification results in seconds, not days. Our optimized 
                system processes documents instantly.
              </p>
            </div>

            <div className="feature-card card">
              <Award className="feature-icon mx-auto" size={60} />
              <h4 className="feature-title">Audit Trail</h4>
              <p className="text-gray">
                Complete transparency with detailed audit logs for all 
                verification activities and system access.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Document Upload Section */}
      <section className="py-16 bg-gradient-to-r from-primary to-secondary text-white">
        <div className="container">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold mb-4">Quick Document Verification</h3>
            <p className="text-lg opacity-90 max-w-2xl mx-auto">
              Upload your academic document below for instant verification. 
              Our OCR system will extract and validate the information.
            </p>
          </div>

          <div className="max-w-2xl mx-auto bg-white rounded-lg p-8 text-gray-800">
            <DocumentUpload />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-light" id="contact">
        <div className="container text-center">
          <h3 className="text-3xl font-bold text-navy mb-4">
            Ready to Get Started?
          </h3>
          <p className="text-lg text-gray mb-8 max-w-2xl mx-auto">
            Join thousands of students, institutions, and officials who trust 
            New India Credential Kavach for secure credential verification.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <div className="card text-center">
              <h4 className="text-xl font-semibold text-navy mb-2">Students</h4>
              <p className="text-gray mb-4">
                Upload and verify your academic documents instantly
              </p>
            </div>

            <div className="card text-center">
              <h4 className="text-xl font-semibold text-navy mb-2">Colleges</h4>
              <p className="text-gray mb-4">
                Verify student credentials and manage institutional records
              </p>
            </div>

            <div className="card text-center">
              <h4 className="text-xl font-semibold text-navy mb-2">Government</h4>
              <p className="text-gray mb-4">
                Administrative access for system oversight and management
              </p>
            </div>
          </div>
          <p className="text-sm text-gray mt-6">Use the Sign In link in the top navigation to access your dashboard.</p>
        </div>
      </section>

      {/* Stats Section */}
      <section id="stats" className="py-16 bg-white">
        <div className="container">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-primary mb-2">10,000+</div>
              <div className="text-gray">Documents Verified</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary mb-2">500+</div>
              <div className="text-gray">Registered Institutions</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary mb-2">95%</div>
              <div className="text-gray">Accuracy Rate</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary mb-2">24/7</div>
              <div className="text-gray">System Availability</div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <Footer />
    </div>
  );
};

export default Landing;