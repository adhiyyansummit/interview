#!/bin/bash
# Setup script for Django Loan System Interview Project

set -e

echo "🚀 Setting up Django Loan System..."

# Activate virtual environment
echo "📦 Activating virtual environment..."
source interview_virtual_env/bin/activate

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️  Running migrations..."
python manage.py migrate

# Create superuser
echo "👤 Creating superuser..."
echo "Please enter credentials for admin user:"
python manage.py createsuperuser

# Run tests
echo "✅ Running tests..."
python manage.py test loans

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "🎉 Setup complete!"
echo ""
echo "Start the server with:"
echo "  python manage.py runserver"
echo ""
echo "Then visit:"
echo "  Admin: http://localhost:8000/admin"
echo "  API:   http://localhost:8000/api/loans/"
echo ""
echo "📖 Read README.md for interview tasks"
echo "═══════════════════════════════════════════════════════════"
