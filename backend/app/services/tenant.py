"""
Tenant Service
Handles tenant management operations
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.tenant import Tenant, TenantStatus, TenantSubscription, SubscriptionPlan
from app.models.user import User, UserRole
from app.schemas.tenant import TenantCreate, TenantUpdate, TenantFilters
from app.core.logging import logger


class TenantService:
    """Service for tenant management operations"""
    
    async def get_tenant(
        self, 
        db: AsyncSession, 
        tenant_id: UUID
    ) -> Optional[Tenant]:
        """Get tenant by ID"""
        try:
            query = select(Tenant).where(Tenant.id == tenant_id)
            query = query.options(
                selectinload(Tenant.subscription)
            )
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting tenant {tenant_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving tenant"
            )
    
    async def get_tenant_by_name(
        self, 
        db: AsyncSession, 
        name: str
    ) -> Optional[Tenant]:
        """Get tenant by name"""
        try:
            query = select(Tenant).where(Tenant.name == name)
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting tenant by name {name}: {str(e)}")
            return None
    
    async def list_tenants(
        self,
        db: AsyncSession,
        filters: Optional[TenantFilters] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """List tenants with optional filtering"""
        try:
            # Base query
            query = select(Tenant)
            count_query = select(func.count()).select_from(Tenant)
            
            # Apply filters
            if filters:
                if filters.status:
                    query = query.where(Tenant.status == filters.status)
                    count_query = count_query.where(Tenant.status == filters.status)
                
                if filters.search:
                    search_filter = or_(
                        Tenant.name.ilike(f"%{filters.search}%"),
                        Tenant.email.ilike(f"%{filters.search}%"),
                        Tenant.company_size.ilike(f"%{filters.search}%")
                    )
                    query = query.where(search_filter)
                    count_query = count_query.where(search_filter)
                
                if filters.created_after:
                    query = query.where(Tenant.created_at >= filters.created_after)
                    count_query = count_query.where(Tenant.created_at >= filters.created_after)
                
                if filters.created_before:
                    query = query.where(Tenant.created_at <= filters.created_before)
                    count_query = count_query.where(Tenant.created_at <= filters.created_before)
            
            # Get total count
            total_result = await db.execute(count_query)
            total = total_result.scalar()
            
            # Apply pagination
            query = query.offset(skip).limit(limit).order_by(Tenant.created_at.desc())
            query = query.options(
                selectinload(Tenant.subscription)
            )
            
            # Execute query
            result = await db.execute(query)
            tenants = result.scalars().all()
            
            return {
                "tenants": tenants,
                "total": total,
                "skip": skip,
                "limit": limit
            }
            
        except Exception as e:
            logger.error(f"Error listing tenants: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving tenants"
            )
    
    async def create_tenant(
        self,
        db: AsyncSession,
        tenant_create: TenantCreate,
        created_by: UUID
    ) -> Tenant:
        """Create a new tenant"""
        try:
            # Check if tenant with name already exists
            existing_tenant = await self.get_tenant_by_name(db, tenant_create.name)
            if existing_tenant:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tenant with this name already exists"
                )
            
            # Create tenant instance
            tenant = Tenant(
                name=tenant_create.name,
                email=tenant_create.contact_email,
                phone=tenant_create.contact_phone,
                industry=tenant_create.industry,
                company_size=tenant_create.size,
                status=TenantStatus.TRIAL,  # Start with trial status
                trial_starts_at=datetime.utcnow(),
                trial_ends_at=datetime.utcnow() + timedelta(days=14)  # 14-day trial
            )
            
            db.add(tenant)
            await db.flush()  # Get tenant ID before creating related objects
            
            # Create default subscription (trial)
            subscription = TenantSubscription(
                tenant_id=tenant.id,
                plan=SubscriptionPlan.FREE,
                status="active",
                current_period_start=datetime.utcnow(),
                current_period_end=datetime.utcnow() + timedelta(days=30),
                cancel_at_period_end=False
            )
            db.add(subscription)
            
            await db.commit()
            await db.refresh(tenant)
            
            logger.info(f"Created tenant {tenant.id} with name {tenant.name}")
            return tenant
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating tenant: {str(e)}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating tenant"
            )
    
    async def update_tenant(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        tenant_update: TenantUpdate
    ) -> Tenant:
        """Update tenant information"""
        try:
            # Get existing tenant
            tenant = await self.get_tenant(db, tenant_id)
            if not tenant:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tenant not found"
                )
            
            # Update fields
            update_data = tenant_update.dict(exclude_unset=True)
            
            # Update fields directly on tenant
            for field, value in update_data.items():
                if hasattr(tenant, field):
                    setattr(tenant, field, value)
            
            await db.commit()
            await db.refresh(tenant)
            
            logger.info(f"Updated tenant {tenant_id}")
            return tenant
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating tenant {tenant_id}: {str(e)}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating tenant"
            )
    
    async def delete_tenant(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        soft_delete: bool = True
    ) -> bool:
        """Delete tenant (soft delete by default)"""
        try:
            tenant = await self.get_tenant(db, tenant_id)
            if not tenant:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tenant not found"
                )
            
            if soft_delete:
                # Soft delete - set status to cancelled
                tenant.status = TenantStatus.CANCELLED
                
                # Deactivate all users
                user_query = select(User).where(User.tenant_id == tenant_id)
                users_result = await db.execute(user_query)
                users = users_result.scalars().all()
                
                for user in users:
                    user.is_active = False
                
                await db.commit()
            else:
                # Hard delete - not recommended
                await db.delete(tenant)
                await db.commit()
            
            logger.info(f"Deleted tenant {tenant_id} (soft_delete={soft_delete})")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting tenant {tenant_id}: {str(e)}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting tenant"
            )
    
    async def suspend_tenant(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        reason: Optional[str] = None
    ) -> Tenant:
        """Suspend tenant account"""
        try:
            tenant = await self.get_tenant(db, tenant_id)
            if not tenant:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tenant not found"
                )
            
            tenant.status = TenantStatus.SUSPENDED
            
            # Log suspension reason if provided
            if reason:
                logger.info(f"Suspending tenant {tenant_id} for reason: {reason}")
            
            await db.commit()
            await db.refresh(tenant)
            
            return tenant
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error suspending tenant {tenant_id}: {str(e)}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error suspending tenant"
            )
    
    async def reactivate_tenant(
        self,
        db: AsyncSession,
        tenant_id: UUID
    ) -> Tenant:
        """Reactivate suspended tenant"""
        try:
            tenant = await self.get_tenant(db, tenant_id)
            if not tenant:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tenant not found"
                )
            
            if tenant.status != TenantStatus.SUSPENDED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tenant is not suspended"
                )
            
            tenant.status = TenantStatus.ACTIVE
            
            await db.commit()
            await db.refresh(tenant)
            
            logger.info(f"Reactivated tenant {tenant_id}")
            return tenant
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error reactivating tenant {tenant_id}: {str(e)}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error reactivating tenant"
            )
    

    
    async def get_tenant_statistics(
        self,
        db: AsyncSession,
        tenant_id: UUID
    ) -> Dict[str, Any]:
        """Get tenant usage statistics"""
        try:
            tenant = await self.get_tenant(db, tenant_id)
            if not tenant:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tenant not found"
                )
            
            # Get user count
            user_count_query = select(func.count()).select_from(User).where(
                User.tenant_id == tenant_id,
                User.is_active == True
            )
            user_count_result = await db.execute(user_count_query)
            user_count = user_count_result.scalar()
            
            # Get call count (would need Call model)
            # call_count = await self.get_call_count(db, tenant_id)
            
            # Get knowledge base size (would need KnowledgeBase model)
            # kb_size = await self.get_knowledge_base_size(db, tenant_id)
            
            return {
                "tenant_id": str(tenant_id),
                "name": tenant.name,
                "status": tenant.status.value,
                "user_count": user_count,
                "created_at": tenant.created_at.isoformat(),
                "subscription": {
                    "plan": tenant.subscription.plan.value if tenant.subscription else "None",
                    "status": tenant.subscription.status if tenant.subscription else "None"
                }
                # Add more statistics as needed
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting tenant statistics: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving tenant statistics"
            )


# Create service instance
tenant_service = TenantService()