from DbContext import MySql
from Model import SignedPlace


class SignedPlacesCon:
    __connection = None

    def __init__(self):
        self.__connection = MySql.Connect()

    def GetShopInfo(self, id):
        cursor = self.__connection.cursor()

        cursor.execute('SELECT * FROM SignedPlaces WHERE Id = "{}";'
                        .format(id))
        shop = cursor.fetchone()
        if shop is not None:
            return SignedPlace(shop[0], shop[1], shop[2], shop[3], shop[4], shop[5])

    def ViewListOfPlaces(self, search, sort, order, limit, offset):
        cursor = self.__connection.cursor()

        whereCondition = 'Id LIKE "%{}%" OR Address LIKE "%{}%" OR UnitNo LIKE "%{}%" OR ShopName LIKE "%{}%" OR '\
                        'Organization LIKE "%{}%" OR Points LIKE "%{}%"'\
                        .format(search, search, search, search, search, search)
        
        sortAndOrder = ''
        if sort:
            sortAndOrder += 'ORDER BY {}'.format(sort)
            if order is not None and order == "desc":
                sortAndOrder += ', DESC'

        cursor.execute('SELECT * FROM SignedPlaces '
                        'WHERE {} {} '
                        'LIMIT {} OFFSET {};'
                        .format(whereCondition, sortAndOrder, limit, int(offset)*int(limit) ))
        results = cursor.fetchall()
        resultDict = [SignedPlace(row[0], row[1], row[2], row[3], row[4], row[5]).dict() for row in results]
        return resultDict

    def CreateEntry(self, shopInfo):
        cursor = self.__connection.cursor()

        try:
            cursor.execute('INSERT INTO SignedPlaces VALUES(NULL, "{}", "{}", "{}", "{}", {});'
                            .format(shopInfo.getAddress(), shopInfo.getUnitNo(), shopInfo.getShopName(), shopInfo.getOrganization(), 
                                    shopInfo.getPoints()))
        except Exception as e:
            return {"success": False, "error": "Such location is already registered"}

        self.__connection.commit()
        cursor.close()
        return {"success": True}

    def UpdateEntry(self, shopInfo):
        cursor = self.__connection.cursor()

        try:
            cursor.execute('UPDATE SignedPlaces SET '
                            'Address = "{}", UnitNo = "{}", ShopName = "{}",'
                            'Organization = "{}", Points = {} '
                            'WHERE Id = {};'
                            .format(shopInfo.getAddress(), shopInfo.getUnitNo(), shopInfo.getShopName(), shopInfo.getOrganization(), 
                                    shopInfo.getPoints(), shopInfo.getId()))
        except Exception as e:
            print(e)
            return {"success": False, "error": "An error occurred updating the place"}
        
        self.__connection.commit()
        cursor.close()
        return {"success": True}
    
    def DeleteEntry(self, shopId):
        cursor = self.__connection.cursor()

        try:
            cursor.execute('DELETE FROM SignedPlaces '
                            'WHERE Id = {};'
                            .format(shopId))
        except Exception as e:
            cursor.close()
            return {"success": False, "error": "An error occurred removing the place"}
        
        self.__connection.commit()
        cursor.close()

        return {"success": True}
        