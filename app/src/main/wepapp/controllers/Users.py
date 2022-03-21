import random
import string
from DbContext import MySql
import hashlib


class UserCon:
    __connection = None

    def __init__(self):
        self.__connection = MySql.Connect()

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

        return {"error": "Incorrect username and password"}

    def Register(self, user):
        passwordSalt = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        passwordHash = hashlib.sha512((user.getPassword() + passwordSalt).encode("utf-8")).hexdigest()
        cursor = self.__connection.cursor()
        try:
            cursor.execute('INSERT INTO Users VALUES(NULL, "{}", "{}", "{}", "{}", "{}", "{}");'.format(user.getUsername(), user.getEmail(), 
                                                                                    user.getAge(), str(user.getContact()) ,passwordHash, passwordSalt))
        except Exception as e:
            print(e)

        self.__connection.commit()
        cursor.close()
        return {"success": True}

