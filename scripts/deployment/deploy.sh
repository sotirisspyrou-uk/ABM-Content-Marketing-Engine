#!/bin/bash

# ABM Content Marketing Engine - Deployment Script
set -e

echo "🚀 Starting deployment..."

# Check if environment is specified
if [ -z "$1" ]; then
    echo "❌ Usage: ./deploy.sh [staging|production]"
    exit 1
fi

ENV=$1

# Pre-deployment checks
echo "🔍 Running pre-deployment checks..."

# Check if all required environment variables are set
if [ ! -f ".env" ]; then
    echo "❌ .env file not found"
    exit 1
fi

# Run tests
echo "🧪 Running tests..."
python -m pytest tests/ -v || {
    echo "❌ Tests failed"
    exit 1
}

# Run system health check
echo "🏥 Running system health check..."
python scripts/validation/test_system_health.py || {
    echo "❌ System health check failed"
    exit 1
}

echo "✅ Deployment validation completed successfully!"
echo "🔗 System is ready for production deployment"
