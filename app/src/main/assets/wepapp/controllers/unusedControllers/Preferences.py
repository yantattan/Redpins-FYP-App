from datetime import datetime
from DbContext import MySql
from DbContext import MongoDBContext
from Model import Preferences


# class PreferencesCon:
#     __connection = None

#     def __init__(self):
#         self.__connection = MongoDBContext.Connect()["Users"]
    
#     def SetPreferences(self, preferences):
#         cursor = self.__connection.cursor()
#         category = preferences.getCategory()
#         try:
#             cursor.execute('DELETE FROM Preferences WHERE '
#                             'UserId = {} AND Category = "{}";'
#                             .format(preferences.getUserId(), category ))
#         except Exception as e:
#             print("An error occurred reseting entries for preferences")


#         for pref in preferences.getPreferences():
#             try:
#                 cursor.execute('INSERT INTO Preferences '
#                                 'VALUES(NULL, {}, "{}", "{}");'
#                                 .format(preferences.getUserId(), pref, category))
#             except Exception as e:
#                 print("An error occurred updating database for preferences")
#                 print(e)


#         self.__connection.commit()
#         cursor.close()
#         print("Hello")


#     def GetPreferences(self, userId, category):
#         cursor = self.__connection.cursor()
#         cursor.execute('SELECT * FROM Preferences '
#                         'WHERE UserId = {}; AND Category = "{}"'
#                         .format(userId, category))
#         preferences = cursor.fetchone()

#         return Preferences(userId, preferences[2], preferences[3])
