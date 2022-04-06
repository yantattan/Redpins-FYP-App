from audioop import add
from decimal import Decimal
import email
from wtforms import Form, StringField, RadioField, SelectField, PasswordField, IntegerField, \
                    DecimalField, FileField, TextAreaField, validators
from wtforms.fields.html5 import DateField


# Webforms helper
class SampleForm(Form):
    firstfield = StringField("First Name", [validators.Length(min=1, max=50), validators.DataRequired()])

class RegisterForm(Form):
    username = StringField("User Name", [validators.Length(min=1, max=20), validators.DataRequired()])
    email = StringField("Email", [validators.Email("someone@example.com"), validators.DataRequired()])
    dateOfBirth = DateField("Date Of Birth", [validators.DataRequired()])
    contact = IntegerField("Mobile Number", [validators.DataRequired()])
    password = PasswordField("Password", [validators.Length(min=7), validators.DataRequired()])
    confirm_password = PasswordField("Confirm Password", [validators.Length(min=7), validators.EqualTo("password", message="Both passwords must match"), validators.DataRequired()])

class LoginForm(Form):
    username = StringField("User Name", [validators.DataRequired()])
    password = PasswordField("Password", [validators.DataRequired()])

class ForgetPasswordForm(Form):
    username = StringField("User Name", [validators.Length(min=1, max=20), validators.DataRequired()])
    email = StringField("Email", [validators.Email("someone@example.com"), validators.DataRequired()])

class SignedPlaceForm(Form):
    shopName = StringField("Shop Name", [validators.DataRequired()])
    organization = StringField("Organization Name", [validators.DataRequired()])
    address = StringField("Address", [validators.DataRequired()])
    unitNo = StringField("Unit Number", [validators.DataRequired()])
    points = IntegerField("Points", [validators.NumberRange(min=3, max=50), validators.Optional()])
    checkpoint = IntegerField("Points Needed", [validators.NumberRange(min=20, max=1000), validators.Optional()])
    discount = DecimalField("Discount (%)", [validators.Optional()], places=2)

class ReviewForm(Form):
    rating = IntegerField("Rating", [validators.NumberRange(min=1, max=5), validators.DataRequired()])
    review = TextAreaField("Review", [validators.DataRequired()])

#Models
class User:
    def __init__(self, username, email, role, dateOfBirth, contact, password, points, tierPoints, tier):
        self.__username = username
        self.__email = email
        self.__role = role
        self.__dateOfBirth = dateOfBirth
        self.__contact = contact
        self.__password = password
        self.__points = points
        self.__tierPoints = tierPoints
        self.__tier = tier

    def setUsername(self, username):
        self.__username = username

    def setEmail(self, email):
        self.__email = email

    def setRole(self, role):
        self.__role = role

    def setDateOfBirth(self, dateOfBirth):
        self.__dateOfBirth = dateOfBirth

    def setContact(self, contact):
        self.__contact = contact

    def setPassword(self, password):
        self.__password = password

    def setPoints(self, points):
        self.__points = points

    def setTierPoints(self, tierPoints):
        self.__tierPoints = tierPoints

    def setTier(self, tier):
        self.__tier = tier

    def getUsername(self):
        return self.__username

    def getEmail(self):
        return self.__email

    def getRole(self):
        return self.__role

    def getDateOfBirth(self):
        return self.__dateOfBirth

    def getContact(self):
        return self.__contact

    def getPassword(self):
        return self.__password

    def getPoints(self):
        return self.__points

    def getTierPoints(self):
        return self.__tierPoints

    def getTier(self):
        return self.__tier


class TrackedPlace:
    def __init__(self, userId, address, placeName, storeMean):
        self.__userId = userId
        self.__address = address
        self.__placeName = placeName
        self.__storeMean = storeMean
        self.__frequency = 0
        self.__timestamps = []

    def setAddress(self, address):
        self.__address = address

    def setPlaceName(self, placeName):
        self.__placeName = placeName
    
    def setStoreMean(self, storeMean):
        self.__storeMean = storeMean

    def setFrequency(self, frequency):
        self.__frequency = frequency

    def setTimestamps(self, timestamps):
        self.__timestamps = timestamps

    def getUserId(self):
        return self.__userId
    
    def getAddress(self):
        return self.__address

    def getPlaceName(self):
        return self.__placeName
    
    def getStoreMean(self):
        return self.__storeMean

    def getFrequency(self):
        return self.__frequency

    def getTimestamps(self):
        return self.__timestamps


class UserPoints:
    def __init__(self, userId, points, tier):
        self.__userId = userId
        self.__points = points
        self.__tier = tier

    def getUserId(self):
        return self.__userId
    
    def getPoints(self):
        return self.__points

    def getTier(self):
        return self.__tier


class Preferences:
    def __init__(self, userId, preferences, category):
        self.__userId = userId
        self.__preferences = preferences
        self.__category = category

    def setPreferences(self, preferences):
        self.__preferences = preferences

    def getUserId(self):
        return self.__userId

    def getPreferences(self):
        return self.__preferences

    def getCategory(self):
        return self.__category


class SignedPlace:
    def __init__(self, id, address, unitNo, shopName, organization, category, details, points, checkpoint, discount):
        self.__id = str(id)
        self.__address = address
        self.__unitNo = unitNo
        self.__shopName = shopName
        self.__organization = organization
        self.__category = category
        self.__details = details
        self.__points = points
        self.__checkpoint = checkpoint
        self.__discount = float(discount)

    def setAddress(self, address):
        self.__address = address

    def setUnitNo(self, unitNo):
        self.__unitNo = unitNo

    def setShopName(self, shopName):
        self.__shopName = shopName

    def setOrganization(self, organization):
        self.__organization = organization

    def setCategory(self, category):
        self.__category = category

    def setDetails(self, details):
        self.__details = details

    def setPoints(self, points):
        self.__points = points

    def setCheckpoint(self, checkpoint):
        self.__checkpoint = checkpoint

    def setDiscount(self, discount):
        self.__discount = discount

    def getId(self):
        return self.__id

    def getAddress(self):
        return self.__address

    def getUnitNo(self):
        return self.__unitNo

    def getShopName(self):
        return self.__shopName

    def getOrganization(self):
        return self.__organization

    def getCategory(self):
        return self.__category

    def getDetails(self):
        return self.__details
        
    def getPoints(self):
        return self.__points
    
    def getCheckpoint(self):
        return self.__checkpoint

    def getDiscount(self):
        return self.__discount

    def dict(self):
        return {"id":           self.getId(), 
                "address":      self.getAddress(), 
                "unitNo":       self.getUnitNo(), 
                "shopName":     self.getShopName(),
                "organization": self.getOrganization(),
                "category":     self.getCategory(),
                "details":      self.getDetails(),
                "points":       self.getPoints(),
                "checkpoint":   self.getCheckpoint(),
                "discount":     self.getDiscount()}


class Review:
    def __init__(self, rating, review):
        self.__rating = rating
        self.__review = review
    
    def setRating(self, rating):
        self.__rating = rating

    def setReview(self, review):
        self.__review = review

    def getRating(self):
        return self.__rating

    def getReview(self):
        return self.__review


class MachineLearningReport:
    def __init__(self, modelName, attribute, data):
        self.__modelName = modelName
        self.__attribute = attribute
        self.__data = data

    def setModelName(self, modelName):
        self.__modelName = modelName

    def setAttribute(self, attribute):
        self.__attribute = attribute
    
    def setData(self, data):
        self.__data = data

    def getModelName(self):
        return self.__modelName

    def getAttribute(self):
        return self.__attribute

    def getData(self):
        return self.__data

