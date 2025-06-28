import json
import uuid
import boto3
import os
import jwt
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('t_usuarios')

SECRET_KEY = os.getenv('JWT_SECRET', 'clave_secreta')

def create_access_token(user_id, empresa, expires_delta=3600):
    payload = {
        'id': user_id,
        'empresa': empresa,
        'exp': datetime.utcnow() + timedelta(seconds=expires_delta)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])

        empresa = body['empresa']
        user_id = str(uuid.uuid4())
        fecha_registro = datetime.utcnow().isoformat()

        item = {
            'empresa': empresa,  # Partition Key
            'id': user_id,       # Sort Key
            'nombres': body['nombres'],
            'apellidos': body['apellidos'],
            'email': body['email'],
            'telefono': body['telefono'],
            'direccion': json.dumps(body['direccion']),
            'password': body['password'],  # Hashear en producción
            'fecha_registro': fecha_registro,
            'rol': 'user'
        }

        table.put_item(Item=item)

        token = create_access_token(user_id, empresa)

        return {
            'statusCode': 201,
            'body': json.dumps({'token': token})
        }

    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }
