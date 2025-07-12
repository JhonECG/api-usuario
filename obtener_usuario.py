import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table_name = os.getenv('TABLE_NAME')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        tenant_id = body.get('tenant_id')
        user_id = body.get('id')

        if not tenant_id or not user_id:
            return {'statusCode': 400, 'body': json.dumps({'message': 'Faltan tenant_id o id en la solicitud'})}

        response = table.get_item(
            Key={
                'tenant_id': tenant_id,
                'id': user_id
            }
        )

        user = response.get('Item')

        if not user:
            return {'statusCode': 404, 'body': json.dumps({'message': 'No se encontró el usuario solicitado'})}

        user.pop('password', None)

        return {'statusCode': 200, 'body': json.dumps({'message': 'Usuario encontrado', 'user': user})}

    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'message': 'Error al obtener usuario', 'error': str(e)})}
