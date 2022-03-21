from datetime import datetime
from DbContext import MySql
from Model import UserPoints


class UserPoints:
    __connection = None

    def __init__(self):
        self.__connection = MySql.Connect()


    def SetReachedDestination(self, address, userId):
        cursor = self.__connection.cursor()
        # Update status of destination
        cursor.execute('UPDATE Itinerary SET Status = "Reached"'
                        'WHERE UserId = {} AND Address = "{}" AND Date = DATE(NOW());'
                        .format(userId, address))


    def GetUserPoints(self, userId):
        cursor = self.__connection.cursor()
        cursor.execute('SELECT * FROM UserPoints WHERE UserId = {}'
                        .format(userId))
        resultData = cursor.fetchone()
        return UserPoints(userId, resultData[0], resultData[1])


    def SetPoints(self, userId, points):
        cursor = self.__connection.cursor()
        # Update points
        cursor.execute('UPDATE UserPoints SET Points = {}'
                        'WHERE UserId = {};'
                        .format(points, userId))

        self.__connection.commit()
        cursor.close()


    def SetTier(self, userId, tier):
        cursor = self.__connection.cursor()
        # Update points
        cursor.execute('UPDATE UserPoints SET Tier = "{}"'
                        'WHERE UserId = {};'
                        .format(tier, userId))
                        
        self.__connection.commit()
        cursor.close()
