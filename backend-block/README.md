# SIH Backend - Django + Docker + SQLite

A Django REST API backend with Docker containerization and SQLite database, using Pipenv for dependency management.

## Features

- 🐍 Django 4.2 with Django REST Framework
- 🐳 Docker & Docker Compose setup
- 📦 Pipenv for dependency management
- 🗄️ SQLite database (volume-mounted for persistence)
- 🌐 CORS enabled for frontend integration
- ⚡ Hot-reload in development
- 🔧 Environment-based configuration

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ (for local development)
- Pipenv (for local development)

### Option 1: Docker (Recommended)

1. **Clone and setup**:
   ```bash
   cd /home/adi/code/sih-backend
   cp .env.example .env
   ```

2. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - API: http://localhost:8000
   - Health Check: http://localhost:8000/api/health/
   - API Info: http://localhost:8000/api/info/
   - Admin: http://localhost:8000/admin/

### Option 2: Local Development

1. **Install dependencies**:
   ```bash
   pipenv install
   pipenv install --dev  # for development dependencies
   ```

2. **Activate virtual environment**:
   ```bash
   pipenv shell
   ```

3. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Create superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

5. **Run development server**:
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
sih-backend/
├── api/                    # API app
│   ├── views.py           # API views
│   ├── urls.py            # API URL patterns
│   └── ...
├── sih_backend/           # Main project
│   ├── settings.py        # Django settings
│   ├── urls.py            # Main URL patterns
│   └── ...
├── data/                  # SQLite database volume (created by Docker)
├── Pipfile                # Pipenv dependencies
├── Pipfile.lock           # Locked dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose configuration
├── .env                   # Environment variables
└── manage.py              # Django management script
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health/` | GET | Health check endpoint |
| `/api/info/` | GET | API information |
| `/admin/` | GET | Django admin interface |

## Environment Variables

Configure these in your `.env` file:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
DATABASE_PATH=/app/data/db.sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Development Commands

### Using Docker Compose

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Run Django commands
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic
```

### Using Pipenv (Local)

```bash
# Install dependencies
pipenv install
pipenv install --dev

# Activate shell
pipenv shell

# Run Django commands
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Run tests
python manage.py test

# Code formatting
black .
flake8 .
```

## Database

- **Type**: SQLite
- **Location**: `./data/db.sqlite3` (in Docker) or `./db.sqlite3` (local)
- **Persistence**: Database is stored in a Docker volume for persistence

## CORS Configuration

CORS is configured to allow requests from:
- `http://localhost:3000` (React default)
- `http://127.0.0.1:3000`

Update `CORS_ALLOWED_ORIGINS` in `.env` to add more origins.

## Production Considerations

1. **Environment Variables**:
   - Set `DEBUG=False`
   - Use a strong `SECRET_KEY`
   - Configure appropriate `ALLOWED_HOSTS`

2. **Database**:
   - Consider PostgreSQL or MySQL for production
   - Implement database backups

3. **Security**:
   - Enable HTTPS
   - Configure proper CORS origins
   - Implement authentication/authorization

4. **Performance**:
   - Use a production WSGI server (gunicorn)
   - Configure static file serving
   - Add caching layer

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests: `python manage.py test`
4. Format code: `black .`
5. Check linting: `flake8 .`
6. Submit a pull request

## License

This project is licensed under the MIT License.
