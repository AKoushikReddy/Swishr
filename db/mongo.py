from pymongo import MongoClient
from config.settings import Settings



client = MongoClient(Settings().MONGO_DB_URL)
db = client[Settings().MONGO_DB_NAME]

def get_collection(name):
    return MongoClient(Settings().MONGO_DB_URL, tz_aware=True)[Settings().MONGO_DB_NAME][name]
