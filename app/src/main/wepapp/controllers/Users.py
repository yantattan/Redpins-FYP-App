import random
import string
from DbContext import MySql
import hashlib

class UserCon:
    __connection = None

    def __init__(self):
        self.__connection = MySql.Connect()

    def Login(self, user):
        if self.__isLoginValid(user):
            self.__Authorize(user)
        else:
            user.setErrMsg("Incorrect username and password")

    def Register(self, user):
        passwordSalt = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        passwordHash = hashlib.sha512(user.password + passwordSalt).hexdigest()
        cursor = self.__connection.cursor()
        cursor.execute("INSERT INTO Users VALUES()")
        self.__connection.commit()
        cursor.close()
        return True


    def __isLoginValid(self, user):
        cursor = self.__connection.cursor()
        cursor.execute("SELECT passwordSalt FROM Users WHERE username = {}".format(user.username))
        if cursor["passwordSalt"]:
            passwordHash = hashlib.sha512(user.password + cursor["passwordSalt"]).hexdigest()
            cursor.execute("SELECT id FROM Users WHERE username = {} AND password = {}".format(user.username, passwordHash))
            if cursor["id"]:
                return True

        return False

