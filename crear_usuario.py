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

        required_fields = ['tenant_id', 'nombres', 'apellidos', 'email', 'telefono', 'direccion', 'password']
        for field in required_fields:
            if field not in body:
                return {
                    'statusCode': 400,
                    'headers': {'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'message': f'Falta el campo obligatorio: {field}'})
                }

        tenant_id = body['tenant_id']
        email = body['email']

        # Verificar si el usuario ya existe usando el índice EmpresaEmailIndex
        response = table.query(
            IndexName='EmpresaEmailIndex',
            KeyConditionExpression='tenant_id = :tenant_id_val AND email = :email_val',
            ExpressionAttributeValues={
                ':tenant_id_val': tenant_id,
                ':email_val': email
            }
        )
        if response.get('Items'):
            return {
                'statusCode': 409,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': 'El usuario ya existe con ese email en este tenant'})
            }

        user_id = str(uuid.uuid4())
        fecha_registro = datetime.utcnow().isoformat()

        item = {
            'tenant_id': tenant_id,
            'id': user_id,
            'nombres': body['nombres'],
            'apellidos': body['apellidos'],
            'email': body['email'],
            'telefono': body['telefono'],
            'direccion': json.dumps(body['direccion']),
            'password': body['password'],
            'fecha_registro': fecha_registro,
            'rol': 'user'
        }

        table.put_item(Item=item)

        token = create_access_token(user_id, tenant_id)

        return {
            'statusCode': 201,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'Usuario creado exitosamente', 'token': token, 'user_id': user_id})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'Error al crear usuario', 'error': str(e)})
        }