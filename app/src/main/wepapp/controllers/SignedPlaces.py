from DbContext import MySql
from Model import SignedPlace


class SignedPlacesCon:
    __connection = None

    def __init__(self):
        self.__connection = MySql.Connect()["PartneredPlaces"]

    def GetShopInfo(self, id):
        # cursor = self.__connection.cursor()

        # cursor.execute('SELECT * FROM SignedPlaces WHERE Id = "{}";'
        #                 .format(id))
        # shop = cursor.fetchone()
        # if shop is not None:
        #     return SignedPlace(shop[0], shop[1], shop[2], shop[3], shop[4], shop[5], shop[6], shop[7])

        shop = self.__connection.findOne({"_id": id})
        if shop is not None:
            return SignedPlace(shop["_id"], shop["Address"], shop["UnitNo"], shop["Name"], shop["Organization"], shop["Point"], shop["Checkpoint"], shop["Discount"])

    def ViewListOfPlaces(self, search, sort, order, limit, offset):
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

        whereCondition = {"$or": [{"Id": "/{}/".format(search)}, {"Address": "/{}/".format(search)}, {"UnitNo": "/{}/".format(search)}, 
                                {"Name": "/{}/".format(search)}, {"Organization": "/{}/".format(search)}, {"Points": "/{}/".format(search)}] }
        
        orderCondition = {}
        if sort:
            if order is not None and order == "desc":
                orderCondition = { sort: 1 }
            else:
                orderCondition = { sort: -1 }
        
        signedPlaces = self.__connection.find({whereCondition}).sort(orderCondition).limit(int(limit)).skip(int(offset) * int(limit))
        resultDict = [SignedPlace(row["_id"], row["Address"], row["UnitNo"], row["Name"], row["Organization"], row["Point"], row["Checkpoint"], row["Discount"]).dict() for row in signedPlaces]
        return resultDict

    def CreateEntry(self, shopInfo):
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
                                        "Points": shopInfo.getPoints(), "Checkpoint": shopInfo.getCheckpoint(), 
                                        "Discount": shopInfo.getDiscount()})
        except Exception as e:
            return {"success": False, "error": "Such location is already registered"}

        return {"success": True}

    def UpdateEntry(self, shopInfo):
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
            self.__connection.update_one({"_id": shopInfo.getId()}, 
                                            {"$set": 
                                                {
                                                    "Address": shopInfo.getAddress(), "UnitNo": shopInfo.getUnitNo(), 
                                                    "Name": shopInfo.getShopName(), "Organization": shopInfo.getOrganization(), 
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
            self.__connection.delete_one({"_id": shopId})
        except Exception as e:
            return {"success": False, "error": "An error occurred removing the place"}
        
        return {"success": True}
        