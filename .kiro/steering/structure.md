# Project Structure & Organization

## Root Directory Layout

```
voice-agent-platform/
├── backend/                 # FastAPI backend application
├── frontend/                # Next.js frontend application
├── nginx/                   # Reverse proxy configuration
├── .kiro/                   # Kiro IDE configuration and steering
├── docker-compose.yml       # Development environment orchestration
├── .env.example            # Environment variables template
├── start.sh                # Quick start script with webhook URLs
└── *.md                    # Documentation files
```

## Backend Structure (`backend/`)

```
backend/
├── app/
│   ├── api/                # API route handlers
│   │   └── v1/            # API version 1 endpoints
│   ├── core/              # Core configuration and utilities
│   │   ├── config.py      # Settings and environment configuration
│   │   ├── database.py    # Database connection and session management
│   │   └── security.py    # Authentication and security utilities
│   ├── models/            # SQLAlchemy database models
│   ├── services/          # Business logic layer (to be implemented)
│   ├── websocket/         # WebSocket connection management
│   └── tests/             # Test files
├── sql/                   # Database initialization scripts
├── main.py               # FastAPI application entry point
├── requirements.txt      # Python dependencies
└── Dockerfile           # Backend container configuration
```

## Frontend Structure (`frontend/`)

```
frontend/
├── src/
│   ├── app/              # Next.js 13+ app directory
│   ├── components/       # Reusable React components
│   ├── lib/             # Utility functions and configurations
│   ├── hooks/           # Custom React hooks
│   └── types/           # TypeScript type definitions
├── public/              # Static assets
├── package.json         # Node.js dependencies and scripts
├── next.config.js       # Next.js configuration
├── tailwind.config.js   # Tailwind CSS configuration
└── Dockerfile          # Frontend container configuration
```

## Key Architectural Patterns

### Backend Patterns
- **Layered Architecture**: API → Services → Models → Database
- **Dependency Injection**: FastAPI's built-in DI for database sessions
- **Repository Pattern**: Database access abstraction (to be implemented)
- **Multi-tenancy**: Tenant isolation at database and API level
- **WebSocket Management**: Centralized connection manager for real-time features

### Frontend Patterns
- **Component-Based**: Modular React components with TypeScript
- **Custom Hooks**: Reusable logic extraction
- **State Management**: Zustand for global state, React Query for server state
- **Form Handling**: React Hook Form with Zod schema validation
- **Responsive Design**: Mobile-first Tailwind CSS approach

## File Naming Conventions

### Backend (Python)
- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **API Endpoints**: `/api/v1/resource-name`

### Frontend (TypeScript/React)
- **Components**: `PascalCase.tsx`
- **Hooks**: `use-kebab-case.ts`
- **Utilities**: `kebab-case.ts`
- **Types**: `PascalCase` interfaces/types
- **Pages**: Next.js file-based routing

## Configuration Management

### Environment Files
- `.env.example`: Template with all required variables
- `.env`: Local development configuration (gitignored)
- Backend uses `pydantic-settings` for type-safe configuration
- Frontend uses Next.js built-in environment variable support

### Docker Configuration
- `docker-compose.yml`: Development environment with all services
- Individual `Dockerfile`s for backend and frontend
- Health checks for all services
- Volume mounts for development (commented out for production)

## Database Organization

### Multi-tenant Schema
- Tenant isolation through `tenant_id` foreign keys
- Shared tables: `tenants`, `users`, `roles`
- Tenant-specific tables: `knowledge_bases`, `calls`, `webhooks`
- Admin tables: `system_settings`, `billing_records`

### Migration Strategy
- Alembic for database migrations
- Initialization scripts in `backend/sql/`
- Sample data creation for development environment

## API Organization

### RESTful Endpoints
- `/api/v1/auth/`: Authentication and authorization
- `/api/v1/tenants/`: Tenant management
- `/api/v1/users/`: User management
- `/api/v1/voice/`: Voice agent and call handling
- `/api/v1/knowledge/`: Knowledge base management
- `/api/v1/webhooks/`: Webhook configuration
- `/api/v1/admin/`: Platform administration

### WebSocket Endpoints
- `/ws/calls/{call_id}`: Real-time call updates
- `/ws/dashboard/{tenant_id}`: Live dashboard updates

## Development Workflow

### Local Development
1. Copy `.env.example` to `.env` and configure
2. Run `docker-compose up --build` for full stack
3. Access frontend at `localhost:3000`, backend at `localhost:8000`
4. Use volume mounts for hot reloading during development

### Code Organization Principles
- **Separation of Concerns**: Clear boundaries between layers
- **Single Responsibility**: Each module has one clear purpose
- **DRY Principle**: Shared utilities and components
- **Type Safety**: Full TypeScript coverage, Python type hints
- **Error Handling**: Consistent error responses and logging