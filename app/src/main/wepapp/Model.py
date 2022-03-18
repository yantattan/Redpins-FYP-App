from audioop import add
import email
from wtforms import Form, StringField, RadioField, SelectField, PasswordField, IntegerField, \
                    DecimalField, FileField, validators


# Model for webforms to be processed
class SampleForm(Form):
    firstfield = StringField("First Name", [validators.Length(min=1, max=50), validators.DataRequired()])


class RegisterForm(Form):
    username = StringField("User Name", [validators.Length(min=1, max=100), validators.DataRequired()])
    email = StringField("Email", [validators.Email("someone@example.com"), validators.DataRequired()])
    contact = IntegerField("Mobile Number", [validators.DataRequired()])
    password = PasswordField("Password", [validators.Length(min=7), validators.DataRequired()])
    confirm_password = PasswordField("Confirm Password", [validators.Length(min=7), validators.EqualTo("password", message="Both passwords must match"), validators.DataRequired()])


class LoginForm(Form):
    username = StringField("User Name", [validators.DataRequired()])
    password = PasswordField("Password", [validators.DataRequired()])


#Models
class User:
    def __init__(self, username, email, contact, password):
        self.__username = username
        self.__email = email
        self.__contact = contact
        self.__password = password

    def setUsername(self, username):
        self.__username = username

    def setEmail(self, email):
        self.__email = email

    def setContact(self, contact):
        self.__contact = contact

    def setPassword(self, password):
        self.__password = password

    def getUsername(self):
        return self.__username

    def getEmail(self):
        return self.__email

    def getContact(self):
        return self.__contact

    def getPassword(self):
        return self.__password


class TrackedPlace:
    def __init__(self, userId, address, storeMean):
        self.__userId = userId
        self.__address = address
        self.__storeMean = storeMean
        self.__frequency = 0

    def setAddress(self, address):
        self.__address = address
    
    def setStoreMean(self, storeMean):
        self.__storeMean = storeMean

    def setFrequency(self, frequency):
        self.__frequency = frequency

    def getUserId(self):
        return self.__userId
    
    def getAddress(self):
        return self.__address
    
    def getStoreMean(self):
        return self.__storeMean

    def getFrequency(self):
        return self.__frequency
