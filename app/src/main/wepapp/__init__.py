from urllib.error import HTTPError
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from apscheduler.scheduler import Scheduler
from io import BytesIO

# Required libraries
from datetime import datetime, timedelta, date
import geocoder, requests, random, string, json, geopy.distance
# Machine learning, csv libraries
import pandas, csv, joblib
from sklearn import preprocessing
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
# Email libraries
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# Database modules
import DbContext
from helpers.permissionValidator import *
from Model import *
from controllers import MachineLearningReports, SignedPlaces, Users, TrackedPlaces, PlacesBonusCodes
# Qrcode libraries
from flask_cors import CORS
import qrcode

app = Flask(__name__)
cron = Scheduler(daemon=True)
cron.start()
CORS(app)
app.secret_key = "redp1n5Buffer"
apiKey = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOjg1NDQsInVzZXJfaWQiOjg1NDQsImVtYWlsIjoieWFudGF0dGFuNzIxQGdtYWlsLmNvbSIsImZvcmV2ZXIiOmZhbHNlLCJpc3MiOiJodHRwOlwvXC9vbTIuZGZlLm9uZW1hcC5zZ1wvYXBpXC92MlwvdXNlclwvc2Vzc2lvbiIsImlhdCI6MTY0ODQ0NTM1NCwiZXhwIjoxNjQ4ODc3MzU0LCJuYmYiOjE2NDg0NDUzNTQsImp0aSI6IjBkYWIzYTIyMDIwMmYxZDA5YzJhYmMxYjEyZjk0M2RhIn0.ygc_daPpwuKKaMqR1MHLVVKBCOtO9cYtGdAnLALGlGI"

# Init all controllers
userCon = Users.UserCon()
trackedPlacesCon = TrackedPlaces.TrackedPlacesCon()
signedPlaceCon = SignedPlaces.SignedPlacesCon()
machineLearningReportCon = MachineLearningReports.MachineLearningReportCon()
placesBonusCodesCon = PlacesBonusCodes.PlacesBonusCodesCon()


# preferencesCon = Preferences.PreferencesCon()
# userRewardsCon = UserPoints.UserPointsCon()

# Functions to perform before showing the page
@app.route("/", methods=['GET', 'POST'])
def mainPage():
    # To render the page (pathing starts from templates folder after). After the filename, variables defined behind are
    # data that the site needs to use
    # session.pop("current_user", None)
    validateLoggedIn()
    yourLocation = geocoder.ip("me")
    userCon.ExportGlobalUserPreferenceCSV()
    scheduledJobs()

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
            userModel = User(register_form.username.data, register_form.email.data, "User",
                             register_form.dateOfBirth.data,
                             register_form.contact.data, register_form.password.data, 0, "Bronze")
            registerResponse = userCon.Register(userModel)
            print(registerResponse)
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
        newPassword = "".join(
            random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(12))

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
        # preferencesCon.setPreferences(pref)
        userCon.SetPreferences(pref)
        print(allPrefs)
        return redirect("/preferences/2")
    else:
        print("Hello")
    return render_template("preferences/preference1.html")


def getpoints(isBonus):
    Utier = {"Bronze": 1, "Silver": 1.1, "Gold": 1.3, "Diamond": 1.5}
    Uid = session["current_user"]["userId"]
    result = {"shopName": "MARINA BAY SANDS", "address": "1 BAYFRONT AVENUE MARINA BAY SANDS SINGAPORE 018971"}
    result2 = signedPlaceCon.GetShopInfo(result["address"])
    points = 10
    if isBonus:
        points = result2.getPoints()
    result3 = userCon.GetUserPointsInfo(Uid)
    result4 = userCon.tierPoints()
    uTierMultiplier = Utier.get(result3.getTier())
    uPoints = result3.getPoints()
    total_pts_earned = points * uTierMultiplier
    new_upoints = total_pts_earned + uPoints
    new_tierPoints = total_pts_earned + result4
    userCon.SetPoints(Uid, new_upoints, tierPoints)

    def UpdateTier():
        OldRank = result3.getTier()
        NewRank = " "
        if 400 <= new_upoints < 2000:
            NewRank = "Silver"
        elif 2000 <= new_upoints < 5000:
            NewRank = "Gold"
        elif new_upoints >= 5000:
            NewRank = "Diamond"

        userCon.SetTier(Uid, NewRank)
        return json.dumps({"OldRank": OldRank, "NewRank": NewRank, "OldPoints": uPoints, "NewPoints": new_upoints})

    UpdateTier()


@app.route("/qr-scanner")
def scanQR():
    return render_template("qrSites/qrScanner.html")


@app.route("/qrCode/claim-bonus/<string:id>")
def qrCodeClaimBonus(id):
    print("Test")


@app.route("qrCode/use-points/<string:id>")
def qrCodeUsePoints(id):
    Total_price = " "
    Uid = session["current_user"]["userId"]
    resultDic = {"shopName": "MARINA BAY SANDS", "address": "1 BAYFRONT AVENUE MARINA BAY SANDS SINGAPORE 018971"}
    result = userCon.GetUserPointsInfo(Uid)
    result2 = signedPlacesCon.GetShopInfo(resultDic["address"])
    discount = result2.getDiscount()
    uPoints = result.getPoints()
    new_uPoints = uPOints - Total_price*(1 - discount)
    userCon.SetPoints(Uid, new_upoints, tierPoints  )
    print("Test")


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
            signedPlace = SignedPlaces.SignedPlace(None, signedPlaceForm.address.data, signedPlaceForm.unitNo.data,
                                                   signedPlaceForm.shopName.data, signedPlaceForm.organization.data,
                                                   signedPlaceForm.points.data,
                                                   signedPlaceForm.checkpoint.data, signedPlaceForm.discount.data)
            response = signedPlaceCon.CreateEntry(signedPlace)

            if response.get("success"):
                return redirect("/admin/signedPlaces")
            else:
                return render_template("admin/createSignedPlace.html", form=signedPlaceForm, error=response["error"])

        return render_template("admin/createSignedPlace.html", form=signedPlaceForm, error="Invalid inputs entered")

    else:
        return render_template("admin/createSignedPlace.html", form=signedPlaceForm)


@app.route("/admin/signedPlaces/update/<string:id>", methods=['GET', 'POST'])
def adminUpdatePlace(id):
    validateAdmin()
    signedPlaceForm = SignedPlaceForm(request.form)
    if request.method == 'POST':
        if signedPlaceForm.validate():
            signedPlace = SignedPlaces.SignedPlace(id, signedPlaceForm.address.data, signedPlaceForm.unitNo.data,
                                                   signedPlaceForm.shopName.data, signedPlaceForm.organization.data,
                                                   signedPlaceForm.points.data,
                                                   signedPlaceForm.checkpoint.data, signedPlaceForm.discount.data)
            response = signedPlaceCon.UpdateEntry(signedPlace)
            print(response)

            if response.get("success"):
                return redirect("/admin/signedPlaces")
            else:
                return render_template("admin/editSignedPlace.html", form=signedPlaceForm, error=response["error"])

        return render_template("admin/editSignedPlace.html", form=signedPlaceForm, error="Invalid inputs entered")

    else:
        placeInfo = signedPlaceCon.GetShopInfo(id)
        if placeInfo is not None:
            signedPlaceForm.address.data = placeInfo.getAddress()
            signedPlaceForm.unitNo.data = placeInfo.getUnitNo()
            signedPlaceForm.shopName.data = placeInfo.getShopName()
            signedPlaceForm.organization.data = placeInfo.getOrganization()
            signedPlaceForm.points.data = placeInfo.getPoints()
            signedPlaceForm.checkpoint.data = placeInfo.getCheckpoint()
            signedPlaceForm.discount.data = placeInfo.getDiscount()

            return render_template("admin/createSignedPlace.html", form=signedPlaceForm)

        return redirect("/admin/signedPlaces")


@app.route("/admin/signedPlaces/delete/<string:id>")
def adminDeletePlace(id):
    validateAdmin()
    signedPlaceCon.DeleteEntry(id)
    return redirect("/admin/signedPlaces")


@app.route("/admin/signedPlaces/registerPurchase/<string:id>")
def adminRegisterPurchase(id):
    validatePlaceAdmin()

    placesBonusCodesCon.GenerateCode(id)


# AJAX CALLS
# Reward points -- Assign rewards point (Udhaya)
@app.route("/funcs/recommend-destination/itinerary", methods=['POST'])
def recommendDestination():
    averageSpeeds = {
        "walk": 4,
        "drive": 60,
        "pt": (80 * 0.45 + 50 * 0.45 + 4 * 0.1),
        "cycle": 18
    }

    if request.method == 'POST':
        def ShortlistByDistance(placesList, transportMode):
            finalList = []
            for place in placesList:
                # 1st stage shortlisting - Determined by roughly estimated average speed of transports
                # Find according to furthest distance possible (a and b distance)
                placeLatlng = place["LatLng"].split(",")
                aDist = geopy.distance.distance((startCoords.latitude, 0), (placeLatlng[0], 0))
                bDist = geopy.distance.distance((0, startCoords.longitutde), (0, placeLatlng[1]))
                furDist = aDist + bDist

                estTime = furDist // averageSpeeds[transportMode] + 0.75
                if estTime <= timeAllowance:
                    # 2nd stage shortlisting - Determined by the fastest route (actual timing needed)
                    currentTime = datetime.now()
                    routeResults = json.loads(
                        "https://developers.onemap.sg/privateapi/routingsvc/route?start=${},${}&end=${},${}" \
                        "&routeType=${}&token=${}&date=${}&time=${}" \
                        "&mode=TRANSIT".format(startCoords.latitude, startCoords.longitutde, placeLatlng[0],
                                               placeLatlng[1], transportMode, apiKey, currentTime.strftime("%Y-%m-%d"),
                                               currentTime.strftime("%H:%M:%S")))
                    estTime = 0.75
                    if transportMode == "pt":
                        estTime += routeResults["plan"]["itineraries"][0]["duration"] / 3600
                    else:
                        estTime += routeResults["route_summary"]["total_time"] / 3600

                    if estTime <= timeAllowance:
                        finalList.append(place)

            return finalList

        startCoords = request.form.get("startCoords")
        timeAllowance = request.form.get("timeAllowance")
        category = request.form.get("category")
        transportMode = request.form.get("transportMode")

        placesList = json.loads("https://developers.onemap.sg/privateapi/themesvc/retrieveTheme?queryName={}&token={}"
                                .format(category, apiKey))
        if placesList.get("SrchResults") is not None:
            # Shortlisted after calculating distance
            shortlistedPlaces = ShortlistByDistance(placesList["SrchResults"], transportMode)


# Reward points -- Assign rewards point (Udhaya)
@app.route("/funcs/reached-place/", methods=['GET', 'POST'])
def reachedPlace():
    # Placeholder returned data
    getpoints(False)


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
    resultDict = signedPlaceCon.ViewListOfPlaces(args.get("search"), args.get("sort"), args.get("order"),
                                                 args.get("limit"), args.get("offset"))
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


# Scheduled tasks to run every week - Web scrap, training of data models
@cron.cron_schedule(day_of_week="3", hour="3")
def scheduledJobs():
    # Encode label strings
    def encodeColumns(data):
        le = preprocessing.LabelEncoder()
        for column_name in data.columns:
            if data[column_name].dtype == object:
                data[column_name] = le.fit_transform(data[column_name])

        return data

    def trainGlobalUserPreferenceModel():
        print("I am training the model")
        path = userCon.ExportGlobalUserPreferenceCSV()  # Supply the new data in db to the csv files
        data = encodeColumns(pandas.read_csv(path))

        inp = data.drop(columns=['Preference'])
        oup = data['Preference']

        # Usage of K-Neighbours algorithm - Many overlaps
        model = KNeighborsClassifier()

        # Calculating average accuracy of current model
        model.fit(inp.values, oup)
        meanAccuracyScore = 0
        for i in range(1, 6):
            inp_train, inp_test, oup_train, oup_test = train_test_split(inp, oup, test_size=0.2)
            model.fit(inp_train, oup_train)
            predictions = model.predict(inp_test)
            print(accuracy_score(oup_test, predictions))
        meanAccuracyScore /= 5

        # Saving the model and accuracy results
        model.fit(inp, oup)
        joblib.dump(model, "csv/dbcsv/global-users-preferences.joblib")  # Saves the newly trained model as a file
        machineLearningReportCon.SetData(MachineLearningReport("GlobalUserPreferences", "Accuracy",
                                                               meanAccuracyScore))  # Save the accuracy score to db

    def webScrap():
        print("I am web scrapping")

    trainGlobalUserPreferenceModel()
    webScrap()


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
