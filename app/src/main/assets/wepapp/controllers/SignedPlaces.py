from DbContext import MySql
from DbContext import MongoDBContext
from Model import SignedPlace
from bson.objectid import ObjectId
import random


class SignedPlacesCon:
    __connection = None

    def __init__(self):
        self.__connection = MongoDBContext.Connect()["PartneredPlaces"]

    def GetShopInfo(self, address):
        # cursor = self.__connection.cursor()

        # cursor.execute('SELECT * FROM SignedPlaces WHERE Id = "{}";'
        #                 .format(id))
        # shop = cursor.fetchone()
        # if shop is not None:
        #     return SignedPlace(shop[0], shop[1], shop[2], shop[3], shop[4], shop[5], shop[6], shop[7])

        shop = self.__connection.find_one({"Address": address})
        if shop is not None:
            return SignedPlace(shop["_id"], shop["Address"], shop["UnitNo"], shop["Name"], shop["Organization"], 
                                    shop["Category"], shop["Details"], shop["Points"], shop["Checkpoint"], shop["Discount"])

    def ViewListOfPlaces(self, search, sort, order, offset, limit):
        # cursor = self.__connection.cursor()

        # whereCondition = 'Id LIKE "%{}%" OR Address LIKE "%{}%" OR UnitNo LIKE "%{}%" OR ShopName LIKE "%{}%" OR '\
        #                 'Organization LIKE "%{}%" OR Points LIKE "%{}%"'\
        #                 .format(search, search, search, search, search, search)
        
        # sortAndOrder = ''
        # if sort:
        #     sortAndOrder += 'ORDER BY {}'.format(sort)
        #     if order is not None and order == "desc":
        #         sortAndOrder += ', DESC'

        # cursor.execute('SELECT * FROM SignedPlaces '
        #                 'WHERE {} {} '
        #                 'LIMIT {} OFFSET {};'
        #                 .format(whereCondition, sortAndOrder, limit, int(offset)*int(limit) ))
        # results = cursor.fetchall()
        # resultDict = [SignedPlace(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]).dict() for row in results]
        # return resultDict
        whereCondition = {}
        if search:
            whereCondition = {"$or": [{"_id": {"$regex": search}}, {"Address": {"$regex": search}}, {"UnitNo": {"$regex": search}}, 
                                    {"Name": {"$regex": search}}, {"Organization": {"$regex": search}}, {"Points": {"$regex": search} }] }
        
        signedPlaces = []
        order = 1
        if sort is not None:
            if order is not None and order == "desc":
                order = -1 
        
            signedPlaces = self.__connection.find(whereCondition).sort({sort: order}).limit(int(limit)).skip(int(offset) * int(limit))
        else:
            signedPlaces = self.__connection.find(whereCondition).limit(int(limit)).skip(int(offset) * int(limit))

        resultDict = [SignedPlace(row["_id"], row["Address"], row["UnitNo"], row["Name"], row["Organization"], row["Category"], {"Cuisine": ["Chinese"]}, row["Points"], row["Checkpoint"], row["Discount"]).dict() for row in signedPlaces]
        return resultDict

    def CreateEntry(self, shopInfo: SignedPlace):
        # cursor = self.__connection.cursor()

        # try:
        #     cursor.execute('INSERT INTO SignedPlaces VALUES(NULL, "{}", "{}", "{}", "{}", {}, {}, {});'
        #                     .format(shopInfo.getAddress(), shopInfo.getUnitNo(), shopInfo.getShopName(), shopInfo.getOrganization(), 
        #                             shopInfo.getPoints(), shopInfo.getCheckpoint(), shopInfo.getDiscount()))
        # except Exception as e:
        #     return {"success": False, "error": "Such location is already registered"}

        # self.__connection.commit()
        # cursor.close()
        # return {"success": True}

        try:
            self.__connection.insert_one({"Address": shopInfo.getAddress(), "UnitNo": shopInfo.getUnitNo(), 
                                        "Name": shopInfo.getShopName(), "Organization": shopInfo.getOrganization(), 
                                        "Category": shopInfo.getCategory(), "Details": shopInfo.getDetails(),
                                        "Points": shopInfo.getPoints(), "Checkpoint": shopInfo.getCheckpoint(), 
                                        "Discount": float(shopInfo.getDiscount()), "RedeemCodes": []})
        except Exception as e:
            print(e)
            return {"success": False, "error": "Such location is already registered"}

        return {"success": True}

    def UpdateEntry(self, shopInfo: SignedPlace):
        # cursor = self.__connection.cursor()

        # try:
        #     cursor.execute('UPDATE SignedPlaces SET '
        #                     'Address = "{}", UnitNo = "{}", ShopName = "{}",'
        #                     'Organization = "{}", Points = {}, Checkpoint = {}, Discount = {} '
        #                     'WHERE Id = {};'
        #                     .format(shopInfo.getAddress(), shopInfo.getUnitNo(), shopInfo.getShopName(), shopInfo.getOrganization(), 
        #                             shopInfo.getPoints(), shopInfo.getCheckpoint(), shopInfo.getDiscount(), shopInfo.getId()))
        # except Exception as e:
        #     print(e)
        #     return {"success": False, "error": "An error occurred updating the place"}
        
        # self.__connection.commit()
        # cursor.close()
        # return {"success": True}

        try:
            self.__connection.update_one({"_id": ObjectId(shopInfo.getId())}, 
                                            {"$set": 
                                                {
                                                    "Address": shopInfo.getAddress(), "UnitNo": shopInfo.getUnitNo(), 
                                                    "Name": shopInfo.getShopName(), "Organization": shopInfo.getOrganization(), 
                                                    "Category": shopInfo.getCategory(), "Details": shopInfo.getDetails(),
                                                    "Points": shopInfo.getPoints(), "Checkpoint": shopInfo.getCheckpoint(), 
                                                    "Discount": shopInfo.getDiscount()
                                                }
                                            })
        except Exception as e:
            print(e)
            return {"success": False, "error": "An error occurred updating the place"}
        
        return {"success": True}
    
    def DeleteEntry(self, shopId):
        # cursor = self.__connection.cursor()

        # try:
        #     cursor.execute('DELETE FROM SignedPlaces '
        #                     'WHERE Id = {};'
        #                     .format(shopId))
        # except Exception as e:
        #     cursor.close()
        #     return {"success": False, "error": "An error occurred removing the place"}
        
        # self.__connection.commit()
        # cursor.close()

        # return {"success": True}
        try:
            self.__connection.delete_one({"_id": ObjectId(shopId)})
        except Exception as e:
            return {"success": False, "error": "An error occurred removing the place"}
        
        return {"success": True}
    
    def GetShopById(self, placeId):
        try:
            shop = self.__connection.find_one({"_id": ObjectId(placeId)})
            print(shop)
            if shop is not None:
                return SignedPlace(shop["_id"], shop["Address"], shop["UnitNo"], shop["Name"], shop["Organization"], 
                                    shop["Category"], shop["Details"], shop["Points"], shop["Checkpoint"], shop["Discount"])
        except Exception as e:
            return 

    def CheckPlace(self, name):
        return self.__connection.find_one({"Name": name}) is not None

    def GenNewCode(self, placeId):
        code = ""
        for _ in range(4):
            code += str(random.randint(0, 9))
        try:
            self.__connection.update_one({"_id": ObjectId(placeId)}, {"$push": {"RedeemCodes": code}})
            return {"success": True}
        except Exception as e:
            print(e)
            return {"success": False}

    def GetRedeemCodes(self, placeId):
        shop = self.__connection.find_one({"_id": placeId})
        if shop is not None:
            return shop["RedeemCodes"]
