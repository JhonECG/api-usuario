import os
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any

SECRET_KEY = os.getenv("JWT_SECRET", "clave_secreta")
ALGORITHM = "HS256"

def lambda_handler(data: Dict[str, Any], expires_delta: int = 3600) -> str:
    try:
        # Validación de entrada
        if not isinstance(data, dict):
            raise ValueError("El parámetro 'data' debe ser un diccionario.")
        
        if not isinstance(expires_delta, int) or expires_delta <= 0:
            raise ValueError("El parámetro 'expires_delta' debe ser un entero positivo.")

        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        to_encode.update({"exp": expire})

        token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return token
    
    except Exception as e:
        # Aquí podrías loguear el error o personalizar el mensaje
        return f"Error al generar el token: {str(e)}"
