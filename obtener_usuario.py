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
        user_id = body['id']

        # Hacemos una consulta directa por la clave primaria compuesta (tenant_id, id)
        response = table.get_item(
            Key={
                'tenant_id': tenant_id,
                'id': user_id
            }
        )

        user = response.get('Item')

        if not user:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Usuario no encontrado'})
            }

        # No devolvemos la contraseña
        user.pop('password', None)

        return {
            'statusCode': 200,
            'body': json.dumps(user)
        }

    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }
