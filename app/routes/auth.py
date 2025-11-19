# app/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_async_session
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.crud.user import authenticate_user, get_user_by_email, create_user
from app.crud.student import create_student, get_student_by_user_id
from app.utils.security import create_access_token
from app.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    credentials: LoginRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Authenticate user and return JWT token.
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns access token and user/student IDs.
    """
    user = await authenticate_user(session, credentials.email, credentials.password)
    
    if not user:
        logger.warning(f"Failed login attempt for email: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Get student profile
    student = await get_student_by_user_id(session, user.id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    logger.info(f"Successful login for user: {user.email}")
    
    return TokenResponse(
        access_token=access_token,
        token_type="Bearer",
        user_id=user.id,
        student_id=student.id,
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    reg_data: RegisterRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Register a new student account.
    
    Creates both user account and student profile.
    Returns JWT token for immediate login.
    """
    # Check if user already exists
    existing_user = await get_user_by_email(session, reg_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user account
    user = await create_user(
        session=session,
        email=reg_data.email,
        password=reg_data.password,
        is_superuser=False,
    )
    
    # Create student profile
    student = await create_student(session, {
        "user_id": user.id,
        "name": reg_data.name,
        "class_name": reg_data.class_name,
        "medium": reg_data.medium,
        "subjects": reg_data.subjects,
        "board": reg_data.board,
    })
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    logger.info(f"New user registered: {user.email}")
    
    return TokenResponse(
        access_token=access_token,
        token_type="Bearer",
        user_id=user.id,
        student_id=student.id,
    )
