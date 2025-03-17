from flask_pymongo import PyMongo

mongo = PyMongo()

class User:
    @staticmethod
    def find_by_username(username):
        return mongo.db.users.find_one({"username": username})

    @staticmethod
    def create_user(data):
        return mongo.db.users.insert_one(data)
