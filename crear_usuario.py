import json
import uuid
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('t_usuarios')

def register(event, context):
    body = json.loads(event['body'])
    
    user_id = str(uuid.uuid4())
    fecha_registro = datetime.utcnow().isoformat()

    item = {
        'id': user_id,
        'nombres': body['nombres'],
        'apellidos': body['apellidos'],
        'email': body['email'],
        'telefono': body['telefono'],
        'direccion': json.dumps(body['direccion']),
        'password': body['password'],  # En producción debería ser hasheada
        'fecha_registro': fecha_registro,
        'rol': 'admin' if body['email'] in os.getenv('ADMIN_EMAILS', '').split(',') else 'user'
    }

    table.put_item(Item=item)

    return {
        'statusCode': 201,
        'body': json.dumps({'message': 'Usuario registrado correctamente', 'id': user_id})
    }
