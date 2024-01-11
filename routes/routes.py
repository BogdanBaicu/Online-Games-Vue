from flask import Flask, jsonify, request
from flask_cors import cross_origin
from bson import ObjectId
import pymongo
import certifi
import gridfs

uri = "mongodb+srv://bogdanbaicu:g5WXaqiWXgvcsUVL@cluster0.mhd9p7f.mongodb.net/?retryWrites=true&w=majority"
# Create a new client and connect to the server
client = pymongo.MongoClient(uri, tlsCAFile=certifi.where())

database = client["web_dev"]
fs = gridfs.GridFS(database)

userCollection = database["users"]
gameCollection = database["games"]
scoreCollection = database["scores"]

app = Flask(__name__)


@app.route('/getScores', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_scores():
    result = []
    for score in scoreCollection.find():
        result.append({'_id': str(score['_id']), 'game': score['game'], 'user': score['user'], 'score': score['score']})
    
    return jsonify(result=result)


@app.route('/getScoresByGameName/<game>', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_scores_game_name(game):
    result = []
    query = {'game': game}
    document = scoreCollection.find(query)

    for score in document:
        result.append({'_id': str(score['_id']), 'game': score['game'], 'user': score['user'], 'score': score['score']})

    return jsonify(result=result)


@app.route('/getScoresByGameId/<id>', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_scores_game_id(id):
    result = []
    query = {'game': ObjectId(id)}
    document = scoreCollection.find(query)

    for score in document:
        user_id = score['user']
        user = userCollection.find_one({'_id': ObjectId(user_id)})
        
        if user:
            result.append({
                '_id': str(score['_id']),
                'game': str(score['game']),
                'user': str(score['user']),
                'username': user['username'],
                'score': score['score']
            })

    return jsonify(result=result)

@app.route('/getGameNameById/<id>', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_game_name_id(id):
    result = []
    query = {'_id': ObjectId(id)}
    document = gameCollection.find_one(query)

    return jsonify(result=document['title'])


@app.route('/getUserNameById/<id>', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_user_name_id(id):
    result = []
    query = {'_id': ObjectId(id)}
    document = userCollection.find_one(query)

    return jsonify(result=document['username'])


@app.route('/addScore', methods=['POST', 'PUT'])
@cross_origin(supports_credentials=True) 
def add_score():
    dict = request.form.to_dict()
    requeste_id = 0

    data = {
        'game': ObjectId(dict['game']),
        'user': ObjectId(dict['user']),
        'score': int(dict['score'])
    }
    if request.method == 'POST':
        requested_id = scoreCollection.insert_one(data).inserted_id

    if request.method == 'PUT':
        scoreCollection.update_one({'game': data['game'], 'user': data['user']}, {'$set': {'score': data['score']}})
        requested_id = dict['_id']

    return jsonify(id=str(requested_id))


@app.route('/getScoreById/<id>', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_score(id):
    result = []
    query = {'_id': ObjectId(id)}
    document = scoreCollection.find_one(query)
    
    return jsonify(result=document['score'])


@app.route('/getGames', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_games():
    result = []
    for score in gameCollection.find():
        result.append({'_id': str(score['_id']), 'title': score['title'], 'description': score['description'], 'image': str(score['image'])})
    
    return jsonify(result=result)


@app.route('/getImageById/<id>', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_image(id):
    out = fs.get(ObjectId(id))
    
    return out.read()


@app.route('/resetPassword', methods=['PUT'])
@cross_origin(supports_credentials=True)
def reset_password():
    dict = request.form.to_dict()
    data = {
        'username': dict['username'],
        'email': dict['email'],
        'password': dict['password'],
        'confirmPassword': dict['confirmPassword']
    }

    result = []
    document = userCollection.find_one_and_update({'username': data['username'], 'email': data['email']}, 
                                                  {'$set': {'password': data['password'], 'confirmPassword': data['confirmPassword']}}, 
                                                  return_document = pymongo.ReturnDocument.AFTER)

    return jsonify(result=str(document['_id']))


@app.route('/searchUserByUsername/<username>', methods=['GET'])
@cross_origin(supports_credentials=True)
def search_user_username(username):
    query = {'username': username}
    document = userCollection.count_documents(query)
    if (document):
        document2 = userCollection.find_one(query)
        return jsonify(result=(document, str(document2['_id'])))
    return jsonify(result=str(document))


@app.route('/searchUserByEmail/<email>', methods=['GET'])
@cross_origin(supports_credentials=True)
def search_user_email(email):
    query = {'email': email}
    document = userCollection.count_documents(query)
    if (document):
        document2 = userCollection.find_one(query)
        return jsonify(result=(document, str(document2['_id'])))
    return jsonify(result=str(document))


@app.route('/login', methods=['POST'])
@cross_origin(supports_credentials=True)
def login():
    dict = request.form.to_dict()
    data = {
        'username': dict['username'],
        'password': dict['password']
    }
    query = {'username': data['username'], 'password': data['password']}
    document = userCollection.count_documents(query)
    if (document):
        document2 = userCollection.find_one(query)
        return jsonify(result=(document, str(document2['_id'])))
    return jsonify(result=str(document))


@app.route('/register', methods=['POST'])
@cross_origin(supports_credentials=True)
def register():
    dict = request.form.to_dict()
    data = {
        'username': dict['username'],
        'email': dict['email'],
        'lastName': dict['lastName'],
        'firstName': dict['firstName'],
        'password': dict['password'],
        'confirmPassword': dict['confirmPassword']
    }

    requested_id = userCollection.insert_one(data).inserted_id

    return jsonify(id=str(requested_id))

if __name__ == "__main__":
    app.run()
