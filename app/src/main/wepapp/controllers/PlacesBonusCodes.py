from DbContext import MongoDBContext
from datetime import datetime
import random


class PlacesBonusCodesCon:
    __connection = None

    def __init__(self):
        self.__connection = MongoDBContext.Connect()["PlacesBonusCodes"]

    def GenerateCode(self, id):
        randomCode = "".join([random.randrange(10) for num in range(0,4)]) 
        tries = 0
        while tries < 4:
            tries += 1
            try:
                self.__connection.insert_one({"PlaceId": id, "Code": randomCode, "Timestamp": datetime.now()})
            except Exception:
                print("Retrying generation of claim code")
    
    def CheckValidCode(self, address, code):
        return self.__connection.find({"Address": address, "Code": code}) is not None
