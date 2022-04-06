import random
import string
import csv
from DbContext import MySql
from DbContext import MongoDBContext
import hashlib

from Model import Preferences
from Model import UserPoints
from Model import User


class UserCon:
    __connection = None

    def __init__(self):
        self.__connection = MongoDBContext.Connect()["Users"]

    # Basic account functions
    def Login(self, user):
        # cursor = self.__connection.cursor()
        # cursor.execute('SELECT pwdSalt FROM Users WHERE username = "{}";'
        #                 .format(user.username.data))

        # dbPwdSalt = cursor.fetchone()[0]
        # if dbPwdSalt is not None:
        #     passwordHash = hashlib.sha512((user.password.data + dbPwdSalt).encode("utf-8")).hexdigest()
        #     cursor.execute('SELECT Id, Username, Role FROM Users WHERE username = "{}" AND password = "{}";'
        #                     .format(user.username.data, passwordHash))

        #     dbInfo = cursor.fetchone()
        #     if dbInfo is not None:
        #         return {"userId": dbInfo[0], "username": dbInfo[1], "role": dbInfo[2]}


        userDBInfo = self.__connection.find_one({"Username": user.username.data})
        if userDBInfo is not None:
            passwordHash = hashlib.sha512((user.password.data + userDBInfo["PasswordSalt"]).encode("utf-8")).hexdigest()
            userVal = self.__connection.find_one({"Username": user.username.data, "Password": passwordHash})
            if userVal is not None:
                return {"userId": userVal["_id"], "username": userVal["Username"], "role": userVal["Role"]}

        return {"error": "Incorrect username and password"}

    def Register(self, user):
        # passwordSalt = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        # passwordHash = hashlib.sha512((user.getPassword() + passwordSalt).encode("utf-8")).hexdigest()
        # cursor = self.__connection.cursor()
        # try:
        #     cursor.execute('INSERT INTO Users VALUES(NULL, "{}", "{}", "{}", "{}", "{}", "{}", "{}");'
        #                     .format(user.getUsername(), user.getEmail(), user.getRole(), user.getDateOfBirth(), str(user.getContact()),
        #                     passwordHash, passwordSalt))
        # except Exception as e:
        #     print(e)
        #     return {"success": False, "error": "Invalid username or email. Please try another one"}

        # self.__connection.commit()
        # cursor.close()
        # return {"success": True}

        passwordSalt = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        passwordHash = hashlib.sha512((user.getPassword() + passwordSalt).encode("utf-8")).hexdigest()
        try:
            checkExist = self.__connection.find_one({"Username": user.getUsername(), "Email": user.getEmail(), "Contact": user.getContact()})
            if checkExist is None:
                self.__connection.insert_one({
                    "_id": self.__connection.find().sort("_id", -1).limit(1)[0]["_id"] + 1,
                    "Username": user.getUsername(), 
                    "Email": user.getEmail(), 
                    "Role": user.getRole(), 
                    "DateOfBirth": str(user.getDateOfBirth()), 
                    "Contact": str(user.getContact()),
                    "Password": passwordHash, 
                    "PasswordSalt": passwordSalt,
                    "Points": user.getPoints(),
                    "TierPoints": user.getTierPoints(),
                    "Tier": user.getTier()
                })
                return {"success": True}

            return {"success": False, "error": "Username, email and contact already exists"}
        except Exception as e:
            print(e)
            return {"success": False, "error": "An error occurred"}
        
    def ChangePassword(self, userId, password):
        # cursor = self.__connection.cursor()
        # passwordSalt = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        # passwordHash = hashlib.sha512((password + passwordSalt).encode("utf-8")).hexdigest()

        # try:
        #     cursor.execute('UPDATE Users SET Password = "{}", PwdSalt = "{}"'
        #                     'WHERE Id = {}'
        #                     .format(passwordHash, passwordSalt, userId))
        # except Exception as e:
        #     print(e)

        # self.__connection.commit()
        # cursor.close()

        passwordSalt = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        passwordHash = hashlib.sha512((password + passwordSalt).encode("utf-8")).hexdigest()

        try:
            self.__connection.update_one({"_id": userId}, {"$set": {"Password": passwordHash, "PasswordSalt": passwordSalt}})
            return {"success": True}

        except Exception as e:
            print(e)
            return {"success": False, "error": "An error occurred"}

    def GetUserById(self, userId):
        try:
            userInfo = self.__connection.find_one({"_id": userId})
            return User(userInfo["Username"], userInfo["Email"], userInfo["Role"], userInfo["DateOfBirth"], userInfo["Contact"], 
                        userInfo["Password"], userInfo["Points"], userInfo["TierPoints"], userInfo["Tier"])
        except Exception as e:
            print(e)
            return {"error": "An error occurred trying to retrieve user information"}


    # Preferences functions
    def SetPreferences(self, preferences):
        # cursor = self.__connection.cursor()
        # category = preferences.getCategory()
        # try:
        #     cursor.execute('DELETE FROM Preferences WHERE '
        #                     'UserId = {} AND Category = "{}";'
        #                     .format(preferences.getUserId(), category ))
        # except Exception as e:
        #     print("An error occurred reseting entries for preferences")


        # for pref in preferences.getPreferences():
        #     try:
        #         cursor.execute('INSERT INTO Preferences '
        #                         'VALUES(NULL, {}, "{}", "{}");'
        #                         .format(preferences.getUserId(), pref, category))
        #     except Exception as e:
        #         print("An error occurred updating database for preferences")
        #         print(e)


        # self.__connection.commit()
        # cursor.close()

        category = preferences.getCategory()
        dbPref = {}
        try:
            userInfo = self.__connection.find_one({"_id": preferences.getUserId()})
            try:
                dbPref = userInfo["Preferences"]
                dbPref[category] = preferences.getPreferences()
            except KeyError:
                dbPref = {category: preferences.getPreferences()}

            print("Here")
            self.__connection.update_one({"_id": preferences.getUserId()}, {"$set": {"Preferences": dbPref}})
        except Exception as e:
            print(e)
            print("An error occurred reseting entries for preferences")
    
    def GetPreferences(self, userId, category):
        # cursor = self.__connection.cursor()
        # cursor.execute('SELECT * FROM Preferences '
        #                 'WHERE UserId = {}; AND Category = "{}"'
        #                 .format(userId, category))
        # preferences = cursor.fetchone()

        # return Preferences(userId, preferences[2], preferences[3])

        try:
            userInfo = self.__connection.find_one({"_id": userId})
            return Preferences(userId, userInfo["Preferences"][category], category) 
        except Exception as e:
            print(e)

    
    # Reward points functions
    def SetReachedDestination(self, address, userId):
        # cursor = self.__connection.cursor()
        # # Update status of destination
        # cursor.execute('UPDATE Itinerary SET Status = "Reached" '
        #                 'WHERE UserId = {} AND Address = "{}" AND Date = DATE(NOW());'
        #                 .format(userId, address))
                        
        # self.__connection.commit()
        # cursor.close()
        print("Hello")

    def GetUserPointsInfo(self, userId):
        # cursor = self.__connection.cursor()
        # cursor.execute('SELECT * FROM UserPoints WHERE UserId = {};'
        #                 .format(userId))
        # resultData = cursor.fetchone()
        # if resultData is not None:
        #     return UserPoints(userId, resultData[0], resultData[1])
        userInfo = self.__connection.find_one({"_id": userId})
        if userInfo is not None:
            return UserPoints(userId, userInfo.get("Points") or 0, userInfo.get("Tier") or "Bronze")

    def SetPoints(self, userId, points, tierPoints):
        # cursor = self.__connection.cursor()
        # # Update points
        # cursor.execute('UPDATE UserPoints SET Points = {} '
        #                 'WHERE UserId = {};'
        #                 .format(points, userId))

        # self.__connection.commit()
        # cursor.close()
        # Update points

        try:
            self.__connection.update_one({"_id": userId}, {"$set": {"Points": points, "TierPoints": tierPoints}})
        except Exception as e:
            print(e)

    def SetTier(self, userId, tier):
        # cursor = self.__connection.cursor()
        # # Update points
        # cursor.execute('UPDATE UserPoints SET Tier = "{}" '
        #                 'WHERE UserId = {};'
        #                 .format(tier, userId))
        try:
            self.__connection.update_one({"_id": userId}, {"$set": {"Tier": tier}})
        except Exception as e:
            print(e)      
            

    # Data export csv functions
    def ExportGlobalUserPreferenceCSV(self):
        path = "csv/dbcsv/global-users-preferences.csv"
        csvFile = open(path, "w", newline="")
        csvWriter = csv.writer(csvFile)
        # Header
        csvWriter.writerow(["BirthYear", "Points", "Tier", "Category", "Preference"])

        allUserInfo = list(self.__connection.find())
        for i in range(1, len(allUserInfo)):
            row = allUserInfo[i]
            preferencesDict = row.get("Preferences") or []
            for cat in preferencesDict:
                for pref in preferencesDict[cat]:
                    csvWriter.writerow([row["DateOfBirth"][:4], row["Points"], row["Tier"], cat, pref])

        return path
