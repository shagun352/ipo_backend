from sqlalchemy import Column, Integer, String,Float
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from database.base import Base

class IPO(Base):
    __tablename__ = "ipo"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String(50), nullable=True)
    pan_number = Column(String(15), nullable=True, unique=True)
    username = Column(String(50))
    applicant_name = Column(String(100), nullable=True)
    company_name = Column(String(100), nullable=True)
    shares_allotted = Column(Integer, nullable=True)
    adjusted_amount = Column(Float, nullable=True)
    refund_amount = Column(Float, nullable=True)
    updated_at = Column(String(50), nullable=True)