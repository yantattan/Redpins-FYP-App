# import hashlib
# import random
# import string

# # For web form inputs
# class Users:
#     def __init__(self, username, password, contact, photo):
#         self.__username = username
#         self.__passwordSalt = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
#         self.__password = hashlib.sha512(password).hexdigest()
#         self.__contact = contact
#         self.__photo = photo
#         self.__preferences = []

#     __userid = 0
#     __username = ""
#     __password = ""
#     __contact = ""
#     __passwordSalt = ""
#     __err_msg = ""

#     def setErrMsg(self, err):
#         self.__err_msg = err

#     def getUsername(self):
#         return self.__username

#     def getContact(self):
#         return self.__contact

#     def setPreferences(self, preferences):
#         self.__preferences = preferences
