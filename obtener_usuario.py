import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table_name = os.getenv('TABLE_NAME')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        empresa = body['empresa']
        user_id = body['id']

        # Hacemos una consulta directa por la clave primaria compuesta (empresa, id)
        response = table.get_item(
            Key={
                'empresa': empresa,
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
