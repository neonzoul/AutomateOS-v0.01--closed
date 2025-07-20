# AutomateOS MVP

> A portfolio-defining workflow automation platform - your personal "operating system" for automation

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)

## 🚀 Overview

AutomateOS is a simplified, self-hosted workflow automation tool inspired by platforms like Zapier and n8n. Built as a portfolio project to demonstrate advanced full-stack development skills, it showcases modern architecture patterns including asynchronous processing, event-driven design, and scalable API-based components.

**Target Audience:** Developers, Software Engineers, Startups, and Software Solopreneurs who need a personal automation platform.

## ✨ Key Features

### Core Functionality
- **🔐 Secure Authentication** - JWT-based user registration and login system
- **📊 Workflow Dashboard** - Central hub for managing automation workflows
- **⚡ Webhook Triggers** - External services can initiate workflows via HTTP requests
- **🔗 HTTP Request Actions** - Integrate with any external API
- **🔍 Conditional Logic** - Filter nodes for dynamic workflow control
- **📝 Execution Logging** - Complete history and monitoring of workflow runs

### Technical Highlights
- **Asynchronous Processing** - Background workers ensure responsive API performance
- **Event-Driven Architecture** - Scalable trigger-action workflow model
- **Modern Tech Stack** - FastAPI, React, PostgreSQL, Redis
- **Production Ready** - Deployed on Render with CI/CD pipeline

## 🏗️ Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[React Frontend<br/>Vite + Chakra UI]
    end
    
    subgraph "API Layer"
        API[FastAPI Web Server<br/>JWT Auth + CORS]
    end
    
    subgraph "Processing Layer"
        QUEUE[Redis Queue<br/>RQ Task Broker]
        WORKER[Background Workers<br/>Workflow Execution]
    end
    
    subgraph "Data Layer"
        DB[(PostgreSQL<br/>User, Workflow, Logs)]
        REDIS[(Redis<br/>Queue + Cache)]
    end
    
    subgraph "External"
        WEBHOOK[Webhook Triggers]
        APIS[External APIs]
    end
    
    UI --> API
    API --> DB
    API --> QUEUE
    QUEUE --> WORKER
    WORKER --> DB
    WORKER --> APIS
    WEBHOOK --> API
```

## 🛠️ Technology Stack

### Backend
- **FastAPI** - High-performance Python web framework with automatic OpenAPI docs
- **SQLModel** - Unified data modeling combining Pydantic validation with SQLAlchemy ORM
- **PostgreSQL** - Production database with SQLite for local development
- **RQ + Redis** - Lightweight task queue for asynchronous workflow execution
- **JWT Authentication** - Token-based auth with passlib/bcrypt password hashing

### Frontend
- **React 18** - Component-based UI with modern hooks and context
- **Vite** - Fast development server and optimized production builds
- **Chakra UI** - Comprehensive component library for rapid UI development
- **Axios** - HTTP client for API communication with auth interceptors

### Infrastructure
- **Render** - Cloud platform for web services, workers, and managed databases
- **GitHub Actions** - CI/CD pipeline for automated deployments
- **Docker** - Containerization for consistent environments

## 🚦 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL (or SQLite for development)
- Redis

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/automate-os-mvp.git
   cd automate-os-mvp
   ```

2. **Backend Setup**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Set environment variables
   cp .env.example .env
   # Edit .env with your database and Redis URLs
   
   # Run database migrations
   alembic upgrade head
   
   # Start the API server
   uvicorn main:app --reload
   ```

3. **Frontend Setup**
   ```bash
   # Navigate to frontend directory
   cd frontend
   
   # Install dependencies
   npm install
   
   # Start development server
   npm run dev
   ```

4. **Start Background Worker**
   ```bash
   # In a new terminal, activate venv and run:
   python worker.py
   ```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📖 API Documentation

The FastAPI backend automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register` | POST | User registration |
| `/api/v1/auth/token` | POST | User login (JWT) |
| `/api/v1/workflows` | GET/POST | List/Create workflows |
| `/api/v1/workflows/{id}` | GET/PUT/DELETE | Manage specific workflow |
| `/api/v1/workflows/{id}/execute` | POST | Webhook trigger endpoint |
| `/api/v1/logs/{workflow_id}` | GET | Execution history |

## 🔧 Usage Examples

### Creating a Simple Workflow

1. **Register/Login** to access the dashboard
2. **Create New Workflow** from the dashboard
3. **Add Nodes** in the workflow editor:
   - Start with a **Webhook Trigger**
   - Add an **HTTP Request** action to call an external API
   - Optionally add a **Filter** for conditional logic
4. **Save** the workflow to generate a unique webhook URL
5. **Trigger** the workflow by sending a POST request to the webhook URL

### Sample Workflow Configuration

```json
{
  "nodes": [
    {
      "id": "trigger-1",
      "type": "webhook",
      "config": {
        "method": "POST",
        "path": "/webhook/abc123"
      }
    },
    {
      "id": "action-1", 
      "type": "http_request",
      "config": {
        "url": "https://api.example.com/data",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": "{{trigger.payload}}"
      }
    }
  ],
  "connections": [
    {"from": "trigger-1", "to": "action-1"}
  ]
}
```

## 🧪 Testing

### Backend Tests
```bash
# Run unit tests
pytest

# Run with coverage
pytest --cov=app tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
# Run end-to-end tests
pytest tests/integration/
```

## 🚀 Deployment

### Production Deployment on Render

1. **Fork this repository** to your GitHub account

2. **Create services on Render**:
   - PostgreSQL database
   - Redis instance
   - Web Service (FastAPI app)
   - Background Worker (RQ worker)

3. **Configure environment variables**:
   ```
   DATABASE_URL=postgresql://...
   REDIS_URL=redis://...
   SECRET_KEY=your-secret-key
   ```

4. **Deploy** - Render will automatically deploy from your GitHub repository

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `SECRET_KEY` | JWT signing secret | `your-super-secret-key` |
| `ENVIRONMENT` | Deployment environment | `development` or `production` |

## 📊 Project Status

This project represents a **6-week MVP** demonstrating:

- ✅ **Week 1**: Project setup and core models
- ✅ **Week 2**: Secure user authentication
- ✅ **Week 3**: Workflow CRUD operations
- ✅ **Week 4**: Workflow editor interface
- ✅ **Week 5**: Asynchronous execution engine
- ✅ **Week 6**: Production deployment

## 🔮 Future Enhancements

### Planned Features (Post-MVP)
- **Notion API Integration** - Create Notion pages as workflow actions
- **Scheduled Triggers** - Cron-based workflow execution
- **Advanced Node Types** - Email, Slack, and other service integrations
- **Real-time Updates** - WebSocket-based live execution monitoring
- **Drag-and-Drop Editor** - Visual workflow builder interface
- **CLI Tool** - Command-line interface for workflow management

## 🤝 Contributing

This is a portfolio project, but contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by [n8n](https://n8n.io/) and [Zapier](https://zapier.com/) architectures
- Built following modern full-stack development best practices
- Designed as a portfolio project to demonstrate advanced software engineering skills

---

**AutomateOS** - Transforming ideas into automated workflows, one trigger at a time. 🚀