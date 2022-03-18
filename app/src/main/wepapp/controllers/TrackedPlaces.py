import random
import string
from DbContext import MySql
import hashlib


class TrackedPlacesCon:
    __connection = None

    def __init__(self):
        self.__connection = MySql.Connect()
    
    def SetInfo(self, trackedPlace):
        cursor = self.__connection.cursor()
        cursor.execute('SELECT LastRegistered FROM TrackedPlaces WHERE UserId = "{}";'.format(trackedPlace.getUserId()))
        try:
            lastRegisteredDate = cursor.fetchone()[0]
            if lastRegisteredDate:
                try:
                    cursor.execute('INSERT INTO TrackedPlaces VALUES(NULL, "{}", "{}", "{}", "{}", "{}");'.format(trackedPlace.getUserId(), 
                                                trackedPlace.getAddress(), trackedPlace.getStoreMean(), trackedPlace.getFrequency()))
                except Exception as e:
                    print(e)
                    return {"success": False, "error": e}
                    
                self.__connection.commit()
                
        except Exception as e:
            print("Already registered today")
        
        cursor.close()
        return {"success": True}

    def Login(self, user):
        cursor = self.__connection.cursor()
        cursor.execute('SELECT pwdSalt FROM Users WHERE username = "{}";'.format(user.username.data))
        dbPwdSalt = cursor.fetchone()[0]

        if dbPwdSalt is not None:
            passwordHash = hashlib.sha512((user.password.data + dbPwdSalt).encode("utf-8")).hexdigest()
            cursor.execute(
                'SELECT id, username FROM Users WHERE username = "{}" AND password = "{}";'.format(user.username.data, passwordHash))
            dbInfo = cursor.fetchone()
            
            if dbInfo is not None:
                return {"userId": dbInfo[0], "username": dbInfo[1]}
            else:
                user.setErrMsg("Incorrect username and password")

        return {"error": "Incorrect username and password"}
