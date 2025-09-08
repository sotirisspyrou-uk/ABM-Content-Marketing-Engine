# Quick Start Guide - ABM Content Marketing Engine

## 1. Environment Setup (2 minutes)
```bash
# Run the setup script
chmod +x setup_project.sh && ./setup_project.sh
cd abm-content-engine

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

## 2. Database & HubSpot Setup (3 minutes)
```bash
# Database initialization
python scripts/setup/database_setup.py

# HubSpot configuration
python scripts/setup/hubspot_setup.py
```

## 3. Start & Validate (2 minutes)
```bash
# Install dependencies
pip install -r requirements.txt

# Start the system
python main.py

# Validate system health (in another terminal)
python scripts/validation/test_system_health.py
```

## 4. Access Your System
- **API Health**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs
- **Basic UI**: http://localhost:3000 (optional)

## Success Indicators
- ✅ All health checks pass
- ✅ HubSpot properties created
- ✅ Database tables initialized  
- ✅ API endpoints responding

**You're ready to implement enterprise ABM automation!**
