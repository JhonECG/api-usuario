import os
import uuid
import boto3
import json
from datetime import datetime
from auth import create_access_token

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.getenv('USERS_TABLE', 't_usuarios'))

ADMIN_EMAILS = [
    "jhon.chilo@utec.edu.pe",
    "sergio.delgado.a@utec.edu.pe",
    "federico.iribar@utec.edu.pe"
]

def handler(event, context):
    body = json.loads(event['body'])
    tenant_id = body['tenant_id']
    email = body['email']

    existing = table.scan(
        FilterExpression="tenant_id = :tenant_id AND email = :email",
        ExpressionAttributeValues={":tenant_id": tenant_id, ":email": email}
    )

    if existing.get("Items"):
        return {"statusCode": 400, "body": json.dumps({"message": "El usuario ya existe"})}

    rol = "admin" if email in ADMIN_EMAILS else "usuario"

    usuario_data = {
        "tenant_id": tenant_id,
        "usuario_id": str(uuid.uuid4()),
        "nombres": body['nombres'],
        "apellidos": body['apellidos'],
        "email": email,
        "telefono": body['telefono'],
        "direccion": body['direccion'],
        "fecha_registro": datetime.utcnow().isoformat(),
        "rol": rol,
        "password": body['password']
    }

    table.put_item(Item=usuario_data)

    return {
        "statusCode": 201,
        "body": json.dumps({"message": "Usuario creado correctamente", "usuario": usuario_data})
    }
