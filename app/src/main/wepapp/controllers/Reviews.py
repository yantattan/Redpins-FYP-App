from DbContext import MongoDBContext
from Model import SignedPlace
from bson.objectid import ObjectId


class ReviewCon:
    __connection = None

    def __init__(self):
        self.__connection = MongoDBContext.Connect()["Review"]

    def SendReviews(self, userId, address, review):
        self.__connection.update_one({"UserId": userId, "Address": address}, {})

    def GetReviews(self, address):
        pass