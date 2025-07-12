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

        if not tenant_id:
            return {'statusCode': 400, 'body': json.dumps({'message': 'Falta tenant_id en la solicitud'})}

        response = table.query(
            KeyConditionExpression='tenant_id = :tenant_id_val',
            ExpressionAttributeValues={':tenant_id_val': tenant_id}
        )

        usuarios = response.get('Items', [])

        # Remover contraseñas del resultado por seguridad
        for usuario in usuarios:
            usuario.pop('password', None)

        if not usuarios:
            return {'statusCode': 404, 'body': json.dumps({'message': 'No se encontraron usuarios para el tenant solicitado'})}

        return {
            'statusCode': 200,
            'body': json.dumps({'usuarios': usuarios, 'message': f'Se encontraron {len(usuarios)} usuarios'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error al listar usuarios', 'error': str(e)})
        }
