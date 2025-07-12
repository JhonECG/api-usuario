import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table_name = os.getenv('TABLE_NAME')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        tenant_id = body['tenant_id']

        # Query para obtener todos los usuarios del tenant
        response = table.query(
            KeyConditionExpression='tenant_id = :tenant_id_val',
            ExpressionAttributeValues={':tenant_id_val': tenant_id}
        )

        usuarios = response.get('Items', [])

        # Remover contraseñas del resultado por seguridad
        for usuario in usuarios:
            usuario.pop('password', None)

        return {
            'statusCode': 200,
            'body': json.dumps({'usuarios': usuarios})
        }

    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }
