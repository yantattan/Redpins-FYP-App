from wtforms import Form, StringField, RadioField, SelectField, PasswordField, IntegerField, TextAreaField, \
                    DecimalField, FileField, validators


# Model for webforms to be processed
class SampleForm(Form):
    firstfield = StringField("First Name", [validators.Length(min=1, max=50), validators.DataRequired()])


class User(Form):
    username = StringField("User Name", [validators.Length(min=1, max=100), validators.DataRequired()])
    contact = IntegerField("Mobile Number", [validators.Regexp("/[8|9]\d{7}/"), validators.DataRequired()])
    password = PasswordField("Password", [validators.Length(min=7), validators.DataRequired()])
