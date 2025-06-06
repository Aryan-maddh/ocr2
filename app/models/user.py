# app/models/user.py
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class SubscriptionPlan(str, enum.Enum):
    FREEMIUM = "freemium"
    BUSINESS = "business"
    INDUSTRY = "industry"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    subscription = Column(Enum(SubscriptionPlan), default=SubscriptionPlan.FREEMIUM)
    documents_processed_today = Column(Integer, default=0)
