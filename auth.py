import os
import jwt
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("JWT_SECRET", "clave_secreta")

def create_access_token(data: dict, expires_delta: int = 3600):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

def verify_token(event):
    try:
        auth_header = event['headers'].get('Authorization')
        if not auth_header:
            return {"statusCode": 401, "body": "Token no proporcionado"}

        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload

    except jwt.ExpiredSignatureError:
        return {"statusCode": 401, "body": "Token expirado"}

    except jwt.PyJWTError:
        return {"statusCode": 401, "body": "Token inválido"}

def require_admin(event):
    payload = verify_token(event)
    if isinstance(payload, dict) and payload.get("statusCode"):
        # Error en la verificación del token
        return payload

    if payload.get("rol") != "admin":
        return {"statusCode": 403, "body": "Acceso restringido a administradores"}

    return payload
