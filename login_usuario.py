import json
import boto3
import os
from auth import generate_token

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    tenant_id = event['pathParameters']['tenant_id']
    body = json.loads(event['body'])
    email = body.get('email')
    password = body.get('password')

    response = table.scan(
        FilterExpression='tenant_id = :tenant_id AND email = :email',
        ExpressionAttributeValues={':tenant_id': tenant_id, ':email': email}
    )

    if not response['Items']:
        return {'statusCode': 404, 'body': json.dumps({'message': 'Usuario no encontrado'})}

    user = response['Items'][0]
    if user['password'] != password:
        return {'statusCode': 401, 'body': json.dumps({'message': 'Contraseña incorrecta'})}

    token = generate_token(user)

    return {
        'statusCode': 200,
        'body': json.dumps({'token': token})
    }
