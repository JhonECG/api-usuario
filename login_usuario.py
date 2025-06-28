import json
import boto3
import os
import jwt
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
table_name = os.getenv('TABLE_NAME')
table = dynamodb.Table(table_name)

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
        email = body['email']
        password = body['password']

        # Query por empresa usando GSI de email
        response = table.query(
            IndexName='gsi_email',
            KeyConditionExpression='empresa = :empresa_val AND email = :email_val',
            ExpressionAttributeValues={
                ':empresa_val': empresa,
                ':email_val': email
            }
        )

        items = response.get('Items', [])

        if not items or items[0]['password'] != password:
            return {
                'statusCode': 401,
                'body': json.dumps({'message': 'Credenciales inválidas'})
            }

        user = items[0]
        user_id = user['id']

        token = create_access_token(user_id, empresa)

        return {
            'statusCode': 200,
            'body': json.dumps({'token': token})
        }

    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }
