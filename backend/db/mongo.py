from pymongo import MongoClient

# db init
client = MongoClient("mongodb://localhost:27017/")
db = client["pokedex"]
