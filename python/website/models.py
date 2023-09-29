from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

#blueprint ajuda a organizar uma aplicação em partes menores, tornando o código mais limpo e legível

models = Blueprint('models', __name__) #nome do blueprint em que estamos trabalhando
# topics = Blueprint('topics', __name__)
#Cria um cliente MongoDB e especifica os nomes do banco de dados 
#e das coleções para a aplicação cobalto, onde serão inseridos 'flashcards' e 'topics'.
client = MongoClient("mongodb://localhost:27017/")
COBALTO_DATABASE = 'cobalto'
FLASHCARDS_COLLECTION = 'flashcards'
TOPICS_COLLECTION = 'topics'

#função pra retornar coleções do banco
def mongo_connection(database, collection):
    db = client[database]
    clct = db[collection]
    return clct

#métodos CRUD (criar, receber, atualizar e deletar) dos flashcards e tópicos
@models.route('/flashcards', methods=['GET', 'POST'])
def flashcards():
    #lógica pra receber
    if request.method == 'GET': 
        collection = mongo_connection(COBALTO_DATABASE, FLASHCARDS_COLLECTION)
        flashcards = list(collection.find())
        for flashcard in flashcards:
            flashcard['_id'] = str(flashcard['_id'])

    #retorna em json
        return jsonify(flashcards), 200
    #lógica pra criar
    if request.method == 'POST':
        collection = mongo_connection(COBALTO_DATABASE, FLASHCARDS_COLLECTION)
        data = request.get_json()
        question = data['question']
        answer = data['answer']
        correct = data['correct']
        created_at = datetime.utcnow()
        insert_data = {
            'question': question,
            'answer': answer,
            'correct': correct,
            'createdAt': created_at
        }
        collection.insert_one(insert_data)
        return jsonify(data), 201
    
@models.route('/flashcards/<flashcard_id>', methods=['PUT', 'DELETE', 'GET'])
def flashcard(flashcard_id):
    if request.method == 'GET': 
        collection = mongo_connection(COBALTO_DATABASE, FLASHCARDS_COLLECTION)
        flashcard = collection.find_one({'_id': ObjectId(flashcard_id)})
        flashcard['_id'] = str(flashcard['_id'])
        if flashcard:
            return jsonify({'message': 'Flashcard encontrado com sucesso!', 'flashcard': flashcard})
        else:
            return jsonify({'error': 'Flashcard não encontrado'}), 404
    if request.method == 'PUT':
        collection = mongo_connection(COBALTO_DATABASE, FLASHCARDS_COLLECTION)
        data = request.get_json()  
        
        update_data = {'$set': {}}
        if 'question' in data:
            update_data['$set']['question'] = data['question']
        if 'answer' in data:
            update_data['$set']['answer'] = data['answer']
        if 'correct' in data:
            update_data['$set']['correct'] = data['correct']
        update_data['$set']['updatedAt'] = datetime.utcnow()
        
        updated_flashcard = collection.find_one_and_update({'_id': ObjectId(flashcard_id)}, update_data, return_document=True)

        if updated_flashcard:
            updated_flashcard['_id'] = str(updated_flashcard['_id'])
            return jsonify({'message': 'Flashcard atualizado com sucesso!', 'flashcard': updated_flashcard})
        else:
            return jsonify({'error': 'Flashcard não encontrado'}), 404
    if request.method == 'DELETE': 
        collection = mongo_connection(COBALTO_DATABASE, FLASHCARDS_COLLECTION)
        flashcard = collection.find_one_and_delete({'_id': ObjectId(flashcard_id)})
        flashcard['_id'] = str(flashcard['_id'])
        if flashcard:
            return jsonify({'message': 'Flashcard excluído com sucesso!'})
        else:
            return jsonify({'error': 'Flashcard não encontrado'}), 404

@models.route('/topics', methods=['GET', 'POST'])
def topics():
    #lógica pra receber
    if request.method == 'GET': 
        collection = mongo_connection(COBALTO_DATABASE, TOPICS_COLLECTION)
        topics = list(collection.find())
        for topic in topics:
            topic['_id'] = str(topic['_id'])
            for flashcard in topic['flashcards']:
                flashcard['_id'] = str(flashcard['_id'])

    #retorna em json
        return jsonify(topics), 200
    #lógica pra criar
    if request.method == 'POST':
        collection = mongo_connection(COBALTO_DATABASE, TOPICS_COLLECTION)
        flashcardsCollection = mongo_connection(COBALTO_DATABASE, FLASHCARDS_COLLECTION)
        
        data = request.get_json()
        flashcardsArray = data['flashcards']
        arrayToInsert = []
        for f in flashcardsArray:
            arrayToInsert.append(ObjectId(f))
        flashcards = list(flashcardsCollection.find({ "_id" : { "$in" : arrayToInsert } }))
        title = data['title']
        description = data['description']
        created_at = datetime.utcnow()
        insert_data = {
            'flashcards': flashcards,
            'title': title,
            'description': description,
            'createdAt': created_at
        }
        collection.insert_one(insert_data)
        return jsonify(data), 201

@models.route('/topics/<topic_id>', methods=['PUT', 'DELETE', 'GET'])
def topic(topic_id):
    if request.method == 'GET': 
        collection = mongo_connection(COBALTO_DATABASE, TOPICS_COLLECTION)
        topic = collection.find_one({'_id': ObjectId(topic_id)})
        topic['_id'] = str(topic['_id'])
        for flashcard in topic['flashcards']:
            flashcard['_id'] = str(flashcard['_id'])
        if topic:
            return jsonify({'message': 'Tópico encontrado com sucesso!', 'topic': topic})
        else:
            return jsonify({'error': 'Tópico não encontrado'}), 404
    if request.method == 'PUT':
        collection = mongo_connection(COBALTO_DATABASE, TOPICS_COLLECTION)
        flashcardsCollection = mongo_connection(COBALTO_DATABASE, FLASHCARDS_COLLECTION)
        
        data = request.get_json()
        flashcardsArray = data['flashcards']
        arrayToInsert = []
        for f in flashcardsArray:
            arrayToInsert.append(ObjectId(f))
        flashcards = list(flashcardsCollection.find({ "_id" : { "$in" : arrayToInsert } }))
        
        update_data = {'$set': {}}
        if 'title' in data:
            update_data['$set']['title'] = data['title']
        if 'description' in data:
            update_data['$set']['description'] = data['description']
        if 'flashcards' in data:
            update_data['$set']['flashcards'] = flashcards
        update_data['$set']['updatedAt'] = datetime.utcnow()
        
        uptdated_topic = collection.find_one_and_update({'_id': ObjectId(topic_id)}, update_data, return_document=True)

        if uptdated_topic:
            uptdated_topic['_id'] = str(uptdated_topic['_id'])
            for flashcard in uptdated_topic['flashcards']:
                flashcard['_id'] = str(flashcard['_id'])
            return jsonify({'message': 'Tópico atualizado com sucesso!', 'topic': uptdated_topic})
        else:
            return jsonify({'error': 'Tópico não encontrado'}), 404
    if request.method == 'DELETE': 
        collection = mongo_connection(COBALTO_DATABASE, TOPICS_COLLECTION)
        topic = collection.find_one_and_delete({'_id': ObjectId(topic_id)})
        topic['_id'] = str(topic['_id'])
        if topic:
            return jsonify({'message': 'Tópico excluído com sucesso!'})
        else:
            return jsonify({'error': 'Tópico não encontrado'}), 