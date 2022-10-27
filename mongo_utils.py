import random
import uuid

from pymongo import MongoClient


class MongoDBConnection:

    def __init__(self, username, password, hostname, port=27017):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.client = None

    def __enter__(self):
        CONNECTION_STRING = f"mongodb://{self.username}:{self.password}@{self.hostname}:{self.port}"
        self.client = MongoClient(CONNECTION_STRING)
        self.db = self.client['test']
        return self.db

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.client.close()


if __name__ == '__main__':
    with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
        collection = db['Stopping point']
        collection.insert_one({'points': [{'name': f"{uuid.uuid4()}",
                                           'lat': random.randint(0, 500), 'lon': random.randint(0, 500)},
                                          {'name': f"{uuid.uuid4()}",
                                           'lat': random.randint(0, 500), 'lon': random.randint(0, 500)}
                                          ]})

        # collection = db['event_users']
        # collection.insert_one({"pending": [2, 3, 1], "accepted": [4, 5]})
