from sqlalchemy.orm import Session
from fastapi import HTTPException
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from core.config import Config
from users.schemas import UserCreate, UserOut
from users.models import Address

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Correos que automáticamente tendrán rol admin
ADMIN_EMAILS = ["jhon.chilo@utec.edu.pe", "sergio.delgado.a@utec.edu.pe"]

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_jwt_token(user_id: int):
    expiration = datetime.utcnow() + timedelta(hours=1)
    token = jwt.encode({"sub": user_id, "exp": expiration}, Config.SECRET_KEY, algorithm="HS256")
    return token

def register_user(db: Session, user: schemas.UserCreate):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)
    role = "admin" if user.email in ADMIN_EMAILS else "user"

    new_user = models.User(
        email=user.email,
        password=hashed_password,
        role=role
    )

    if user.address:
        address = Address(
            country=user.address.country,
            city=user.address.city,
            street=user.address.street,
            postal_code=user.address.postal_code
        )
        new_user.address = address

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def login_user(db: Session, user: schemas.UserLogin):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_jwt_token(db_user.id)
    return {"access_token": token, "token_type": "bearer"}
