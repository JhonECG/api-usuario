import json
import boto3
from auth import create_access_token

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('t_usuarios')

def login(event, context):
    body = json.loads(event['body'])
    email = body['email']
    password = body['password']

    response = table.scan(
        FilterExpression='email = :email_val',
        ExpressionAttributeValues={':email_val': email}
    )
    
    items = response.get('Items', [])

    if not items or items[0]['password'] != password:
        return {'statusCode': 401, 'body': json.dumps({'message': 'Credenciales inválidas'})}

    user = items[0]
    token = create_access_token({'id': user['id'], 'email': user['email'], 'rol': user['rol']})

    return {'statusCode': 200, 'body': json.dumps({'token': token})}
