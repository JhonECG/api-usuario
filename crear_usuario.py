import json
import uuid
import boto3
import os
import jwt
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
table_name = os.getenv('TABLE_NAME')
table = dynamodb.Table(table_name)


SECRET_KEY = os.getenv('JWT_SECRET', 'clave_secreta')

def create_access_token(user_id, tenant_id, expires_delta=3600):
    payload = {
        'id': user_id,
        'tenant_id': tenant_id,
        'exp': datetime.utcnow() + timedelta(seconds=expires_delta)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])

        tenant_id = body['tenant_id']
        user_id = str(uuid.uuid4())
        fecha_registro = datetime.utcnow().isoformat()

        item = {
            'tenant_id': tenant_id,  # Partition Key
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

        token = create_access_token(user_id, tenant_id)

        return {
            'statusCode': 201,
            'body': json.dumps({'token': token})
        }

    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }
