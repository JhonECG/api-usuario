import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('t_usuarios')

def delete_user(event, context):
    user_id = event['pathParameters']['id']

    table.delete_item(Key={'id': user_id})

    return {'statusCode': 200, 'body': json.dumps({'message': 'Usuario eliminado correctamente'})}
