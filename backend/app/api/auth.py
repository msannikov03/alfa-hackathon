from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import logging

from app.database import AsyncSessionLocal
from app.models import User
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str


class UserResponse(BaseModel):
    id: int
    username: Optional[str]
    email: Optional[str]
    full_name: Optional[str]
    telegram_id: Optional[str]


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    # Ensure 'sub' is a string (JWT standard)
    if 'sub' in to_encode and isinstance(to_encode['sub'], int):
        to_encode['sub'] = str(to_encode['sub'])
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        # Convert string back to int
        user_id = int(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user is None:
            raise credentials_exception
        return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security)
) -> int:
    """
    Get current user ID from JWT token, or fall back to demo_admin user if no token provided.
    This allows Phase 2 features to work without authentication for demo purposes.
    """
    async def get_demo_user_id() -> int:
        """Get demo_admin user ID from database"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.username == "demo_admin"))
            demo_user = result.scalar_one_or_none()
            if demo_user:
                return demo_user.id
            # Fallback to user_id=1 if demo_admin doesn't exist
            return 1

    if credentials is None:
        # No authentication provided, use demo_admin user
        demo_user_id = await get_demo_user_id()
        logger.info(f"No authentication provided, using demo_admin user_id={demo_user_id}")
        return demo_user_id

    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            demo_user_id = await get_demo_user_id()
            logger.warning(f"Invalid token, falling back to demo_admin user_id={demo_user_id}")
            return demo_user_id
        # Convert string to int
        return int(user_id_str)
    except (JWTError, ValueError) as e:
        demo_user_id = await get_demo_user_id()
        logger.warning(f"JWT decode error: {e}, falling back to demo_admin user_id={demo_user_id}")
        return demo_user_id


@router.post("/register", response_model=Token)
async def register(user_data: UserRegister):
    """Register a new user"""
    async with AsyncSessionLocal() as session:
        # Check if username exists
        result = await session.execute(
            select(User).where(User.username == user_data.username)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        # Check if email exists
        result = await session.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=True,
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        # Create access token
        access_token = create_access_token(data={"sub": new_user.id})

        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=new_user.id,
            username=new_user.username or ""
        )


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """Login user"""
    async with AsyncSessionLocal() as session:
        # Find user by username
        result = await session.execute(
            select(User).where(User.username == user_data.username)
        )
        user = result.scalar_one_or_none()

        if not user or not user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )

        # Verify password
        if not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        # Create access token
        access_token = create_access_token(data={"sub": user.id})

        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            username=user.username or ""
        )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        telegram_id=current_user.telegram_id,
    )


@router.post("/set-password")
async def set_password(
    telegram_id: str,
    password: str,
):
    """Set password for telegram user (for bot authentication)"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Set password
        user.hashed_password = get_password_hash(password)
        await session.commit()

        return {"status": "success", "message": "Password set successfully"}
