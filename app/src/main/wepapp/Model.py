from wtforms import Form, StringField, RadioField, SelectField, PasswordField, IntegerField, TextAreaField, \
                    DecimalField, FileField, validators


# Model for webforms to be processed
class SampleForm(Form):
    firstfield = StringField("First Name", [validators.Length(min=1, max=50), validators.DataRequired()])


class RegisterForm(Form):
    username = StringField("User Name", [validators.Length(min=1, max=100), validators.DataRequired()])
    contact = IntegerField("Mobile Number", [validators.DataRequired()])
    password = PasswordField("Password", [validators.Length(min=7), validators.DataRequired()])
    confirm_password = PasswordField("Confirm Password", [validators.Length(min=7), validators.EqualTo("password", message="Both passwords must match"), validators.DataRequired()])

class LoginForm(Form):
    username = StringField("User Name", [validators.DataRequired()])
    password = PasswordField("Password", [validators.DataRequired()])


#Models
class User:
    def __init__(self, username, contact, password):
        self.__username = username
        self.__contact = contact
        self.__password = password

    def setUsername(self, username):
        self.__username = username

    def setContact(self, contact):
        self.__contact = contact

    def setPassword(self, password):
        self.__password = password

    def getUsername(self):
        return self.__username

    def getContact(self):
        return self.__contact

    def getPassword(self):
        return self.__password
