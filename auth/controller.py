from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from core.database import get_db  # Usamos get_db para obtener la sesión de base de datos
from users.models import User
from users.schemas import UserCreate, UserOut, UserLogin
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Función para hashear contraseñas
def hash_password(password: str):
    return pwd_context.hash(password)

# Función para verificar contraseñas
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_jwt_token(user_id: int):
    expiration = datetime.utcnow() + timedelta(hours=1)
    token = jwt.encode({"sub": user_id, "exp": expiration}, "your_secret_key", algorithm="HS256")  # Asegúrate de poner tu clave secreta en lugar de "your_secret_key"
    return token

ADMIN_EMAILS = ["jhon.chilo@utec.edu.pe", "sergio.delgado.a@utec.edu.pe"]

@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Iniciar una transacción explícita
        with db.begin():  # db.begin() abre una transacción
            # Verificar si el email ya está registrado
            db_user = db.query(User).filter(User.email == user.email).first()
            if db_user:
                raise HTTPException(status_code=400, detail="Email already registered")

            # Hashear la contraseña
            hashed_password = hash_password(user.password)

            # Asignamos rol automático basado en el correo
            role = "admin" if user.email in ADMIN_EMAILS else "user"

            # Crear el nuevo usuario
            new_user = User(username=user.username, email=user.email, password=hashed_password, role=role)
            db.add(new_user)

        # Si todo está bien, se hace commit automáticamente

        return new_user
    except SQLAlchemyError as e:
        db.rollback()  # Asegurarse de que se haga rollback si hay un error
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except Exception as e:
        db.rollback()  # Asegurarse de que se haga rollback si hay un error no relacionado con la base de datos
        raise HTTPException(status_code=500, detail="Error: " + str(e))


@router.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    # Buscar al usuario por email
    db_user = db.query(User).filter(User.email == user.email).first()
    
    # Verificar si el usuario existe y si la contraseña es correcta
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Crear el token JWT
    token = create_jwt_token(db_user.id)
    
    # Devolver el token JWT
    return {"access_token": token, "token_type": "bearer"}
