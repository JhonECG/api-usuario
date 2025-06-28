import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('t_usuarios')

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        empresa = body['empresa']
        user_id = body['id']

        # Campos que se pueden actualizar
        update_fields = ['nombres', 'apellidos', 'telefono', 'direccion', 'password']

        # Construir expresión de actualización dinámica
        update_expression = []
        expression_values = {}

        for field in update_fields:
            if field in body:
                update_expression.append(f"{field} = :{field}")
                expression_values[f":{field}"] = body[field] if field != 'direccion' else json.dumps(body[field])

        if not update_expression:
            return {'statusCode': 400, 'body': json.dumps({'message': 'No hay campos para actualizar'})}

        response = table.update_item(
            Key={'empresa': empresa, 'id': user_id},
            UpdateExpression="SET " + ", ".join(update_expression),
            ExpressionAttributeValues=expression_values,
            ReturnValues="ALL_NEW"
        )

        updated_user = response.get('Attributes', {})
        updated_user.pop('password', None)  # No devolvemos la contraseña

        return {'statusCode': 200, 'body': json.dumps({'message': 'Usuario actualizado', 'user': updated_user})}

    except Exception as e:
        return {'statusCode': 400, 'body': json.dumps({'error': str(e)})}
