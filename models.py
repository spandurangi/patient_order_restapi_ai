from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    date_of_birth = Column(String, index=True)

class UserActivityLog(Base):
    __tablename__ = "user_activity"
    id = Column(Integer, primary_key=True, index=True)
    path = Column(String)
    method = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_ip = Column(String)