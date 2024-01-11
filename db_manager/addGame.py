import pymongo
import certifi
import gridfs

uri = "mongodb+srv://bogdanbaicu:g5WXaqiWXgvcsUVL@cluster0.mhd9p7f.mongodb.net/?retryWrites=true&w=majority"
# Create a new client and connect to the server
client = pymongo.MongoClient(uri, tlsCAFile=certifi.where())

database = client["web_dev"]
fs = gridfs.GridFS(database)

gamesCollection =  database["games"]

gameList = [
    {"title": "Balloon Madness", "description": "Try beat your friends' high scores by shooting as many balloons as possible before he time runs up", "image": "balloons.jpg"},
    {"title": "Endless Runner", "description": "How long can you survive in this amazing endless runner? Can you beat the highest scores of other players? Try it now!", "image": "runner.jpg"},
    {"title": "Duck Hunt", "description": "Try beat your friends' high scores by shooting as many ducks as possible making your dog happy", "image": "duck_hunt.jpg"},
    {"title": "Pong", "description": "Try beat your friends' high scores winning against the computer as fast as possible", "image": "pong.jpg"}
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

        try:
            file3 = open("duck_hunt.jpg", "rb")
            content3 = file3.read()
            out3 = fs.put(content3, filename="duck_hunt.jpg")
            gameList[2]["image"] = out3 

            try:
                file4 = open("pong.jpg", "rb")
                content4 = file4.read()
                out4 = fs.put(content4, filename="pong.jpg")
                gameList[3]["image"] = out4

            except:
                print("Error uploading the image")
        except:
            print("Error uploading the image")

        gameIds = gamesCollection.insert_many(gameList)
        print(gameIds.inserted_ids)

    except:
        print("Error uploading the image!")
except:
    print("Error uploading the image!")