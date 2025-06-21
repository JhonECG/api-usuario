from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import models, schemas
import bcrypt  

# Lista de correos de administradores
ADMIN_EMAILS = ["jhon.chilo@utec.edu.pe", "sergio.delgado.a@utec.edu.pe"]

# Función para hashear la contraseña
def hash_password(password: str) -> str:
    # Generar un salt y luego hacer el hash
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def create_user(db: Session, user: schemas.UserCreate):

    role = "admin" if user.email in ADMIN_EMAILS else "user"  # Asigna admin si el correo está en la lista

    # Hashear la contraseña antes de guardarla
    hashed_password = hash_password(user.password)

    db_user = models.User(
        email=user.email,
        password=hashed_password,
        role=role
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ---------------- LEER USUARIO ----------------
def get_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).offset(skip).limit(limit).all()

# ---------------- ACTUALIZAR USUARIO ----------------
def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate, current_user_role: str):
    # Solo los administradores pueden cambiar el rol
    if user_update.role and current_user_role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to change user role")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.email:
        user.email = user_update.email
    if user_update.password:
        user.password = hash_password(user_update.password)  # Hashear la nueva contraseña
    if user_update.role:
        user.role = user_update.role

    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}
