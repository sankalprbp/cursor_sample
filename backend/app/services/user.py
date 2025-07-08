"""
User Service
Handles user management operations
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserFilters
from app.services.auth import auth_service
from app.core.logging import logger


class UserService:
    """Service for user management operations"""
    
    async def get_user(
        self, 
        db: AsyncSession, 
        user_id: UUID,
        tenant_id: Optional[UUID] = None
    ) -> Optional[User]:
        """Get user by ID with optional tenant filtering"""
        try:
            query = select(User).where(User.id == user_id)
            
            # Apply tenant filter if provided
            if tenant_id:
                query = query.where(User.tenant_id == tenant_id)
            
            result = await db.execute(query.options(selectinload(User.tenant)))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving user"
            )
    
    async def get_user_by_email(
        self, 
        db: AsyncSession, 
        email: str,
        tenant_id: Optional[UUID] = None
    ) -> Optional[User]:
        """Get user by email with optional tenant filtering"""
        try:
            query = select(User).where(User.email == email)
            
            if tenant_id:
                query = query.where(User.tenant_id == tenant_id)
            
            result = await db.execute(query.options(selectinload(User.tenant)))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {str(e)}")
            return None
    
    async def list_users(
        self,
        db: AsyncSession,
        tenant_id: Optional[UUID] = None,
        filters: Optional[UserFilters] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """List users with optional filtering"""
        try:
            # Base query
            query = select(User)
            count_query = select(func.count()).select_from(User)
            
            # Apply tenant filter
            if tenant_id:
                query = query.where(User.tenant_id == tenant_id)
                count_query = count_query.where(User.tenant_id == tenant_id)
            
            # Apply additional filters
            if filters:
                if filters.role:
                    query = query.where(User.role == filters.role)
                    count_query = count_query.where(User.role == filters.role)
                
                if filters.is_active is not None:
                    query = query.where(User.is_active == filters.is_active)
                    count_query = count_query.where(User.is_active == filters.is_active)
                
                if filters.is_verified is not None:
                    query = query.where(User.is_verified == filters.is_verified)
                    count_query = count_query.where(User.is_verified == filters.is_verified)
                
                if filters.search:
                    search_filter = or_(
                        User.email.ilike(f"%{filters.search}%"),
                        User.username.ilike(f"%{filters.search}%"),
                        User.first_name.ilike(f"%{filters.search}%"),
                        User.last_name.ilike(f"%{filters.search}%")
                    )
                    query = query.where(search_filter)
                    count_query = count_query.where(search_filter)
            
            # Get total count
            total_result = await db.execute(count_query)
            total = total_result.scalar()
            
            # Apply pagination
            query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
            query = query.options(selectinload(User.tenant))
            
            # Execute query
            result = await db.execute(query)
            users = result.scalars().all()
            
            return {
                "users": users,
                "total": total,
                "skip": skip,
                "limit": limit
            }
            
        except Exception as e:
            logger.error(f"Error listing users: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving users"
            )
    
    async def create_user(
        self,
        db: AsyncSession,
        user_create: UserCreate,
        tenant_id: Optional[UUID] = None,
        created_by: Optional[UUID] = None
    ) -> User:
        """Create a new user"""
        try:
            # Check if user with email already exists
            existing_user = await self.get_user_by_email(db, user_create.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email already exists"
                )
            
            # Create user instance
            user = User(
                email=user_create.email,
                username=user_create.username,
                first_name=user_create.first_name,
                last_name=user_create.last_name,
                hashed_password=auth_service.get_password_hash(user_create.password),
                role=user_create.role or UserRole.USER,
                tenant_id=tenant_id or user_create.tenant_id,
                is_active=user_create.is_active if user_create.is_active is not None else True,
                is_verified=False
            )
            
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            logger.info(f"Created user {user.id} with email {user.email}")
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating user"
            )
    
    async def update_user(
        self,
        db: AsyncSession,
        user_id: UUID,
        user_update: UserUpdate,
        tenant_id: Optional[UUID] = None
    ) -> User:
        """Update user information"""
        try:
            # Get existing user
            user = await self.get_user(db, user_id, tenant_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Update fields
            update_data = user_update.dict(exclude_unset=True)
            
            # Handle password update separately
            if "password" in update_data:
                user.hashed_password = auth_service.get_password_hash(update_data.pop("password"))
            
            # Update other fields
            for field, value in update_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            
            await db.commit()
            await db.refresh(user)
            
            logger.info(f"Updated user {user_id}")
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {str(e)}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating user"
            )
    
    async def delete_user(
        self,
        db: AsyncSession,
        user_id: UUID,
        tenant_id: Optional[UUID] = None,
        soft_delete: bool = True
    ) -> bool:
        """Delete user (soft delete by default)"""
        try:
            user = await self.get_user(db, user_id, tenant_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            if soft_delete:
                # Soft delete - just deactivate
                user.is_active = False
                await db.commit()
            else:
                # Hard delete
                await db.delete(user)
                await db.commit()
            
            logger.info(f"Deleted user {user_id} (soft_delete={soft_delete})")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting user"
            )
    
    async def verify_user(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> User:
        """Verify user email"""
        try:
            user = await self.get_user(db, user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            user.is_verified = True
            await db.commit()
            await db.refresh(user)
            
            logger.info(f"Verified user {user_id}")
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error verifying user {user_id}: {str(e)}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error verifying user"
            )
    
    async def get_user_permissions(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> List[str]:
        """Get user permissions based on role"""
        try:
            user = await self.get_user(db, user_id)
            if not user:
                return []
            
            # Define permissions based on role
            permissions_map = {
                UserRole.SUPER_ADMIN: [
                    "users:read", "users:write", "users:delete",
                    "tenants:read", "tenants:write", "tenants:delete",
                    "billing:read", "billing:write",
                    "system:admin"
                ],
                UserRole.TENANT_ADMIN: [
                    "users:read", "users:write",
                    "tenants:read",
                    "billing:read",
                    "knowledge:read", "knowledge:write",
                    "calls:read", "calls:write",
                    "analytics:read"
                ],
                UserRole.USER: [
                    "users:read:self",
                    "knowledge:read",
                    "calls:read",
                    "analytics:read"
                ]
            }
            
            return permissions_map.get(user.role, [])
            
        except Exception as e:
            logger.error(f"Error getting user permissions: {str(e)}")
            return []


# Create service instance
user_service = UserService()