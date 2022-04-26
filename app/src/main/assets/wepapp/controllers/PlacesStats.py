from DbContext import MongoDBContext
from Model import SignedPlace
from bson.objectid import ObjectId

class PlacesStatsCon:
    __connection = None

    def __init__(self):
        self.__connection = MongoDBContext.Connect()["PlacesStats"]
