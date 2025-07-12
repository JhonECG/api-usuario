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

        update_fields = ['nombres', 'apellidos', 'telefono', 'direccion', 'password']
        update_expression = []
        expression_values = {}

        for field in update_fields:
            if field in body:
                update_expression.append(f"{field} = :{field}")
                expression_values[f":{field}"] = body[field] if field != 'direccion' else json.dumps(body[field])

        if not update_expression:
            return {'statusCode': 400, 'body': json.dumps({'message': 'No hay campos para actualizar'})}

        response = table.update_item(
            Key={'tenant_id': tenant_id, 'id': user_id},
            UpdateExpression="SET " + ", ".join(update_expression),
            ExpressionAttributeValues=expression_values,
            ReturnValues="ALL_NEW"
        )

        updated_user = response.get('Attributes', {})
        if not updated_user:
            return {'statusCode': 404, 'body': json.dumps({'message': 'No se encontró el usuario para modificar'})}
        updated_user.pop('password', None)

        return {'statusCode': 200, 'body': json.dumps({'message': 'Usuario modificado exitosamente', 'user': updated_user})}

    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'message': 'Error al modificar usuario', 'error': str(e)})}
