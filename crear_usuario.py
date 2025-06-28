import json
import uuid
import boto3
import os
from datetime import datetime, timedelta
import jwt

# Inicializamos DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('t_usuarios')

# Configuración JWT
SECRET_KEY = os.getenv("JWT_SECRET", "clave_secreta")
ALGORITHM = "HS256"

# Función para crear el token JWT
def create_token(user_id: str, expires_delta: int = 3600) -> str:
    try:
        payload = {
            "sub": user_id,
            "exp": datetime.utcnow() + timedelta(seconds=expires_delta)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token
    except Exception as e:
        raise Exception(f"Error al generar el token: {str(e)}")

# Función Lambda principal
def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])

        # Generar ID único y fecha de registro
        user_id = str(uuid.uuid4())
        fecha_registro = datetime.utcnow().isoformat()

        # Crear item para DynamoDB
        item = {
            'id': user_id,
            'nombres': body['nombres'],
            'apellidos': body['apellidos'],
            'email': body['email'],
            'telefono': body['telefono'],
            'direccion': json.dumps(body['direccion']),
            'password': body['password'],  # En producción deberías hashearla
            'fecha_registro': fecha_registro
        }

        # Guardar en DynamoDB
        table.put_item(Item=item)

        # Crear token para el usuario
        token = create_token(user_id)

        # Respuesta exitosa
        return {
            'statusCode': 201,
            'body': json.dumps({
                'message': 'Usuario registrado correctamente',
                'id': user_id,
                'token': token
            })
        }

    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }
