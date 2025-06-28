import json
import boto3
import os
import jwt
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('t_usuarios')

SECRET_KEY = os.getenv('JWT_SECRET', 'clave_secreta')

def create_access_token(user_id, expires_delta=3600):
    payload = {
        'id': user_id,
        'exp': datetime.utcnow() + timedelta(seconds=expires_delta)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        email = body['email']
        password = body['password']

        response = table.scan(
            FilterExpression='email = :email_val',
            ExpressionAttributeValues={':email_val': email}
        )

        items = response.get('Items', [])

        if not items or items[0]['password'] != password:
            return {
                'statusCode': 401,
                'body': json.dumps({'message': 'Credenciales inválidas'})
            }

        user = items[0]
        user_id = user['id']

        token = create_access_token(user_id)

        return {
            'statusCode': 200,
            'body': json.dumps({'token': token})
        }

    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }
