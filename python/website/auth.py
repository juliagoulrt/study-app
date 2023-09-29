from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from datetime import datetime
import bcrypt


auth = Blueprint('auth', __name__)

client = MongoClient("mongodb://localhost:27017/")
COBALTO_DATABASE = 'cobalto'
USERS_COLLECTION = 'users'

#função pra retornar coleções do banco
def mongo_connection(database, collection):
    db = client[database]
    clct = db[collection]
    return clct

@auth.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        collection = mongo_connection(COBALTO_DATABASE, USERS_COLLECTION)
        data = request.get_json()
        username = data['username']
        password = data['password']
        password = password.encode('utf-8')
        user = collection.find_one({'username': username})
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404 
        if bcrypt.checkpw(password, user['password']):
            return jsonify({'Sucesso!': 'Bem-vindo ao sistema!'}), 200
        else:
            return jsonify({'Erro!': 'Senha incorreta!'}), 400

@auth.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        collection = mongo_connection(COBALTO_DATABASE, USERS_COLLECTION)
        data = request.get_json()
        username = data['username']
        password = data['password']
        user = collection.find_one({'username': username})
        if user:
            return jsonify({'error': 'Usuário já existe'}), 400         
        password = password.encode('utf-8')
        encriptedPass = bcrypt.hashpw(password, bcrypt.gensalt())
        name = data['name']
        created_at = datetime.utcnow()
        insert_data = {
            'username': username,
            'password': encriptedPass,
            'name': name,
            'createdAt': created_at
        }
        collection.insert_one(insert_data)
        
        return jsonify({"sucess": "Usuário criado com sucesso!"}), 201
