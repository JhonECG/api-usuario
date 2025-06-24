import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('t_usuarios')

def update_user(event, context):
    user_id = event['pathParameters']['id']
    body = json.loads(event['body'])

    update_expression = "SET " + ", ".join(f"{k} = :{k}" for k in body.keys())
    expression_values = {f":{k}": v for k, v in body.items()}

    table.update_item(
        Key={'id': user_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values
    )

    return {'statusCode': 200, 'body': json.dumps({'message': 'Usuario actualizado correctamente'})}
