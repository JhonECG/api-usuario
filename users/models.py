from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)  # Longitud definida
    email = Column(String(120), unique=True, index=True, nullable=False)  # Longitud ya definida
    password = Column(String(128), nullable=False)  # Longitud ya definida
    role = Column(String(50), nullable=False)  # Longitud definida

    address = relationship("Address", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    country = Column(String(100), nullable=False)  # Longitud definida
    city = Column(String(100), nullable=False)  # Longitud definida
    street = Column(String(100), nullable=False)  # Longitud definida
    postal_code = Column(String(20), nullable=True)  # Longitud ya definida

    user = relationship("User", back_populates="address")