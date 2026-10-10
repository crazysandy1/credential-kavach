import React from 'react';
import { Shield, Facebook, Twitter, Linkedin, Mail } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="site-footer">
      <div className="container">
        <div className="footer-grid">
          <div>
            <div className="footer-brand">
              <Shield size={28} />
              <div>
                <div className="brand-title">New India Credential Kavach</div>
                <div className="brand-sub">Government of Jharkhand</div>
              </div>
            </div>
            <p className="footer-desc">
              Secure digital credential verification platform ensuring authenticity and
              preventing educational fraud.
            </p>
          </div>

          <div>
            <div className="footer-heading">Quick Links</div>
            <ul className="footer-links">
              <li><a href="#features">Features</a></li>
              <li><a href="#stats">Statistics</a></li>
              <li><a href="#contact">Contact</a></li>
            </ul>
          </div>

          <div>
            <div className="footer-heading">Government Links</div>
            <ul className="footer-links">
              <li><a href="https://jharkhand.gov.in" target="_blank" rel="noreferrer">Jharkhand Government</a></li>
              <li><a href="https://digitalindia.gov.in" target="_blank" rel="noreferrer">Digital India</a></li>
              <li><a href="#privacy">Privacy Policy</a></li>
              <li><a href="#terms">Terms of Service</a></li>
            </ul>
          </div>

          <div>
            <div className="footer-heading">Contact</div>
            <ul className="footer-links">
              <li className="contact-item"><Mail size={16} /> support@credentialkavach.gov.in</li>
            </ul>
            <div className="socials">
              <a href="#" aria-label="Facebook"><Facebook size={18} /></a>
              <a href="#" aria-label="Twitter"><Twitter size={18} /></a>
              <a href="#" aria-label="LinkedIn"><Linkedin size={18} /></a>
            </div>
          </div>
        </div>

        <div className="footer-bottom">
          © 2025 Government of Jharkhand. All rights reserved. Built for Digital India Initiative.
        </div>
      </div>
    </footer>
  );
};

export default Footer;
