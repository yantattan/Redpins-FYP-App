from DbContext import MySql
from Model import SignedPlace


class SignedPlacesCon:
    __connection = None

    def __init__(self):
        self.__connection = MySql.Connect()

    def getShopInfo(self, shopName, address):
        cursor = self.__connection.cursor()

        cursor.execute('SELECT * FROM SignedPlaces WHERE ShopName = "{}" AND Address = "{}"'
                        .format(shopName, address))
        shop = cursor.fetchone()
        if shop is not None:
            return SignedPlace(shop[0], shop[1], shop[2], shop[3], shop[4], shop[5])

    def createEntry(self, shopInfo):
        cursor = self.__connection.cursor()

        try:
            cursor.execute('INSERT INTO SignedPlaces VALUES("{}", "{}", "{}", "{}", {});'
                            .format(shopInfo.getAddress(), shopInfo.getUnitNo(), shopInfo.getShopName(), shopInfo.getOrganization(), 
                                    shopInfo.getPoints()))
        except Exception as e:
            return {"success": False, "error": "Such location is already registered"}

        self.__connection.commit()
        cursor.close()
        return {"success": True}

    def updateEntry(self, shopInfo):
        cursor = self.__connection.cursor()

        try:
            cursor.execute('UPDATE SignedPlaces SET'
                            'Address = "{}", UnitNo = "{}", ShopName = "{}",'
                            'Organization = "{}", Points = "{}"'
                            'WHERE Id = {};'
                            .format(shopInfo.getAddress(), shopInfo.getUnitNo(), shopInfo.getShopName(), shopInfo.getOrganization(), 
                                    shopInfo.getPoints(), shopInfo.getId()))
        except Exception as e:
            return {"success": False, "error": "An error occurred updating the place"}
        
        self.__connection.commit()
        cursor.close()
        return {"success": True}
    
    def deleteEntry(self, shopId):
        cursor = self.__connection.cursor()

        try:
            cursor.execute('DELETE FROM SignedPlaces'
                            'WHERE Id = {};'
                            .format(shopId))
        except Exception as e:
            return {"success": False, "error": "An error occurred removing the place"}

        return {"success": True}
        