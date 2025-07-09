-- Voice Agent Platform Database Initialization
-- This script only creates the UUID extension
-- All tables and data will be created by the backend application

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Note: All table creation, indexes, and sample data will be handled by the backend application
-- This ensures proper initialization order and avoids conflicts