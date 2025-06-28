import json
import boto3

dynamodb = boto3.resource('dynamodb')
table_name = os.getenv('TABLE_NAME')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        empresa = body['empresa']
        user_id = body['id']

        response = table.delete_item(
            Key={'empresa': empresa, 'id': user_id},
            ConditionExpression='attribute_exists(id)'  # Para evitar eliminar un registro inexistente
        )

        return {'statusCode': 200, 'body': json.dumps({'message': 'Usuario eliminado correctamente'})}

    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return {'statusCode': 404, 'body': json.dumps({'message': 'Usuario no encontrado'})}

    except Exception as e:
        return {'statusCode': 400, 'body': json.dumps({'error': str(e)})}
