# Docker Startup Issues - Fixes Applied

## 🚨 **Issues Identified from Logs**

### 1. **Database Initialization Error**
```
postgres | ERROR: relation "users" does not exist
postgres | STATEMENT: CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON users(tenant_id);
```

### 2. **Nginx Configuration Error**
```
nginx | [emerg] host not found in upstream "frontend:3000" in /etc/nginx/nginx.conf:49
```

### 3. **Sample Data Duplication Error**
```
backend | ERROR: duplicate key value violates unique constraint "ix_tenants_subdomain"
backend | DETAIL: Key (subdomain)=(demo) already exists.
```

### 4. **Service Startup Order Issues**
- Nginx trying to connect to services before they're ready
- No health checks to ensure proper startup order

---

## ✅ **Fixes Applied**

### 1. **Fixed Database Initialization Script** (`backend/sql/init.sql`)
**Problem**: Script was trying to create indexes on tables that didn't exist yet.

**Solution**: 
- Removed all table-specific operations from init.sql
- Only kept UUID extension creation
- All tables and indexes now created by backend application

**Changes**:
```sql
-- Before: Complex script with table operations
-- After: Simple extension creation only
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### 2. **Fixed Sample Data Creation** (`backend/app/core/database_init.py`)
**Problem**: Backend was trying to create sample data that already existed, causing duplicate key errors.

**Solution**:
- Added check for existing demo tenant before creation
- Changed error handling to log warnings instead of failing
- Made sample data creation idempotent

**Changes**:
```python
# Check if demo tenant already exists
existing_tenant = await session.get(Tenant, "b1244b00-5bb5-4f55-94e3-720d683ae82c")
if existing_tenant:
    print("ℹ️  Sample data creation skipped: Demo tenant already exists")
    return
```

### 3. **Enhanced Nginx Configuration** (`nginx/nginx.conf`)
**Problem**: Nginx couldn't find upstream services during startup.

**Solution**:
- Added health checks and fail_timeout to upstream servers
- Added dedicated health check endpoint
- Improved error handling and retry logic

**Changes**:
```nginx
upstream backend {
    server backend:8000 max_fails=3 fail_timeout=30s;
}

upstream frontend {
    server frontend:3000 max_fails=3 fail_timeout=30s;
}
```

### 4. **Updated Docker Compose** (`docker-compose.yml`)
**Problem**: Services starting in wrong order, no health checks.

**Solution**:
- Added health checks for all services
- Updated dependencies to use health check conditions
- Added proper startup timeouts

**Changes**:
```yaml
depends_on:
  postgres:
    condition: service_healthy
  redis:
    condition: service_healthy
```

---

## 🔧 **Health Checks Added**

### PostgreSQL
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 10s
  timeout: 5s
  retries: 5
```

### Redis
```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 10s
  timeout: 5s
  retries: 5
```

### Backend
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Frontend
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:3000"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

---

## � **Startup Order**

1. **PostgreSQL** → Health check passes
2. **Redis** → Health check passes  
3. **Backend** → Waits for PostgreSQL & Redis, then starts
4. **Frontend** → Waits for Backend, then starts
5. **Nginx** → Waits for both Frontend & Backend, then starts

---

## 🧪 **Testing**

Created `test_startup.py` to verify fixes:
- Tests health endpoints for all services
- Verifies API endpoints are accessible
- Checks nginx proxy functionality

Run with:
```bash
python test_startup.py
```

---

## 📋 **Expected Results**

After applying these fixes:

✅ **PostgreSQL** starts without table creation errors  
✅ **Backend** starts without sample data conflicts  
✅ **Frontend** starts and is accessible  
✅ **Nginx** starts without upstream errors  
✅ **All services** start in correct order  
✅ **Health checks** pass for all services  

---

## 🔄 **Next Steps**

1. **Rebuild and restart services**:
   ```bash
   docker-compose down
   docker-compose up --build
   ```

2. **Verify startup**:
   ```bash
   python test_startup.py
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Nginx Proxy: http://localhost

---

## 📝 **Notes**

- All fixes are backward compatible
- Health checks ensure reliable startup
- Error handling is now graceful
- Services can restart independently
- Development and production configurations supported