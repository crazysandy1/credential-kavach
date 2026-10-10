# New India Credential Kavach - React Frontend

Modern React application for the Government of Jharkhand's digital credential verification platform. Built with React 18, featuring role-based authentication, document management, and seamless integration with the Flask backend.

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm
- Backend server running on `http://127.0.0.1:5001`

### Installation & Setup

```bash
# Navigate to the React frontend directory
cd frontend-sih

# Install dependencies
npm install

# Start the development server
npm start
```

The application will be available at `http://localhost:3000`

## 🏗️ Project Structure

```
frontend-sih/
├── public/
│   ├── index.html              # Main HTML template
│   └── manifest.json           # PWA configuration
├── src/
│   ├── components/             # Reusable UI components
│   ├── pages/                  # Page components
│   │   ├── Landing.js         # Main landing page
│   │   ├── Login.js           # Authentication page
│   │   ├── Signup.js          # Registration page
│   │   ├── StudentDashboard.js    # Student portal
│   │   ├── CollegeDashboard.js    # College interface
│   │   └── GovernmentDashboard.js # Admin dashboard
│   ├── services/
│   │   └── api.js             # API service layer
│   ├── utils/
│   │   ├── AuthContext.js     # Authentication context
│   │   └── ProtectedRoute.js  # Route protection
│   ├── App.js                 # Main app component
│   ├── App.css               # Global styles
│   └── index.js              # Application entry point
├── package.json              # Dependencies and scripts
└── README.md                 # This file
```

## 🎨 Features

### ✅ Implemented
- **Landing Page**: Professional homepage with Government of Jharkhand branding
- **Authentication System**: Login/signup with role-based forms
- **Student Dashboard**: Complete document management interface
- **File Upload**: Drag-and-drop with OCR processing integration
- **Document Management**: View, download, and track verification status
- **Responsive Design**: Mobile-first approach with professional UI
- **Real-time Notifications**: Toast notifications for user feedback
- **Protected Routes**: Role-based access control

### 🚧 Coming Soon
- **College Dashboard**: Student verification and institutional management
- **Government Dashboard**: System administration and analytics
- **Advanced File Viewer**: In-app document preview
- **Real-time Updates**: WebSocket integration for live status updates

## 🔧 Available Scripts

```bash
# Development
npm start          # Start development server (http://localhost:3000)
npm test           # Run test suite
npm run build      # Build for production
npm run eject      # Eject from Create React App (one-way operation)
```

## 🌐 API Integration

The frontend connects to the Flask backend using axios with the following configuration:

### Base Configuration
```javascript
const API_BASE_URL = 'http://127.0.0.1:5001';
```

### Authentication Flow
1. User logs in through `/login`
2. JWT token received and stored in localStorage
3. Token automatically included in all API requests
4. Role-based redirection to appropriate dashboard

### Key API Endpoints
- `POST /api/auth/login` - User authentication
- `POST /api/auth/signup` - User registration
- `GET /api/auth/profile` - User profile data
- `POST /api/documents/upload` - Document upload with OCR
- `GET /api/documents` - List user documents
- `GET /api/documents/:id/download` - Download documents

## 👥 User Roles & Features

### 🎓 Student Features
- **Registration**: Academic details with validation
- **Document Upload**: Drag-and-drop interface
- **OCR Results**: Real-time text extraction display
- **Status Tracking**: Monitor verification progress
- **File Management**: Download verified documents

### 🏫 College Features *(Backend Ready)*
- **Institution Management**: College profile and settings
- **Student Verification**: Approve/reject student documents
- **Bulk Operations**: Handle multiple documents
- **Analytics**: Institution-specific metrics

### 🏛️ Government Features *(Backend Ready)*
- **System Administration**: Complete platform oversight
- **User Approval**: Manage college registrations
- **Audit Logs**: Monitor all system activity
- **Analytics**: System-wide statistics and insights

## 🎨 Design System

### Color Palette
```css
--primary-saffron: #FF6B35;    /* Government saffron */
--primary-green: #228B22;      /* Growth and prosperity */
--navy-blue: #1e3a8a;          /* Trust and authority */
--light-gray: #f8f9fa;         /* Clean backgrounds */
--dark-gray: #495057;          /* Professional text */
```

### Typography
- **Font Family**: Inter (Google Fonts)
- **Weights**: 300, 400, 500, 600, 700, 800
- **Professional hierarchy** for government standards

### Components
- **Cards**: Clean white containers with subtle shadows
- **Buttons**: Multiple variants (primary, secondary, outline)
- **Forms**: Consistent styling with proper validation
- **Status Badges**: Color-coded verification status
- **Modals**: Centered overlays for detailed interactions

## 📱 Responsive Design

### Breakpoints
- **Mobile**: < 768px (Stack layout, touch-friendly)
- **Tablet**: 768px - 1024px (Adaptive grid)
- **Desktop**: > 1024px (Full layout with sidebars)

### Mobile Features
- Touch-friendly buttons and form elements
- Swipe gestures for navigation
- Optimized file upload for mobile cameras
- Progressive enhancement for desktop features

## 🔒 Security Features

### Client-Side Security
- JWT tokens stored securely in localStorage
- Automatic token expiration handling
- Input validation and sanitization
- Role-based UI element visibility
- Protected routes with authentication checks

### API Security
- Automatic token inclusion in requests
- Request/response interceptors for error handling
- Secure file upload with validation
- CORS protection through backend configuration

## 🚀 Production Deployment

### Build Process
```bash
# Create production build
npm run build

# The build folder will contain optimized static files
```

### Environment Variables
Create `.env` file in the root directory:
```env
REACT_APP_API_URL=https://api.credentialkavach.jharkhand.gov.in
REACT_APP_ENVIRONMENT=production
```

### Deployment Options
1. **Static Hosting**: Netlify, Vercel, GitHub Pages
2. **CDN**: AWS CloudFront, Azure CDN
3. **Traditional Hosting**: Apache, Nginx with build files

### Production Checklist
- [ ] Set proper API URL in environment variables
- [ ] Configure HTTPS and SSL certificates
- [ ] Set up CDN for static assets
- [ ] Configure proper caching headers
- [ ] Enable gzip compression
- [ ] Set up error tracking (Sentry, etc.)
- [ ] Configure analytics (Google Analytics)

## 🛠️ Development Guidelines

### Code Organization
```javascript
// Component structure
const ComponentName = () => {
  // State and hooks
  // Event handlers
  // Effects
  // Render
};

// Consistent naming
- Components: PascalCase
- Files: PascalCase for components
- Variables/Functions: camelCase
- CSS Classes: kebab-case
```

### Best Practices
- Use functional components with hooks
- Implement proper error boundaries
- Follow React accessibility guidelines
- Use semantic HTML elements
- Implement proper loading states
- Handle edge cases gracefully

### State Management
- React Context for authentication
- Local state for component-specific data
- Custom hooks for reusable logic
- Proper state updates and effects

## 🔍 Testing

### Test Structure
```bash
npm test               # Run all tests
npm test -- --watch   # Run tests in watch mode
npm test -- --coverage # Run with coverage report
```

### Testing Strategy
- Unit tests for utility functions
- Component tests for UI interactions
- Integration tests for API calls
- End-to-end tests for user workflows

## 🐛 Troubleshooting

### Common Issues

**API Connection Problems**
```javascript
// Check backend server is running
curl http://127.0.0.1:5001/api/health

// Verify CORS configuration
// Check browser console for errors
```

**Authentication Issues**
- Clear localStorage and cookies
- Check JWT token expiration
- Verify backend JWT configuration
- Ensure proper role assignments

**File Upload Problems**
- Check file size (16MB limit)
- Verify supported file types
- Ensure backend upload folder permissions
- Check network connection during upload

**Build/Start Issues**
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear npm cache
npm cache clean --force
```

### Browser Compatibility
- **Modern Browsers**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Features**: ES6+, CSS Grid, Fetch API
- **Polyfills**: Included via Create React App for older browsers

## 📚 Dependencies

### Core Dependencies
```json
{
  "react": "^18.3.1",
  "react-dom": "^18.3.1",
  "react-router-dom": "^6.26.1",
  "axios": "^1.7.5",
  "react-hot-toast": "^2.4.1",
  "react-dropzone": "^14.2.3",
  "date-fns": "^3.6.0",
  "lucide-react": "^0.428.0"
}
```

### Development Tools
- **Create React App**: Zero-config setup
- **React Scripts**: Build tools and dev server
- **ESLint**: Code linting and formatting
- **Testing Library**: Component testing utilities

---

**New India Credential Kavach React Frontend - Modern, Secure, Government-Grade Interface** 🇮🇳

Built with ❤️ for Digital India Initiative