# Real Estate Rental Backend

A comprehensive FastAPI-based backend for managing rental properties with user authentication, property management, image storage, and rental applications.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL (local installation)
- MinIO (installed via homebrew: `brew install minio`)

### Setup

1. **Clone and navigate to backend**
   ```bash
   cd real-estate/back-end
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

3. **Start everything**
   ```bash
   ./start.sh
   ```

That's it! The script will:
- Create virtual environment and install dependencies
- Start MinIO server with sample images
- Setup database tables and sample data
- Start the FastAPI server

### Access Points
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)

## 🏗 Architecture

### Core Features
- **User Management**: Registration, authentication, role-based access
- **Property Management**: CRUD operations with advanced search
- **Image Storage**: MinIO integration for property photos
- **Rental Applications**: Submit and manage rental applications
- **Role System**: Tenant, Landlord, and Admin roles

### Tech Stack
- **FastAPI**: Modern async web framework
- **PostgreSQL**: Database with SQLAlchemy ORM
- **MinIO**: S3-compatible object storage
- **JWT**: Authentication tokens
- **Pydantic**: Data validation

## 📁 Project Structure

```
back-end/
├── app.py                 # Main FastAPI application
├── config.py             # Configuration settings
├── database.py           # Database models and connection
├── auth.py               # Authentication logic
├── schemas.py            # Pydantic schemas
├── routers/              # API route handlers
│   ├── auth.py
│   ├── properties.py
│   └── applications.py
├── start.sh              # Startup script
├── setup_database.py     # Database initialization
└── setup_complete_minio.py # MinIO setup
```

## 🔧 Manual Setup (if needed)

### Database Setup
```bash
# Create database
createdb real-estate-rental

# Initialize tables and sample data
python3 setup_database.py
```

### MinIO Setup
```bash
# Start MinIO manually
minio server minio-data --console-address ":9001"

# Setup bucket and images (in another terminal)
python3 setup_complete_minio.py
```

### Start API Server
```bash
# Activate virtual environment
source .venv/bin/activate

# Start FastAPI server
python3 -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## 🔐 Authentication

The API uses JWT tokens for authentication. Users have roles:
- **Tenant**: Can search properties, submit applications
- **Landlord**: Can manage their properties, view applications
- **Admin**: Full system access

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### Properties
- `GET /api/properties/` - List properties (with filters)
- `GET /api/properties/{id}` - Get property details
- `POST /api/properties/` - Create property (landlord only)
- `PUT /api/properties/{id}` - Update property
- `DELETE /api/properties/{id}` - Delete property

### Applications
- `GET /api/applications/` - List applications
- `POST /api/applications/` - Submit application
- `PUT /api/applications/{id}` - Update application status

## 🐛 Troubleshooting

### Database Issues
```bash
# Check PostgreSQL is running
brew services list | grep postgresql

# Start PostgreSQL if needed
brew services start postgresql@14
```

### MinIO Issues
```bash
# Check MinIO is running
curl http://localhost:9000/minio/health/live

# Access MinIO console
open http://localhost:9001
```

### Port Conflicts
```bash
# Check what's using port 8000
lsof -i :8000

# Kill process if needed
lsof -ti:8000 | xargs kill -9
```

## 📝 Development

### Adding New Features
1. Update database models in `database.py`
2. Create/update Pydantic schemas in `schemas.py`
3. Add route handlers in appropriate router file
4. Update tests and documentation

### Database Migrations
Currently using SQLAlchemy's `create_all()`. For production, consider using Alembic for proper migrations.

## 🔄 Frontend Integration

The backend is designed to work with the React frontend in the `renting-front` directory. Make sure both are running:

- Backend: http://localhost:8000
- Frontend: http://localhost:8080

CORS is configured to allow requests from the frontend.
