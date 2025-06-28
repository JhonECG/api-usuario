import json
import boto3

dynamodb = boto3.resource('dynamodb')
table_name = os.getenv('TABLE_NAME')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        empresa = body['empresa']

        # Query para obtener todos los usuarios de la empresa
        response = table.query(
            KeyConditionExpression='empresa = :empresa_val',
            ExpressionAttributeValues={':empresa_val': empresa}
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
