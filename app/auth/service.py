from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"

# Subscription limits
SUBSCRIPTION_LIMITS = {
    SubscriptionTier.FREE: {"daily_docs": 5, "storage_mb": 100},
    SubscriptionTier.BASIC: {"daily_docs": 50, "storage_mb": 1000},
    SubscriptionTier.PREMIUM: {"daily_docs": 200, "storage_mb": 5000},
    SubscriptionTier.ENTERPRISE: {"daily_docs": -1, "storage_mb": -1}  # Unlimited
}

class AuthService:
    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password):
        return pwd_context.hash(password)
    
    def check_document_limit(self, user: User) -> bool:
        """Check if user can process more documents today"""
        limit = SUBSCRIPTION_LIMITS[user.subscription_tier]["daily_docs"]
        if limit == -1:  # Unlimited
            return True
        
        # Reset counter if it's a new day
        if user.last_reset_date.date() < datetime.now().date():
            user.documents_processed_today = 0
            user.last_reset_date = datetime.now()
        
        return user.documents_processed_today < limit