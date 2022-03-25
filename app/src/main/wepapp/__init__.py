from urllib import response
from urllib.error import HTTPError
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from datetime import datetime, timedelta, date
import time, pandas, geocoder, requests, random, string
import json
from io import BytesIO

# Email libraries
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Database modules
import DbContext
from helpers.permissionValidator import *
from Model import *
from controllers import SignedPlaces, Users, TrackedPlaces, UserPoints, Preferences

# Qrcode libraries
from flask_cors import CORS
import qrcode

app = Flask(__name__)
CORS(app)
app.secret_key = "redp1n5Buffer"

# Init all controllers
userCon = Users.UserCon()
trackedPlacesCon = TrackedPlaces.TrackedPlacesCon()
preferencesCon = Preferences.PreferencesCon()
signedPlaceCon = SignedPlaces.SignedPlacesCon()
userRewardsCon = UserPoints.UserPointsCon()


# Functions to perform before showing the page
@app.route("/", methods=['GET', 'POST'])
def mainPage():
    # To render the page (pathing starts from templates folder after). After the filename, variables defined behind are
    # data that the site needs to use
    # session.pop("current_user", None)
    validateLoggedIn()
    yourLocation = geocoder.ip("me")
    print(yourLocation.latlng)

    if request.method == 'POST':
        return redirect("/")
    # For functions to perform before loading of site
    else:
        if session.get("current_user") is None:
            return redirect("/login")

        yourLocation = geocoder.ipinfo("")
        return render_template("main.html", locationCoords=",".join("%.11f" % coord for coord in yourLocation.latlng),
                               y="Meh")


@app.route("/login", methods=['GET', 'POST'])
def login():
    # To render the page (pathing starts from templates folder after). After the filename, variables defined behind are
    # data that the site needs to use
    login_form = LoginForm(request.form)

    if request.method == 'POST' and login_form.validate():
        userInfo = userCon.Login(login_form)
        if userInfo:
            if userInfo.get("error") is None:
                session["current_user"] = userInfo
                print(userInfo)
                return redirect("/")

        return render_template("accounts/login.html", form=login_form, error="Invalid username or password")

    return render_template("accounts/login.html", form=login_form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    register_form = RegisterForm(request.form)

    if request.method == 'POST':
        if register_form.validate():
            userModel = User(register_form.username.data, register_form.email.data, "User", register_form.dateOfBirth.data, register_form.contact.data, register_form.password.data)
            registerResponse = userCon.Register(userModel)
            if registerResponse.get("error"):
                return render_template("accounts/register.html", form=register_form, error=registerResponse["error"])
            else:
                return redirect("/login")

        return render_template("accounts/register.html", form=register_form, error="Invalid fields submitted")

    return render_template("accounts/register.html", form=register_form)


@app.route("/forgetPassword", methods=['GET', 'POST'])
def forgetPassword():
    forget_password_form = ForgetPasswordForm(request.form)

    if request.method == 'POST' and forget_password_form.validate():
        # Generate random string of characters
        newPassword = "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(12))

        # Reset password
        result = userCon.ChangePassword(session['current_user']['userId'], newPassword)
        if result.get("success"):
            # Create email to send new password
            mailFrom = "redpinsbuffer@gmail.com" 
            mailTo = forget_password_form.email.data
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "Change of password"
            msg['From'] = mailFrom
            msg['To'] = mailTo
            emailBody = '<div class="container text-center">' \
                        '<h1>Redpins Buffer</h1>' \
                        '<p>Your password has been reset:</p>' \
                        '<p><b>{}</b></p>' \
                        '</div>'.format(newPassword)

            msg.attach(MIMEText(emailBody, "html"))

            mail = smtplib.SMTP('smtp.gmail.com', 587)
            mail.ehlo
            mail.starttls()
            mail.login('Redpins Buffer', 'redpinsP@ssw0rd')
            mail.sendmail(mailFrom, mailTo, msg.as_string())
            mail.quit()

            return redirect("/login")
            
        return render_template("accounts/forgetPassword.html", form=forget_password_form, error="An error occurred")

    return render_template("accounts/forgetPassword.html", form=forget_password_form)


# Preferences backend -- Send pref to db (Daoying)
@app.route("/preferences/1", methods=['GET', 'POST'])
def pref1():
    validateLoggedIn()
    if request.method == 'POST':
        category = "Cuisine"
        allPrefs = request.form.getlist("preferences[]")
        pref = Preferences.Preferences(session["current_user"]["userId"], allPrefs, category)
        preferencesCon.setPreferences(pref)
        print(allPrefs)
        return redirect("/preferences/2")
    else:
        print("Hello")
    return render_template("preferences/preference1.html")


@app.route("/qr-scanner")
def scanQR():
    return render_template("qrSites/qrScanner.html")


@app.route("/qrCode/arrival")
def qrCodeArrival():
    return render_template("qrSites/arrivalQrCode.html")


# ADMIN SITES
@app.route("/admin/signedPlaces")
def viewSignedPlaces():
    validateAdmin()
    return render_template("admin/viewSignedPlaces.html")

@app.route("/admin/signedPlaces/create", methods=['GET', 'POST'])
def adminCreatePlace():
    validateAdmin()
    signedPlaceForm = SignedPlaceForm(request.form)
    if request.method == 'POST':
        if signedPlaceForm.validate():
            signedPlace = SignedPlaces.SignedPlace(None, signedPlaceForm.address.data, signedPlaceForm.unitNo.data, signedPlaceForm.shopName.data, 
                        signedPlaceForm.organization.data, signedPlaceForm.points.data)
            response = signedPlaceCon.CreateEntry(signedPlace)

            if response.get("success"):
                return redirect("/admin/signedPlaces")
            else:
                return render_template("admin/createSignedPlace.html", form=signedPlaceForm, error=response["error"])
        
        return render_template("admin/createSignedPlace.html", form=signedPlaceForm, error="Invalid inputs entered")

    else:
        return render_template("admin/createSignedPlace.html", form=signedPlaceForm)

@app.route("/admin/signedPlaces/update/<int:id>", methods=['GET', 'POST'])
def adminUpdatePlace(id):
    validateAdmin()
    signedPlaceForm = SignedPlaceForm(request.form)
    if request.method == 'POST':
        if signedPlaceForm.validate():
            signedPlace = SignedPlaces.SignedPlace(id, signedPlaceForm.address.data, signedPlaceForm.unitNo.data, signedPlaceForm.shopName.data, 
                        signedPlaceForm.organization.data, signedPlaceForm.points.data)
            response = signedPlaceCon.UpdateEntry(signedPlace)
            print(response)

            if response.get("success"):
                return redirect("/admin/signedPlaces")
            else:
                return render_template("admin/editSignedPlace.html", form=signedPlaceForm, error=response["error"])
        
        return render_template("admin/editSignedPlace.html", form=signedPlaceForm, error="Invalid inputs entered")

    else:
        placeInfo = signedPlaceCon.GetShopInfo(id)
        signedPlaceForm.address.data = placeInfo.getAddress()
        signedPlaceForm.unitNo.data = placeInfo.getUnitNo()
        signedPlaceForm.shopName.data = placeInfo.getShopName()
        signedPlaceForm.organization.data = placeInfo.getOrganization()
        signedPlaceForm.points.data = placeInfo.getPoints()

        return render_template("admin/createSignedPlace.html", form=signedPlaceForm)

@app.route("/admin/signedPlaces/delete/<int:id>")
def adminDeletePlace(id):
    validateAdmin()
    response = signedPlaceCon.DeleteEntry(id)
    return redirect("/admin/signedPlaces")


# AJAX CALLS
# Reward points -- Assign rewards point (Udhaya)
@app.route("/funcs/reached-place/", methods=['GET', 'POST'])
def reachedPlace():
    # Placeholder returned data
    Utier = {"Bronze": 1, "Silver": 1.1, "Gold": 1.2, "Platinum": 1.3, "Diamond": 1.5}
    Uid = session["current_user"]["userId"]
    result = {"shopName":"MARINA BAY SANDS", "address": "1 BAYFRONT AVENUE MARINA BAY SANDS SINGAPORE 018971"}
    result2 = signedPlaceCon.getShopInfo()
    points = result2.getPoints()
    result3 = userRewardsCon.GetUserPointsInfo(Uid)
    uTierMultiplier = Utier.get(result3.getTier())
    uPoints = result3.getPoints()
    total_pts_earned = points*Utier
    new_upoints = total_pts_earned + uPoints
    userRewardsCon.SetPoints(Uid, new_upoints)
    def UpdateTier():
        OldRank = result3.getTier()
        NewRank = " "
        if 400<=new_upoints<1900:
            NewRank = "Silver"
        elif 1900<=new_upoints<5400:
            NewRank = "Gold"
        elif 5400<=new_upoints<11600:
            NewRank = "Platinum"
        elif new_upoints>=11600:
            NewRank = "Diamond"
            
        userRewardsCon.SetTier(Uid, NewRank)
        return json.dumps({"OldRank": OldRank,"NewRank": NewRank, "OldPoints": uPoints, "NewPoints": new_upoints })
    UpdateTier()

def trackPlaces(places, storeMean):
    # Track down the destinations for future recommendation algorithm
    for place in places:
        trackedPlacesCon.SetInfo(TrackedPlace(session["current_user"]["user_id"], place["address"], storeMean))

@app.route("/funcs/post-places/", methods=['POST'])
def recommendPlace():
    finalResult = {}
    trackPlaces(request.form.get("destinations"), request.form.get("storeMean"))

    return json.dumps(finalResult) 

@app.route("/funcs/mark-tracked/", methods=['POST'])
def markTracked():
    trackPlaces(request.form.get("places"), request.form.get("storeMean"))

@app.route("/funcs/admin/table_getSignedPlaces")
def tableGetSignedPlaces():
    args = request.args
    resultDict = signedPlaceCon.ViewListOfPlaces(args.get("search"), args.get("sort"), args.get("order"), args.get("limit"), args.get("offset"))
    return json.dumps(resultDict)

@app.route("/funcs/generate-arrival-qrcode", methods=['POST'])
def genQRCode():
    buffer = BytesIO()
    data = request.form.get("data")

    img = qrcode.make(data)
    img.save(buffer)
    buffer.seek(0)

    response = send_file(buffer, mimetype='image/png')
    return response


@app.route("/funcs/use-points", methods=['POST'])
def usePoints():
    return 


# Error pages handling
# @app.errorhandler(403)
# def forbidden_error(error):
#     return render_template(""), 403

# Form submit methods starts here
# @app.route("/", methods=['GET', 'POST'])
# def formSubmit():
#     sample_form = SampleForm(request.form)
#     if request.method == 'POST' and sample_form.validate():
#         # Operations starts here
#         x = 0
#     return redirect("/")


if __name__ == '__main__':
    app.run()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
