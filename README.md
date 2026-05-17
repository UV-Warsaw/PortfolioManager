# PortfolioManager

A full-stack web application for managing and analyzing investment portfolios with a cinematic dark theme interface.

## Architecture

- **Backend**: FastAPI + SQLAlchemy + Pydantic
- **Frontend**: Vite + React + TypeScript
- **Database**: PostgreSQL (production) / SQLite (local dev)
- **Testing**: Pytest (backend)
- **Containerization**: Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)
- Poetry (for backend dependency management)

### Running with Docker Compose

1. **Clone the repository**
   ```bash
   git clone git@github.com:UV-Warsaw/PortfolioManager.git
   cd PortfolioManager
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start all services**
   ```bash
   docker compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - PostgreSQL: localhost:5432

### Stopping Services

```bash
docker compose down
```

To remove volumes (database data):
```bash
docker compose down -v
```

## Local Development

### Backend

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
cd backend
poetry run pytest -v
```

## Project Structure

```
PortfolioManager/
├── docker-compose.yml
├── .env.example
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── app/
│       ├── main.py
│       ├── core/
│       ├── models/
│       ├── repositories/
│       ├── routers/
│       ├── schemas/
│       └── services/
└── frontend/
    ├── Dockerfile
    ├── package.json
    └── src/
        ├── components/
        ├── services/
        └── types/
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | - |
| `DEBUG` | Enable debug mode | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `SECRET_KEY` | Application secret key | - |
| `CORS_ORIGINS` | Allowed CORS origins | `[]` |
| `VITE_API_URL` | Backend API URL for frontend | `http://localhost:8000` |

## Contributing

1. Create a feature branch from `main`
2. Make your changes
3. Run tests and linting
4. Create a pull request

## License

MIT
