import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, Menu, X } from 'lucide-react';

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = React.useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  return (
    <header className="site-header">
      <div className="container">
        <div className="header-content">
          {/* Logo Section */}
          <Link to="/" className="logo-section">
            <Shield size={36} />
            <div>
              <h1 className="logo-text">New India Credential Kavach</h1>
              <p className="government-text">Government of Jharkhand</p>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="desktop-nav">
            <ul className="nav-links">
              <li><a href="#features" className="nav-link">Features</a></li>
              <li><a href="#stats" className="nav-link">Statistics</a></li>
              <li><a href="#contact" className="nav-link">Contact</a></li>
            </ul>
          </nav>

          {/* Auth Buttons */}
          <div className="auth-buttons">
            <Link to="/login" className="btn btn-outline">
              Sign In
            </Link>
            <Link to="/signup" className="btn btn-primary">
              Sign Up
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="mobile-menu-btn"
            onClick={toggleMenu}
            aria-label="Toggle menu"
          >
            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="mobile-nav">
            <nav>
              <ul className="mobile-nav-links">
                <li><a href="#features" className="mobile-nav-link" onClick={toggleMenu}>Features</a></li>
                <li><a href="#stats" className="mobile-nav-link" onClick={toggleMenu}>Statistics</a></li>
                <li><a href="#contact" className="mobile-nav-link" onClick={toggleMenu}>Contact</a></li>
              </ul>
            </nav>
            <div className="mobile-auth-buttons">
              <Link to="/login" className="btn btn-outline w-full" onClick={toggleMenu}>
                Sign In
              </Link>
              <Link to="/signup" className="btn btn-primary w-full" onClick={toggleMenu}>
                Sign Up
              </Link>
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
