import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('t_usuarios')

def list_users(event, context):
    response = table.scan()
    items = response.get('Items', [])

    return {'statusCode': 200, 'body': json.dumps(items)}
