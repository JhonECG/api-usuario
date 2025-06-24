import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('t_usuarios')

def get_user(event, context):
    user_id = event['pathParameters']['id']

    response = table.get_item(Key={'id': user_id})

    if 'Item' not in response:
        return {'statusCode': 404, 'body': json.dumps({'message': 'Usuario no encontrado'})}

    return {'statusCode': 200, 'body': json.dumps(response['Item'])}
