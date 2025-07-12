# File: verificar_token_lambda.py
import json
import os
import jwt

SECRET_KEY = os.getenv("JWT_SECRET", "clave_secreta")

def lambda_handler(event, context):
    try:
        # Extraer el header Authorization
        auth_header = event['headers'].get('Authorization')
        if not auth_header:
            return {
                "statusCode": 401,
                "body": json.dumps({"message": "Token no proporcionado"})
            }

        # Extraer el token (Bearer <token>)
        token = auth_header.split(" ")[1]

        # Decodificar el token (esto verifica la firma y expiración)
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        # Si no hay excepción, el token es válido
        # Se espera que el payload contenga 'tenant_id' en vez de 'empresa'
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Token válido", "payload": payload})
        }

    except jwt.ExpiredSignatureError:
        return {
            "statusCode": 401,
            "body": json.dumps({"message": "Token expirado"})
        }

    except jwt.PyJWTError:
        return {
            "statusCode": 401,
            "body": json.dumps({"message": "Token inválido"})
        }
