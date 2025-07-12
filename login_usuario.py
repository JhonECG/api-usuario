import json
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
        email = body['email']
        password = body['password']

        # Query por tenant usando GSI de email
        response = table.query(
            IndexName='gsi_email',
            KeyConditionExpression='tenant_id = :tenant_id_val AND email = :email_val',
            ExpressionAttributeValues={
                ':tenant_id_val': tenant_id,
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

        token = create_access_token(user_id, tenant_id)

        return {
            'statusCode': 200,
            'body': json.dumps({'token': token})
        }

    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }
