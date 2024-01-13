# https://motor.readthedocs.io/en/stable/tutorial-asyncio.html
from motor.motor_asyncio import AsyncIOMotorClient


class MongoDB:
    def __init__(self):
        self.db_url = "mongodb://localhost:27017"
        self.collection = ""

    def connect(self):
        client = AsyncIOMotorClient(self.db_url)
        return client

    def get_collection(self):
        client = self.connect()
        db = getattr(client, self.collection)
        return db

    async def insert_one(self, data):
        collection = self.get_collection()
        result = await collection.insert_one(data)
        return result

    async def insert_many(self, data):
        collection = self.get_collection()
        result = await collection.insert_many(data)
        return result

    async def find_one(self, query):
        collection = self.get_collection()
        result = await collection.find_one(query)
        return result

    async def find_many(self, query):
        collection = self.get_collection()
        result = await collection.find(query)
        return result

    async def update_one(self, query, data):
        collection = self.get_collection()
        result = await collection.update_one(query, data)
        return result

    async def update_many(self, query, data):
        collection = self.get_collection()
        result = await collection.update_many(query, data)
        return result

    async def delete_one(self, query):
        collection = self.get_collection()
        result = await collection.delete_one(query)
        return result

    async def delete_many(self, query):
        collection = self.get_collection()
        result = await collection.delete_many(query)
        return result

    async def drop_collection(self):
        collection = self.get_collection()
        result = await collection.drop()
        return result
