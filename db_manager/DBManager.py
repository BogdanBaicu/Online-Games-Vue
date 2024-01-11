import pymongo
import certifi
import gridfs

uri = "mongodb+srv://bogdanbaicu:g5WXaqiWXgvcsUVL@cluster0.mhd9p7f.mongodb.net/?retryWrites=true&w=majority"
# Create a new client and connect to the server
client = pymongo.MongoClient(uri, tlsCAFile=certifi.where())

database = client["web_dev"]
fs = gridfs.GridFS(database)

userCollection = database["users"]
userList = [
        {"username": "spiderman99", "firstName": "Spider", "lastName": "Man", "email": "spiderman@email.com", "password": "panda1234", "confirmPassword": "panda1234"},
        {"username": "princessLeia", "firstName": "Princess", "lastName": "Leia", "email": "princessleia@email.com", "password": "panda1234", "confirmPassword": "panda1234"},
        {"username": "geraltofRivia", "firstName": "Geralt", "lastName": "OfRivia", "email": "geraltofrivia@email.com", "password": "panda1234", "confirmPassword": "panda1234"},
        {"username": "ezio_auditore", "firstName": "Ezio", "lastName": "Auditore", "email": "ezioauditore@email.com", "password": "panda1234", "confirmPassword": "panda1234"},
        {"username": "nathan_drake99", "firstName": "Natha", "lastName": "Drake", "email": "nathandrake@email.com", "password": "panda1234", "confirmPassword": "panda1234"}
    ] 

userIds = userCollection.insert_many(userList)
print(userIds.inserted_ids)

gamesCollection = database["games"]
gameList = [
    {"title": "Balloon Madness", "description": "Try beat your friends' high scores by shooting as many balloons as possible before he time runs up", "image": "balloons.jpg"},
    {"title": "Endless Runner", "description": "How long can you survive in this amazing endless runner? Can you beat the highest scores of other players? Try it now!", "image": "runner.jpg"},
]

try:
    file1 = open("balloons.jpg", "rb")
    content1 = file1.read()
    out1 = fs.put(content1, filename="balloons.jpg")
    gameList[0]["image"] = out1 

    try:
        file2 = open("runner.jpg", "rb")
        content2 = file2.read()
        out2 = fs.put(content2, filename="runner.jpg")
        gameList[1]["image"] = out2

        gameIds = gamesCollection.insert_many(gameList)
        print(gameIds.inserted_ids)

        highScoresCollection = database["scores"]
        highScoresList = [
            {"game": gameIds.inserted_ids[0], "user": userIds.inserted_ids[0], "score": 67},
            {"game": gameIds.inserted_ids[1], "user": userIds.inserted_ids[0], "score": 55},
            {"game": gameIds.inserted_ids[1], "user": userIds.inserted_ids[1], "score": 109},
            {"game": gameIds.inserted_ids[0], "user": userIds.inserted_ids[2], "score": 73},
            {"game": gameIds.inserted_ids[0], "user": userIds.inserted_ids[3], "score": 45},
            {"game": gameIds.inserted_ids[1], "user": userIds.inserted_ids[4], "score": 77},
        ]
        highScoresIds = highScoresCollection.insert_many(highScoresList)
        print(highScoresIds)
    except:
        print("Error uploading the image!")
except:
    print("Error uploading the image!")



# try:
#     file = open("balloons.jpg", "rb")
#     content = file.read()
#     out = fs.put(content, filename="balloons.jpg")
#     print(out)

#     try:
#         out2 = fs.get(out)
#         file2 = open("balloon2.jpg", "wb")
#         byteArray = out2.read()
#         file2.write(byteArray)
#     except:
#         print("Error downloading the image!")
# except:
#     print("Error uploading the image!")