#!/bin/bash

# SIH Backend Management Script

set -e

case "$1" in
  "setup")
    echo "🚀 Setting up SIH Backend..."
    cp .env.example .env
    echo "✅ Environment file created"
    echo "📝 Please edit .env file with your configuration"
    ;;
  
  "dev")
    echo "🐍 Starting local development server..."
    pipenv install
    pipenv run python manage.py migrate
    pipenv run python manage.py runserver
    ;;
  
  "docker-dev")
    echo "🐳 Starting Docker development environment..."
    docker-compose up --build
    ;;
  
  "docker-prod")
    echo "🐳 Starting Docker production environment..."
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build
    ;;
  
  "migrate")
    echo "📊 Running database migrations..."
    if [ "$2" = "docker" ]; then
      docker-compose exec web python manage.py migrate
    else
      pipenv run python manage.py migrate
    fi
    ;;
  
  "superuser")
    echo "👤 Creating superuser..."
    if [ "$2" = "docker" ]; then
      docker-compose exec web python manage.py createsuperuser
    else
      pipenv run python manage.py createsuperuser
    fi
    ;;
  
  "test")
    echo "🧪 Running tests..."
    if [ "$2" = "docker" ]; then
      docker-compose exec web python manage.py test
    else
      pipenv run python manage.py test
    fi
    ;;
  
  "format")
    echo "🎨 Formatting code..."
    pipenv run black .
    pipenv run flake8 .
    ;;
  
  "clean")
    echo "🧹 Cleaning up..."
    docker-compose down -v
    docker system prune -f
    ;;
  
  *)
    echo "SIH Backend Management Script"
    echo ""
    echo "Usage: $0 {command} [options]"
    echo ""
    echo "Commands:"
    echo "  setup          - Initial project setup"
    echo "  dev            - Start local development server"
    echo "  docker-dev     - Start Docker development environment"
    echo "  migrate [docker] - Run database migrations"
    echo "  superuser [docker] - Create superuser"
    echo "  test [docker]  - Run tests"
    echo "  format         - Format code with black and flake8"
    echo "  clean          - Clean Docker containers and volumes"
    echo ""
    echo "Examples:"
    echo "  $0 setup"
    echo "  $0 dev"
    echo "  $0 docker-dev"
    echo "  $0 migrate docker"
    echo "  $0 superuser"
    ;;
esac
