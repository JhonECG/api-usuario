import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv
import os

load_dotenv()  # Esto carga las variables desde el .env en la raíz 

# Obtén la URL de la base de datos desde las variables de entorno
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

# Crea el motor de conexión
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Crea la sesión local para la interacción con la DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crea la base declarativa
Base = declarative_base()

# Crea la función para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()