"""
Database Initialization Script
Creates tables and populates with sample data for development
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from uuid import uuid4

from app.core.database import async_session_maker, Base, engine
from app.models.user import User, UserRole
from app.models.tenant import Tenant, TenantStatus, TenantSubscription, SubscriptionPlan
from app.models.billing import UsageMetric, UsageType
try:
    from app.services.auth import auth_service
except ImportError:
    # Fallback password hashing if auth service isn't available
    import hashlib
    class FallbackAuthService:
        @staticmethod
        def get_password_hash(password: str) -> str:
            return hashlib.sha256(password.encode()).hexdigest()
    auth_service = FallbackAuthService()


async def create_tables():
    """Create all database tables"""
    print("🔧 Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully!")


async def create_sample_data():
    """Create sample data for development"""
    print("🔧 Creating sample data...")
    
    async with async_session_maker() as session:
        try:
            # Check if demo tenant already exists by subdomain
            existing_tenant = await session.scalar(
                select(Tenant).where(Tenant.subdomain == "demo")
            )
            if existing_tenant:
                print("ℹ️  Sample data creation skipped: Demo tenant already exists")
                return
            
            # Create default tenant
            tenant = Tenant(
                id=uuid4(),
                name="Demo Company",
                subdomain="demo",
                email="admin@demo.com",
                phone="+1-555-0123",
                status=TenantStatus.ACTIVE,
                agent_name="AI Assistant",
                agent_personality="Friendly and professional customer service assistant",
                agent_instructions="Help customers with their inquiries. Be polite and helpful.",
                max_monthly_calls=1000,
                max_concurrent_calls=10,
                max_knowledge_docs=100,
                max_storage_mb=5000
            )
            session.add(tenant)
            await session.flush()  # Get the tenant ID
            
            # Create tenant subscription
            subscription = TenantSubscription(
                tenant_id=tenant.id,
                plan=SubscriptionPlan.PROFESSIONAL,
                status="active",
                monthly_price=99.00,
                price_per_call=0.10,
                current_period_start=datetime.now(timezone.utc),
                current_period_end=datetime.now(timezone.utc).replace(month=datetime.now().month + 1)
            )
            session.add(subscription)
            
            # Create super admin user
            super_admin = User(
                id=uuid4(),
                email="admin@voiceagent.com",
                username="superadmin",
                hashed_password=auth_service.get_password_hash("admin123"),
                first_name="Super",
                last_name="Admin",
                role=UserRole.SUPER_ADMIN,
                is_active=True,
                is_verified=True
            )
            session.add(super_admin)
            
            # Create tenant admin user
            tenant_admin = User(
                id=uuid4(),
                email="admin@demo.com",
                username="admin",
                hashed_password=auth_service.get_password_hash("demo123"),
                first_name="Demo",
                last_name="Admin",
                role=UserRole.TENANT_ADMIN,
                tenant_id=tenant.id,
                is_active=True,
                is_verified=True
            )
            session.add(tenant_admin)
            
            # Create regular user
            regular_user = User(
                id=uuid4(),
                email="user@demo.com",
                username="user",
                hashed_password=auth_service.get_password_hash("user123"),
                first_name="Demo",
                last_name="User",
                role=UserRole.TENANT_USER,
                tenant_id=tenant.id,
                is_active=True,
                is_verified=True
            )
            session.add(regular_user)

            # Sample usage metric
            metric = UsageMetric(
                tenant_id=tenant.id,
                metric_type=UsageType.CALLS,
                metric_name="demo_calls",
                date=datetime.now(timezone.utc).date(),
                count=5,
                unit_price_usd=0.10,
                billing_unit="call",
                cost_usd=0.50,
            )
            session.add(metric)
            
            await session.commit()
            
            print("✅ Sample data created successfully!")
            print("\n🔑 Test Accounts Created:")
            print("📧 Super Admin: admin@voiceagent.com / admin123")
            print("📧 Tenant Admin: admin@demo.com / demo123")
            print("📧 Regular User: user@demo.com / user123")
            
        except Exception as e:
            await session.rollback()
            print(f"ℹ️  Sample data creation skipped: {e}")
            # Don't raise the exception, just log it


async def initialize_database():
    """Initialize database with tables and sample data"""
    print("🚀 Initializing Voice Agent Database...")
    print("=" * 50)
    
    try:
        # Create tables
        await create_tables()
        
        # Create sample data
        await create_sample_data()
        
        print("\n" + "=" * 50)
        print("🎉 Database initialization completed successfully!")
        print("\n🔗 Next Steps:")
        print("1. Start the backend server: uvicorn main:app --reload")
        print("2. Access API docs: http://localhost:8000/docs")
        print("3. Test authentication with the accounts above")
        
    except Exception as e:
        print(f"\n❌ Database initialization failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(initialize_database())