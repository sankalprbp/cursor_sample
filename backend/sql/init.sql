-- Voice Agent Platform Database Initialization
-- This script creates initial data and indexes for the platform

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create indexes for better performance (only if tables exist)
-- These indexes will be created by the application after tables are created

-- Initial data insertion will be handled by the application after table creation
-- The following sections are commented out until tables are created by the backend application

/*
-- Insert initial super admin user (password: admin123)
-- Note: In production, this should be changed immediately
INSERT INTO users (
    id,
    email,
    username,
    hashed_password,
    first_name,
    last_name,
    role,
    is_active,
    is_verified,
    tenant_id
) VALUES (
    uuid_generate_v4(),
    'admin@voiceagent.platform',
    'superadmin',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', -- admin123
    'Super',
    'Admin',
    'super_admin',
    true,
    true,
    null
) ON CONFLICT (email) DO NOTHING;

-- Insert demo tenant for testing
INSERT INTO tenants (
    id,
    name,
    subdomain,
    email,
    phone,
    status,
    is_active,
    agent_name,
    agent_personality,
    max_monthly_calls,
    max_concurrent_calls,
    max_knowledge_docs,
    max_storage_mb
) VALUES (
    uuid_generate_v4(),
    'Demo Company',
    'demo',
    'demo@example.com',
    '+1-555-0123',
    'trial',
    true,
    'AI Assistant',
    'You are a helpful and professional AI assistant representing Demo Company. You are knowledgeable, friendly, and always aim to provide accurate information.',
    1000,
    10,
    100,
    5000
) ON CONFLICT (subdomain) DO NOTHING;

-- Get the demo tenant ID for creating demo user
DO $$
DECLARE
    demo_tenant_id UUID;
BEGIN
    SELECT id INTO demo_tenant_id FROM tenants WHERE subdomain = 'demo';
    
    IF demo_tenant_id IS NOT NULL THEN
        -- Insert demo tenant admin user
        INSERT INTO users (
            id,
            email,
            username,
            hashed_password,
            first_name,
            last_name,
            role,
            is_active,
            is_verified,
            tenant_id
        ) VALUES (
            uuid_generate_v4(),
            'admin@demo.com',
            'demoadmin',
            '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', -- admin123
            'Demo',
            'Admin',
            'tenant_admin',
            true,
            true,
            demo_tenant_id
        ) ON CONFLICT (email) DO NOTHING;
        
        -- Insert demo tenant subscription
        INSERT INTO tenant_subscriptions (
            id,
            tenant_id,
            plan,
            status,
            monthly_price,
            price_per_call,
            current_period_start,
            current_period_end
        ) VALUES (
            uuid_generate_v4(),
            demo_tenant_id,
            'basic',
            'active',
            29.99,
            0.05,
            CURRENT_DATE,
            CURRENT_DATE + INTERVAL '1 month'
        ) ON CONFLICT (tenant_id) DO NOTHING;
        
        -- Insert demo knowledge base
        INSERT INTO knowledge_bases (
            id,
            tenant_id,
            name,
            description,
            is_active,
            is_default
        ) VALUES (
            uuid_generate_v4(),
            demo_tenant_id,
            'Company Information',
            'General information about Demo Company including services, policies, and FAQ',
            true,
            true
        );
    END IF;
END $$;

-- Create stored procedure for monthly usage reset
CREATE OR REPLACE FUNCTION reset_monthly_usage()
RETURNS void AS $$
BEGIN
    UPDATE tenants 
    SET current_month_calls = 0 
    WHERE EXTRACT(day FROM CURRENT_DATE) = 1;
END;
$$ LANGUAGE plpgsql;

-- Create stored procedure for cleanup old data
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS void AS $$
BEGIN
    -- Delete old webhook events (older than 30 days)
    DELETE FROM webhook_events 
    WHERE created_at < CURRENT_DATE - INTERVAL '30 days'
    AND status IN ('delivered', 'expired');
    
    -- Archive old call transcripts (older than 1 year)
    UPDATE call_transcripts 
    SET full_transcript = NULL, conversation_json = NULL
    WHERE created_at < CURRENT_DATE - INTERVAL '1 year';
    
    -- Delete old usage metrics (older than 2 years, keep monthly aggregates)
    DELETE FROM usage_metrics 
    WHERE created_at < CURRENT_DATE - INTERVAL '2 years'
    AND aggregation_level = 'daily';
END;
$$ LANGUAGE plpgsql;
*/