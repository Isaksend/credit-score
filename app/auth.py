"""
Модуль авторизации для Credit Scoring API
Использует JWT токены для защиты эндпоинтов
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# Конфигурация
SECRET_KEY = "your-secret-key-change-in-production-123456789"  # В продакшене использовать переменную окружения
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Настройка хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer схема для токенов
security = HTTPBearer()

# Простая база пользователей (в продакшене использовать БД)
USERS_DB = {
    "admin": {
        "username": "admin",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        "role": "admin"
    },
    "user": {
        "username": "user",
        "hashed_password": "$2b$12$KIXwGzFrKxLnCj8JYvZvLOXZpN5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Zu",  # "password"
        "role": "user"
    }
}


class Token(BaseModel):
    """Модель токена"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Данные из токена"""
    username: Optional[str] = None
    role: Optional[str] = None


class User(BaseModel):
    """Модель пользователя"""
    username: str
    role: str


class LoginRequest(BaseModel):
    """Запрос на авторизацию"""
    username: str
    password: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Аутентификация пользователя"""
    user = USERS_DB.get(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создание JWT токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Получение текущего пользователя из токена"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        
        if username is None:
            raise credentials_exception
            
        token_data = TokenData(username=username, role=role)
    except JWTError:
        raise credentials_exception
    
    user = USERS_DB.get(token_data.username)
    if user is None:
        raise credentials_exception
    
    return User(username=user["username"], role=user["role"])


async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Проверка прав администратора"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав доступа"
        )
    return current_user
