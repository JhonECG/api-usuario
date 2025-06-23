import json
import boto3
import os
import uuid
import bcrypt
import datetime
import jwt
from utils import response, get_user_by_email, authorize

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.getenv("USERS_TABLE"))

SECRET_KEY = os.getenv("SECRET_KEY")
JWT_ALGORITHM = "HS256"

def register(event, context):
    body = json.loads(event['body'])

    id = str(uuid.uuid4())
    nombres = body['nombres']
    apellidos = body['apellidos']
    email = body['email']
    telefono = body['telefono']
    direccion = body['direccion']
    password = body['password']
    rol = body.get('rol', 'user')
    fecha_registro = datetime.datetime.utcnow().isoformat()

    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    item = {
        'id': id,
        'nombres': nombres,
        'apellidos': apellidos,
        'email': email,
        'telefono': telefono,
        'direccion': direccion,
        'password': hashed_pw,
        'rol': rol,
        'fecha_registro': fecha_registro
    }

    table.put_item(Item=item)
    item.pop('password')
    return response(201, item)

def login(event, context):
    body = json.loads(event['body'])
    email = body['email']
    password = body['password']

    user = get_user_by_email(email, table)
    if not user or not bcrypt.checkpw(password.encode(), user['password'].encode()):
        return response(401, {"error": "Credenciales inválidas"})

    payload = {
        "sub": user['id'],
        "email": user['email'],
        "rol": user['rol'],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return response(200, {"token": token})

def list_users(event, context):
    claims = authorize(event, admin_only=True)
    if 'error' in claims:
        return response(403, claims)

    scan = table.scan()
    for item in scan['Items']:
        item.pop('password', None)
    return response(200, scan['Items'])

def get_user(event, context):
    user_id = event['pathParameters']['id']
    res = table.get_item(Key={'id': user_id})
    user = res.get('Item')
    if not user:
        return response(404, {"error": "Usuario no encontrado"})
    user.pop('password', None)
    return response(200, user)

def update_user(event, context):
    claims = authorize(event, admin_only=True)
    if 'error' in claims:
        return response(403, claims)

    user_id = event['pathParameters']['id']
    body = json.loads(event['body'])

    update_expr = "SET " + ", ".join([f"{k}=:{k}" for k in body.keys()])
    expr_attrs = {f":{k}": v for k, v in body.items()}

    table.update_item(
        Key={'id': user_id},
        UpdateExpression=update_expr,
        ExpressionAttributeValues=expr_attrs
    )

    return response(200, {"msg": "Usuario actualizado"})

def delete_user(event, context):
    claims = authorize(event, admin_only=True)
    if 'error' in claims:
        return response(403, claims)

    user_id = event['pathParameters']['id']
    table.delete_item(Key={'id': user_id})
    return response(200, {"msg": "Usuario eliminado"})
