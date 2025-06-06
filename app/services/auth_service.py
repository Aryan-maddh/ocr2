# app/services/auth_service.py
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.models.user import SubscriptionPlan, User

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def check_document_limit(self, user: User) -> bool:
        if user.subscription == SubscriptionPlan.FREEMIUM and user.documents_processed_today >= 5:
            return False
        elif user.subscription == SubscriptionPlan.BUSINESS and user.documents_processed_today >= 50:
            return False
        elif user.subscription == SubscriptionPlan.INDUSTRY:
            return True
        return True
