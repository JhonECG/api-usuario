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
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': 'Faltan tenant_id o id en la solicitud'})
            }

        response = table.delete_item(
            Key={'tenant_id': tenant_id, 'id': user_id},
            ConditionExpression='attribute_exists(id)'
        )

        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': f'Usuario {user_id} eliminado correctamente'})
        }

    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return {
            'statusCode': 404,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'No se encontró el usuario para eliminar'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'Error al eliminar usuario', 'error': str(e)})
        }