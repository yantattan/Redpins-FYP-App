from datetime import datetime
from unicodedata import category
from DbContext import MySql
from Model import Preferences


class PreferencesCon:
    __connection = None

    def __init__(self):
        self.__connection = MySql.Connect()
    
    def setPreferences(self, preferences):
        cursor = self.__connection.cursor()
        category = preferences.getCategory()
        try:
            cursor.execute('DELETE FROM Preferences WHERE'
                            'UserId = {} AND Category = "{}";'
                            .format(preferences.getUserId(), category ))
        except Exception:
            print("An error occurred")


        for pref in preferences.getPreferences():
            try:
                cursor.execute('INSERT INTO Preferences'
                                'VALUES(NULL, {}, "{}", "{}");'
                                .format(preferences.getUserId(), pref, category))
            except Exception:
                print("An error occurred updating database for preferences")


        self.__connection.commit()
        cursor.close()


    def getPreferences(self, userId, category):
        cursor = self.__connection.cursor()
        cursor.execute('SELECT * FROM Preferences'
                        'WHERE UserId = {}; AND Category = "{}"'
                        .format(userId, category))
        preferences = cursor.fetchone()

        return Preferences(userId, preferences[2], preferences[3])
