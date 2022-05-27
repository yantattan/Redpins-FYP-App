from urllib.error import HTTPError
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from apscheduler.scheduler import Scheduler
from io import BytesIO
import uuid
import warnings

# Required libraries
from datetime import datetime, timedelta, date
import calendar
from functools import reduce
import geocoder, requests, random, string, json, geopy.distance, numpy
import asyncio, aiohttp
# Machine learning, csv libraries, vectors
import pandas, joblib
from sklearn import preprocessing
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
# Email libraries
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# Database modules
import DbContext
from helpers.permissionValidator import *
from Model import *
from controllers import MachineLearningReports, SignedPlaces, Users, TrackedPlaces, PlacesBonusCodes, Reviews, Itineraries
# Qrcode libraries
from flask_cors import CORS
import qrcode

app = Flask(__name__)
cron = Scheduler(daemon=True)
cron.start()
CORS(app)
app.secret_key = "redp1n5Buffer"
apiKey = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOjg1NDQsInVzZXJfaWQiOjg1NDQsImVtYWlsIjoieWFudGF0dGFuNzIxQGdtYWlsLmNvbSIsImZvcmV2ZXIiOmZhbHNlLCJpc3MiOiJodHRwOlwvXC9vbTIuZGZlLm9uZW1hcC5zZ1wvYXBpXC92MlwvdXNlclwvc2Vzc2lvbiIsImlhdCI6MTY1MzU1ODQ2MCwiZXhwIjoxNjUzOTkwNDYwLCJuYmYiOjE2NTM1NTg0NjAsImp0aSI6IjU0NzA2ZjE4MmVlZWRmZWI0M2NjOTg1MDhhZTkwYzQ1In0.QEiPcqPq7v7eu2zVYJ4tS2XM4pNv3zujJo0LNS8jDN8"

# Init all controllers
userCon = Users.UserCon()
trackedPlacesCon = TrackedPlaces.TrackedPlacesCon()
signedPlaceCon = SignedPlaces.SignedPlacesCon()
machineLearningReportCon = MachineLearningReports.MachineLearningReportCon()
placesBonusCodesCon = PlacesBonusCodes.PlacesBonusCodesCon()
reviewsCon = Reviews.ReviewCon()
itinerariesCon = Itineraries.ItinerariesCon()

# preferencesCon = Preferences.PreferencesCon()
# userRewardsCon = UserPoints.UserPointsCon()

# Init label encoders
globalPrefLE = trackedInfoLE = preprocessing.LabelEncoder()

categoriesInfo = {
    "Eateries": {"filename":"restaurants_info.csv", "category":"Eateries", "colName": "Category", "activityTime": 45, 
                "preferences": ["Italian", "Chinese", "Japanese", "Thai", "French", "Spanish", "American", "Mexican", "Indian", "Turkish", "Korean", "Vietnamese", "Hong Kong", 
                                "German", "British", "Taiwanese", "Singaporean", "Indonesian", "Malaysian", "Australian", "Swedish"]},

    "Attractions": {"filename":"attractions_info.csv", "category":"Attractions", "colName": "Category",
                "preferences": ["Museums", "Fun and Games", "Sights and Landmarks", "Nature and Parks"]}
}

tierRange = {
    "Silver": [400, 2000],
    "Gold": [2000, 5000]
}

allWebscrapData = {}

# Functions to perform before showing the page
@app.route("/")
def homePage():
    if session.get("current_user") is None:
        return redirect("/login")

    return render_template("itinerary/selectPlan.html")


# Accounts pages
@app.route("/login", methods=['GET', 'POST'])
def login():
    # To render the page (pathing starts from templates folder after). After the filename, variables defined behind are
    # data that the site needs to use
    login_form = LoginForm(request.form)
    session["session_id"] = str(uuid.uuid4())

    if request.method == 'POST' and login_form.validate():
        userInfo = userCon.Login(login_form)
        if userInfo:
            if userInfo.get("error") is None:
                session["current_user"] = userInfo
                if userInfo["setupComplete"]:
                    return redirect("/")
                
                return redirect("/preferences/1")

        return render_template("accounts/login.html", form=login_form, error="Invalid username or password")

    return render_template("accounts/login.html", form=login_form)

@app.route("/register", methods=['GET', 'POST'])
def register():
    register_form = RegisterForm(request.form)

    if request.method == 'POST':
        if register_form.validate():
            userModel = User(register_form.username.data, register_form.email.data, "User",
                             register_form.dateOfBirth.data,
                             register_form.contact.data, register_form.password.data, 0, 0, "Bronze")
            registerResponse = userCon.Register(userModel)
            print(registerResponse)
            if registerResponse.get("error"):
                return render_template("accounts/register.html", form=register_form, error=registerResponse["error"])
            else:
                return redirect("/login")

        return render_template("accounts/register.html", form=register_form, error="Invalid fields submitted")

    return render_template("accounts/register.html", form=register_form)

@app.route("/logout")
def logout():
    session.pop("current_user", None)
    return redirect("/login")

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

@app.route("/yourProfile")
def profileInfo():
    userId = session["current_user"]["userId"]
    pointsInfo = userCon.GetUserPointsInfo(userId)
    tier = pointsInfo.getTier()
    pointsLeft = None
    if tier == "Bronze":
        pointsLeft = tierRange["Silver"][0] - pointsInfo.getPoints()
    elif tier == "Silver":
        pointsLeft = tierRange["Gold"][0] - pointsInfo.getPoints()
    elif tier == "Gold":
        pointsLeft = tierRange["Gold"][1] - pointsInfo.getPoints()

    return render_template("accounts/profile.html", pointsInfo=pointsInfo, pointsLeft=pointsLeft)

#Onboarding page
@app.route("/onboarding")
def onBoardingPage():
    return render_template("onboarding.html")
    

@app.route("/loading")
def loading():
    return render_template("includes/_loading.html")

# Itinerary planning pages
@app.route("/itinerary/planners")
def showItineraries():
    invalidRedirect = validateLoggedIn()
    if invalidRedirect is not None:
        return redirect(invalidRedirect)

    userId = session["current_user"]["userId"]

    ongoing = itinerariesCon.GetOngoingItinerary(userId)
    if ongoing != None:
        if ongoing.getType() != "Planner":
            ongoing = None
    saved = itinerariesCon.GetSavedItinerary(userId)
    planning = itinerariesCon.GetUnconfimredItinerary(userId, "Planner") or []
    completed = itinerariesCon.GetCompletedItineraries(userId) or []

    return render_template("/itinerary/listItineraries.html", ongoing=ongoing, planning=planning, saved=saved, completed=completed)

@app.route("/itinerary/planning/planner", methods=['GET', 'POST'])
def plannerItinerary():
    invalidRedirect = validateLoggedIn()
    if invalidRedirect is not None:
        return redirect(invalidRedirect)

    itineraries = itinerariesCon.GetUnconfimredItinerary(session["current_user"]["userId"], "Planner")

    if request.method == 'POST':
        itinerary = itinerariesCon.GetUnconfimredItinerary(session["current_user"]["userId"], "Planner")
        for iti in itinerary:
            iti.setConfirmed(True)
            iti.setStatus("Saved")
            itinerariesCon.SetItinerary(iti)
        return redirect("/itinerary/planners")

    recentInfo = []
    recentSearches = trackedPlacesCon.GetTopSearchedInfo(session["current_user"]["userId"]) or []
    for search in recentSearches:
        webScrapData = allWebscrapData["Eateries"]
        entry = webScrapData.loc[webScrapData["Address"] == search.getAddress()]
        recentInfo.append({"Image_url": entry["Image_url"], "Rating": entry["Rating"]})

    return render_template("/itinerary/plannerItinerary.html", itineraries=itineraries, recentSearches=recentSearches, recentInfo=recentInfo,
                            apiKey=apiKey, catInfo=categoriesInfo)

@app.route("/itinerary/planning/explorer", methods=['GET', 'POST'])
def explorerItinerary():
    invalidRedirect = validateLoggedIn()
    if invalidRedirect is not None:
        return redirect(invalidRedirect)

    itinerary = itinerariesCon.GetUnconfimredItinerary(session["current_user"]["userId"], "Explorer")

    if request.method == 'POST':
        itineraryId = request.form.get("id")
        itinerary = itinerariesCon.GetItineraryById(itineraryId)
        itinerary.setConfirmed(True)
        itinerariesCon.SetItinerary(itinerary)
        return redirect("/itinerary/review/explorer")
    
    if itinerary is None:
        reviewItinerary = itinerariesCon.GetReviewingItinerary(session["current_user"]["userId"], "Explorer")
        if reviewItinerary is not None:
            return redirect("/itinerary/review/explorer")
        ongoingItinerary = itinerariesCon.GetOngoingItinerary(session["current_user"]["userId"])
        if ongoingItinerary is not None:
            return redirect("/itinerary/showTrip")
    
    recentInfo = []
    recentSearches = trackedPlacesCon.GetTopSearchedInfo(session["current_user"]["userId"])
    for search in recentSearches:
        webScrapData = allWebscrapData[search.getCategory()]
        entry = webScrapData.loc[webScrapData["Address"] == search.getAddress()]
        recentInfo.append({"Image_url": entry["Image_url"], "Rating": entry["Rating"]})

    return render_template("/itinerary/editExplorerItinerary.html", itinerary=itinerary, recentSearches=recentSearches, recentInfo=recentInfo, 
                            apiKey=apiKey, catInfo=categoriesInfo)

@app.route("/itinerary/unconfirm/explorer")
def unconfirmExplorer():
    invalidRedirect = validateLoggedIn()
    if invalidRedirect is not None:
        return redirect(invalidRedirect)

    itinerary = itinerariesCon.GetReviewingItinerary(session["current_user"]["userId"], "Explorer")
    itinerary.setConfirmed(False)
    itinerariesCon.SetItinerary(itinerary)
    return redirect("/itinerary/planning/explorer")

@app.route("/itinerary/review/<string:typ>", methods=['GET', 'POST'])
def confirmItinerary(typ):
    invalidRedirect = validateLoggedIn()
    if invalidRedirect is not None:
        return redirect(invalidRedirect)

    userId = session["current_user"]["userId"]
    itinerary = itinerariesCon.GetReviewingItinerary(userId, typ.capitalize())
    
    if request.method == 'POST':
        itinerary.setStatus("Ongoing")
        res = itinerariesCon.SetItinerary(itinerary)
        if res["success"]:
            return redirect("/itinerary/showTrip")
        else:
            return render_template("/itinerary/reviewItinerary.html", error="An error occurred. Try again")
    else:
        if itinerary is None:
            return render_template("/itinerary/reviewItinerary.html", error="There is no itinerary under review")
        if itinerary.getUserId() != userId:
            return render_template("/itinerary/reviewItinerary.html", error="You are not permitted to view this itinerary")

        return render_template("/itinerary/reviewItinerary.html", itinerary=itinerary, type=itinerary.getType(), apiKey=apiKey)

@app.route("/itinerary/showTrip", methods=['GET', 'POST'])
def showTrip():
    invalidRedirect = validateLoggedIn()
    if invalidRedirect is not None:
        return redirect(invalidRedirect)

    currItinerary = itinerariesCon.GetOngoingItinerary(session["current_user"]["userId"])

    if request.method == 'POST':
        currItinerary.setStatus("Completed")
        itinerariesCon.SetItinerary(currItinerary)
        return redirect("/itinerary/postFeedback")

    if currItinerary is None:
        return redirect("/")
    if currItinerary.getUserId() != session["current_user"]["userId"]:
        return render_template("/itinerary/reviewItinerary.html", error="You are not permitted to view this itinerary")


    return render_template("/itinerary/showTrip.html", itinerary=currItinerary, apiKey=apiKey)

@app.route("/itinerary/trip/<string:id>")
def tripDetails(id):
    itinerary = itinerariesCon.GetItineraryById(id)
    if itinerary is None:
        return redirect("/itinerary/planners")

    return render_template("/itinerary/showTrip.html", readonly=True, itinerary=itinerary, apiKey=apiKey)
    

@app.route("/itinerary/postFeedback", methods=['GET', 'POST'])
def postFeedback():
    invalidRedirect = validateLoggedIn()
    if invalidRedirect is not None:
        return redirect(invalidRedirect)

    currItinerary = itinerariesCon.GetLatestCompletedItinerary(session["current_user"]["userId"])

    if request.method == 'POST':
        return redirect("/")

    return render_template("/itinerary/postFeedback.html", itinerary=currItinerary)


# Preferences pages
@app.route("/preferences/1", methods=['GET', 'POST'])
def pref1():
    invalidRedirect = validateSession()
    if invalidRedirect is not None:
        print(invalidRedirect)
        return redirect(invalidRedirect)

    category = "Eateries"
    if request.method == 'POST':
        allPrefs = request.form.getlist("preferences[]")
        pref = Preferences(session["current_user"]["userId"], allPrefs, category)
        userCon.SetPreferences(pref)
        newUserInfo = userCon.SetSetupComplete(session["current_user"]["userId"])
        session["current_user"] = newUserInfo
        print(allPrefs)
        return redirect("/preferences/2")
    
    webscrapData = pandas.read_csv("csv/webcsv/"+categoriesInfo[category]["filename"], encoding = "ISO-8859-1")
    allPrefs = pandas.unique(webscrapData[categoriesInfo[category]["colName"]].str.split(",", expand=True).stack())

    prefs = userCon.GetPreferences(session["current_user"]["userId"], category).getPreferences()
    print(prefs)

    return render_template("preferences/preference1.html", prefs=prefs, allPrefs=allPrefs)

@app.route("/preferences/2", methods=['GET', 'POST'])
def pref2():
    invalidRedirect = validateSession()
    if invalidRedirect is not None:
        print(invalidRedirect)
        return redirect(invalidRedirect)

    category = "Attractions"
    if request.method == 'POST':
        allPrefs = request.form.getlist("preferences[]")
        pref = Preferences(session["current_user"]["userId"], allPrefs, category)
        userCon.SetPreferences(pref)
        newUserInfo = userCon.SetSetupComplete(session["current_user"]["userId"])
        session["current_user"] = newUserInfo
        print(allPrefs)
        return redirect("/")
    
    webscrapData = pandas.read_csv("csv/webcsv/"+categoriesInfo[category]["filename"], encoding = "ISO-8859-1")
    allPrefs = pandas.unique(webscrapData[categoriesInfo[category]["colName"]].str.split(",", expand=True).stack())

    prefs = userCon.GetPreferences(session["current_user"]["userId"], category).getPreferences()

    return render_template("preferences/preference2.html", prefs=prefs, allPrefs=allPrefs)


# Reviews pages
@app.route("/yourReview/<string:address>", methods=['GET', 'POST'])
def editReview(address):
    review_form = ReviewForm(request.form)
    return render_template("editReview.html", form=review_form)


# Qr code and points pages
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
    userCon.SetPoints(Uid, new_upoints, new_tierPoints)

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

@app.route("/qrCode/onlineQr")
def onlineQR():
    return render_template("qrSites/onlineQrCodes.html")

@app.route("/qrCode/claim-bonus/<string:id>")
def qrCodeClaimBonus(id):
    shop = signedPlaceCon.GetShopById(id)
    if shop is None:
        return redirect("/qrCode/invalidCode")

    return render_template("/rewardPoints/earnedPoints.html", bonus=shop.getPoints(), id=id)

@app.route("/qrCode/use-points/<string:id>")
def qrCodeUsePoints(id):
    Total_price = 26.90
    Uid = session["current_user"]["userId"]
    place = signedPlaceCon.GetShopById(id)
    result = userCon.GetUserById(Uid)

    discount = place.getDiscount()
    uPoints = result.getPoints()
    tierPoints = result.getTierPoints()
    new_uPoints = uPoints - Total_price*(1 - discount)
    userCon.SetPoints(Uid, new_uPoints, tierPoints)
    return render_template("rewardPoints/usePoints.html")

@app.route("/qrCode/invalidCode")
def qrCodeInvalid():
    return render_template("qrSites/invalid.html")


# ADMIN SITES
@app.route("/admin/signedPlaces")
def viewSignedPlaces():
    invalidRedirect = validateAdmin()
    if invalidRedirect is not None:
        return redirect(invalidRedirect)
    return render_template("admin/viewSignedPlaces.html")

@app.route("/admin/signedPlaces/create", methods=['GET', 'POST'])
def adminCreatePlace():
    invalidRedirect = validateAdmin()
    if invalidRedirect is not None:
        return redirect(invalidRedirect)

    signedPlaceForm = SignedPlaceForm(request.form)
    if request.method == 'POST':
        if signedPlaceForm.validate():
            signedPlace = SignedPlaces.SignedPlace(None, signedPlaceForm.address.data, signedPlaceForm.unitNo.data,
                        signedPlaceForm.shopName.data, signedPlaceForm.organization.data, signedPlaceForm.category.data,
                        {"Cuisine": ["Chinese"]}, signedPlaceForm.points.data, signedPlaceForm.checkpoint.data, signedPlaceForm.discount.data)
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
    invalidRedirect = validateAdmin()
    if invalidRedirect is not None:
        return redirect(invalidRedirect)

    signedPlaceForm = SignedPlaceForm(request.form)
    if request.method == 'POST':
        if signedPlaceForm.validate():
            signedPlace = SignedPlaces.SignedPlace(id, signedPlaceForm.address.data, signedPlaceForm.unitNo.data,
                            signedPlaceForm.shopName.data, signedPlaceForm.organization.data, signedPlaceForm.category.data,
                            {"Cuisine": ["Chinese"]}, signedPlaceForm.points.data, signedPlaceForm.checkpoint.data, signedPlaceForm.discount.data)
            response = signedPlaceCon.UpdateEntry(signedPlace)
            print(response)

            if response.get("success"):
                return redirect("/admin/signedPlaces")
            else:
                return render_template("admin/editSignedPlace.html", form=signedPlaceForm, error=response["error"])

        return render_template("admin/editSignedPlace.html", form=signedPlaceForm, error="Invalid inputs entered")

    else:
        placeInfo = signedPlaceCon.GetShopById(id)
        if placeInfo is not None:
            signedPlaceForm.address.data = placeInfo.getAddress()
            signedPlaceForm.unitNo.data = placeInfo.getUnitNo()
            signedPlaceForm.shopName.data = placeInfo.getShopName()
            signedPlaceForm.organization.data = placeInfo.getOrganization()
            signedPlaceForm.category.data = placeInfo.getCategory()
            signedPlaceForm.points.data = placeInfo.getPoints()
            signedPlaceForm.checkpoint.data = placeInfo.getCheckpoint()
            signedPlaceForm.discount.data = placeInfo.getDiscount()

            return render_template("admin/createSignedPlace.html", form=signedPlaceForm)

        return redirect("/admin/signedPlaces")

@app.route("/admin/signedPlaces/delete/<string:id>")
def adminDeletePlace(id):
    invalidRedirect = validateAdmin()
    if invalidRedirect is not None:
        return redirect(invalidRedirect)
        
    signedPlaceCon.DeleteEntry(id)
    return redirect("/admin/signedPlaces")

@app.route("/admin/signedPlaces/registerPurchase/<string:id>")
def adminRegisterPurchase(id):
    invalidRedirect = validateAdmin()
    if invalidRedirect is not None:
        return redirect(invalidRedirect)

    placesBonusCodesCon.GenerateCode(id)


# AJAX CALLS
averageSpeeds = {
    "walk": 4,
    "drive": 60,
    "pt": (80 * 0.45 + 50 * 0.45 + 4 * 0.1),
    "cycle": 18
}

def calculateAndReturnList(userId, category, webScrapData, shortlistedPlaces, displaySize, activityTime, skipped, placesAdded, sectionIndex):
    # CALCULATIONS BEFORE CHECKING AGAINST DIFFERENT PLACES
    # From here, every different checks contributes to different weightage to the final chance.
    globalPreference = joblib.load("csv/dbcsv/global-users-preferences.joblib")

    # Check preference against people of your age, tier, points, giving bonus points for them
    userInfo = userCon.GetUserById(userId)
    if type(userInfo) is not dict and userInfo is not None:
        proba = globalPreference.predict_proba([globalPrefLE.fit_transform([userInfo.getDateOfBirth()[:4], userInfo.getPoints(), 
                                                userInfo.getTier(), category]) ])
        top5Pref = numpy.argsort(proba, axis=1)[:,-5:]
        globalPrefAccuracy = 0
        try:
            globalPrefAccuracy = machineLearningReportCon.GetData("GlobalUserPreferences")["Data"]["Accuracy"]
        except TypeError:
            globalPrefAccuracy = 0

        # Get most recommended cuisines based on your tracked whereabouts, histories e.t.c
        yourTop5Frequent = trackedPlacesCon.GetTopAccessedInfo(userId) or {}
        yourTop5Search = trackedPlacesCon.GetDetailedTopAccessedInfo(userId, "Searched")

        trackedInfoPreference = joblib.load("csv/dbcsv/global-users-preferences.joblib")
        # yourTop5Recent = trackedPlacesCon.GetRecentlyAccessedInfo(userId) or []

        actionPoints = {"Visited": -2, "Searched":1, "Planned": -1}
        freqtrackedPlacesCuisine = {} # Cuisines weighted - MAX score 5
        futuretrackedPlacesPoints = {} # - MAX score 3
        rerecommend = [] # Places to rerecommend again

        for action in yourTop5Frequent:
            for place in yourTop5Frequent[action]:
                # Determine if the place is good to re-recommend back to user (Kept searching but yet to plan/go)
                dataRow = webScrapData.loc[webScrapData["Address"] == place.getAddress()]   
                cuisines = dataRow[categoriesInfo[category]["colName"]].split(",")
                for cuisine in cuisines:
                    try:
                        freqtrackedPlacesCuisine[cuisine] += 1
                    except KeyError:
                        freqtrackedPlacesCuisine[cuisine] = 1
        
        # Check for rerecommend places on top 5 searches 
        for place in yourTop5Search:
            rerecommendPoints = 0 # If >=0, can rerecommend
            dataRow = webScrapData.loc[webScrapData["Address"] == place["Address"]]

            if len(dataRow.values) > 0:
                for action in place["Actions"]:
                    addPoints = actionPoints[action] * place["Actions"]["Searched"]["Frequency"]
                    rerecommendPoints += addPoints

                if rerecommendPoints >= 0:
                    rerecommend.append(dataRow["Name"].values[0])

        # Score preferences based on regression of his preferences 
        for action in actionPoints:
            yourFuturePref = trackedInfoPreference.predict([trackedInfoLE.fit_transform([userId, category, action, str(datetime.now()) ])])[0]
            try:
                futuretrackedPlacesPoints[yourFuturePref] += 1
            except KeyError:
                futuretrackedPlacesPoints[yourFuturePref] = 1

        # START OF CHECK AGAINST LISTS
        scoredPlaces = []
        for place in shortlistedPlaces:
            netChance = 0   # -- Chance calculation for every place shortlisted
            if not place.Name in list(webScrapData["Name"]):
                # Low chance to try and exclude restaurants outside of our dataset
                netChance = 0.1
            else:
                placeDetails = webScrapData.loc[webScrapData["Name"] == place.Name]
                placesCat = placeDetails[categoriesInfo[category]["colName"]].values[0].split(",")

                # #1 - Check against global and your preference
                if sectionIndex in [1, 3]:
                    cuisinesMatch = 0
                    yourPrefs = userCon.GetPreferences(userId, category)

                    for pref in top5Pref:
                        if pref in placesCat:
                            cuisinesMatch += 1 * globalPrefAccuracy
                    for pref in yourPrefs.getPreferences():
                        if pref in placesCat:
                            cuisinesMatch += 2

                    cuisinesMatch /= ( (len(yourPrefs.getPreferences())*2) + 5 )
                    netChance += cuisinesMatch * 0.35

                # #2 - Check reviews
                if sectionIndex in [1, 2]:
                    reviews = reviewsCon.GetReviews(place.Address)
                    if reviews is not None:
                        calRating = placeDetails["Rating"].values[0] * 0.25 + reviews * 0.75
                        calRating /= 5
                        # calRatingXVal = calRating * 0.5
                        # netChance += ((2 * calRatingXVal * (1 - calRatingXVal) + 0.5) * calRating) * 0.35
                        netChance += calRating * 0.25
                    else:
                        calRating = placeDetails["Rating"].values[0] / 5
                        netChance += calRating * 0.25

                # #3 - Check against the cuisines & places recommended from your tracked history
                if sectionIndex in [1, 4]:
                    trackedMatch = 0
                    if freqtrackedPlacesCuisine != {}:
                        if place.Name in rerecommend:
                            trackedMatch += 5

                        for cuisine in placesCat:
                            trackedMatch += freqtrackedPlacesCuisine[cuisine]
                            trackedMatch += futuretrackedPlacesPoints[cuisine]

                    trackedMatch /= 13
                    
                    netChance += trackedMatch * 0.25

                # #4 - Check if the places are our partners
                if sectionIndex in [1, 3]:
                    partnered = signedPlaceCon.CheckPlace(place.Name)
                    if partnered:
                        netChance += 0.15
                
                # #5 - Check if place already selected
                if place.Address in placesAdded:
                    netChance /= 2

            placeDict = dict(place._asdict())
            placeDict["RecommendationScore"] = netChance
            placeDict["ActivityDuration"] = activityTime
            scoredPlaces.append(placeDict)

        pageNum = request.args.get("page") or 1
        pageNum = int(pageNum)
        
        takenSet = []
        orderedPlaces = sorted(scoredPlaces, key=lambda x:x["RecommendationScore"], reverse=True)

        totalSkip = 0
        try:
            totalSkip = reduce(lambda x,y: x+y, skipped[:pageNum-1])
        except TypeError:
            pass
        
        if displaySize == 1:
            takenSet = [orderedPlaces[0]]
        else:
            try:
                takenSet = orderedPlaces[((pageNum-1)*displaySize)+totalSkip: (pageNum*displaySize) + totalSkip]
            except IndexError:
                takenSet = orderedPlaces[((pageNum-1)*displaySize)+totalSkip: ]

        return takenSet, orderedPlaces

def recommenderAlgorithm(userId, startDatetime, timeAllowance, displaySize, latitude, longitude, category, transportMode, skipped, pageNum, placesAdded, abovePlace=None, belowPlace=None, sectionIndex=1):
    recommendList = []

    def firstShortlist(placesList, startDatetime, transportMode, activityTime, abovePlace, belowPlace):
        pList = []
        for place in placesList.itertuples():
            # 1st stage shortlisting - Determined by roughly estimated average speed of transports
            # Find according to furthest distance possible (a and b distance)
            placeLatlng = place.Latlng.split(",")
            if len(placeLatlng) < 2:
                continue
            placeLatlng = list(map(lambda x: round(float(x), 7), placeLatlng))
            aDist = geopy.distance.distance((latitude, 0), (placeLatlng[0], 0)).km
            bDist = geopy.distance.distance((0, longitude), (0, placeLatlng[1])).km
            furDist = aDist + bDist

            estTime = (furDist // averageSpeeds[transportMode] + activityTime / 60) * 60
            if estTime <= timeAllowance:
                canAdd = True
                # Check if place is the same as before
                if abovePlace is not None:
                    if abovePlace == place.Address:
                        canAdd = False

                if belowPlace is not None:
                    if belowPlace == place.Address:
                        canAdd = False
                
                # Check operating time
                operatingHrs = json.loads(place.Operating_hours)
                dayOfWk = calendar.day_name[startDatetime.weekday()]
                operatingRanges = operatingHrs[dayOfWk]

                rangeValid = False
                for rangeStr in operatingRanges:
                    rangeArr = rangeStr.split("-")

                    if (startDatetime.replace(hour=int(rangeArr[0][:2]), minute=int(rangeArr[0][2:])) <= startDatetime < 
                        startDatetime.replace(hour=int(rangeArr[1][:2]), minute=int(rangeArr[1][2:])) - timedelta(hours=1)):
                        rangeValid = True
                        break

                if not rangeValid:
                    canAdd = False

                if canAdd:
                    pList.append(place)
            
        return pList    
    print(timeAllowance)

     # Shortlisted after calculating distance
    webScrapData = pandas.read_csv("csv/webcsv/"+categoriesInfo[category]["filename"], encoding = "ISO-8859-1")
    activityTime = 90
    if category == "Eateries":
        activityTime = categoriesInfo[category]["activityTime"]
    shortlistedPlaces = firstShortlist(webScrapData, startDatetime, transportMode, activityTime, abovePlace, belowPlace)

    if len(shortlistedPlaces) > 0:
        returnList = calculateAndReturnList(userId, category, webScrapData, shortlistedPlaces, displaySize, activityTime, skipped, placesAdded, sectionIndex)

        async def CheckRealDuration(placesList, orderedPlaces, transportMode):
            # Final shortlisting - Ensure estimated shortlisted places can actually be reached in time
            async with aiohttp.ClientSession() as clientSession:
                currentTime = datetime.now()
                try:
                    skipped[pageNum-1] = 0
                except IndexError:
                    skipped.append(0)
                async def getFinalDataset(subList, startIndex):
                    routeTasks = []
                    for place in subList:
                        placeLatlng = place["Latlng"].split(",")
                        if len(placeLatlng) < 2:
                            continue
                        placeLatlng = list(map(lambda x: round(float(x), 7), placeLatlng))

                        routeApi = "https://developers.onemap.sg/privateapi/routingsvc/route?start={},{}&end={},{}" \
                                    "&routeType={}&token={}&date={}&time={}" \
                                    "&mode=TRANSIT&numItineraries=1".format(latitude, longitude, placeLatlng[0], placeLatlng[1], transportMode, apiKey,
                                    currentTime.strftime("%Y-%m-%d"), currentTime.strftime("%H:%M:%S")) 
                        
                        routeTasks.append(clientSession.get(routeApi, ssl=False))
                    
                    responses = await asyncio.gather(*routeTasks)

                    skippedCount = 0
                    for i in range(len(responses)):
                        routeResultsRaw = responses[i]
                        estTime = activityTime
                        routeResults = None
                        try:
                            routeResults = await routeResultsRaw.json()
                        except Exception:
                            continue

                        if routeResults is not None:
                            if routeResults.get("error") is None:
                                if transportMode == "pt":
                                    estTime += routeResults["plan"]["itineraries"][0]["duration"] / 60
                                else:
                                    estTime += routeResults["route_summary"]["total_time"] / 60

                                if estTime <= timeAllowance:
                                    subList[i]["TravelDuration"] = estTime - activityTime
                                    subList[i]["Duration"] = estTime
                                    subList[i]["Category"] = category
                                    recommendList.append(subList[i])
                                else:
                                    skippedCount += 1

                    skipped[pageNum-1] += skippedCount
                    # Recursively call the function till a definite 
                    if skippedCount > 0:
                        recurIndex = startIndex + len(placesList) 
                        await getFinalDataset(orderedPlaces[recurIndex: recurIndex + skippedCount], recurIndex)
                
                await getFinalDataset(placesList, (pageNum-1)*displaySize)

        print("Final Check...")
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())           
        asyncio.run(CheckRealDuration(returnList[0], returnList[1], transportMode))

    return {"list": recommendList, "skipped": skipped}

def recommenderAlgorithmEndPoint(userId, startDatetime, timeAllowance, displaySize, latitude, longitude, endLatitude, endLongitude, category, transportMode, skipped, pageNum, placesAdded, abovePlace=None, belowPlace=None, sectionIndex=1):
    recommendList = []

    def firstShortlist(placesList, startDatetime, transportMode, activityTime, abovePlace, belowPlace):
        pList = []
        for place in placesList.itertuples():
            # 1st stage shortlisting - Determined by roughly estimated average speed of transports
            # Find according to furthest distance possible (a and b distance)
            placeLatlng = place.Latlng.split(",")
            if len(placeLatlng) < 2:
                continue
            placeLatlng = list(map(lambda x: round(float(x), 7), placeLatlng))
            aDist = geopy.distance.distance((latitude, 0), (placeLatlng[0], 0)).km
            bDist = geopy.distance.distance((0, longitude), (0, placeLatlng[1])).km

            a2Dist = geopy.distance.distance((placeLatlng[0], 0), (round(endLatitude, 7), 0)).km
            b2Dist = geopy.distance.distance((0, placeLatlng[1]), (0, round(endLongitude, 7))).km
            furDist = aDist + bDist + a2Dist + b2Dist

            estTime = (furDist // averageSpeeds[transportMode] + activityTime / 60) * 60
            if estTime <= timeAllowance:
                canAdd = True
                # Check if place is the same as before
                if abovePlace is not None:
                    if abovePlace == place.Address:
                        canAdd = False
                
                if belowPlace is not None:
                    if belowPlace == place.Address:
                        canAdd = False

                # Check operating time
                operatingHrs = json.loads(place.Operating_hours)
                dayOfWk = calendar.day_name[startDatetime.weekday()]
                operatingRanges = operatingHrs[dayOfWk]

                rangeValid = False
                for rangeStr in operatingRanges:
                    rangeArr = rangeStr.split("-")

                    if (startDatetime.replace(hour=int(rangeArr[0][:2]), minute=int(rangeArr[0][2:])) <= startDatetime < 
                        startDatetime.replace(hour=int(rangeArr[1][:2]), minute=int(rangeArr[1][2:])) - timedelta(hours=1)):
                        rangeValid = True
                        break

                if not rangeValid:
                    canAdd = False

                if canAdd:
                    pList.append(place)
            
        return pList    

     # Shortlisted after calculating distance
    webScrapData = pandas.read_csv("csv/webcsv/"+categoriesInfo[category]["filename"], encoding = "ISO-8859-1")
    activityTime = 90
    if category == "Eateries":
        activityTime = categoriesInfo[category]["activityTime"]
    shortlistedPlaces = firstShortlist(webScrapData, startDatetime, transportMode, activityTime, abovePlace, belowPlace)

    if len(shortlistedPlaces) > 0:
        returnList = calculateAndReturnList(userId, category, webScrapData, shortlistedPlaces, displaySize, activityTime, skipped, placesAdded, sectionIndex)

        async def CheckRealDuration(placesList, orderedPlaces, transportMode):
            # Final shortlisting - Ensure estimated shortlisted places can actually be reached in time
            async with aiohttp.ClientSession() as clientSession:
                currentTime = datetime.now()
                try:
                    skipped[pageNum-1] = 0
                except IndexError:
                    skipped.append(0)
                async def getFinalDataset(subList, startIndex):
                    routeTasks = []
                    for place in subList:
                        placeLatlng = place["Latlng"].split(",")
                        if len(placeLatlng) < 2:
                            continue
                        placeLatlng = list(map(lambda x: round(float(x), 7), placeLatlng))

                        routeApi = "https://developers.onemap.sg/privateapi/routingsvc/route?start={},{}&end={},{}" \
                                    "&routeType={}&token={}&date={}&time={}" \
                                    "&mode=TRANSIT&numItineraries=1".format(latitude, longitude, placeLatlng[0], placeLatlng[1], transportMode, apiKey,
                                    currentTime.strftime("%Y-%m-%d"), currentTime.strftime("%H:%M:%S")) 
                        
                        routeTasks.append(clientSession.get(routeApi, ssl=False))
                    
                    responses = await asyncio.gather(*routeTasks)

                    skippedCount = 0
                    for i in range(len(responses)):
                        routeResultsRaw = responses[i]
                        estTime = activityTime
                        try:
                            routeResults = await routeResultsRaw.json()
                        except Exception:
                            continue

                        if routeResults is not None:
                            routeTasks = []

                            endTime = ""
                            if transportMode == "pt":
                                endTime = datetime.fromtimestamp(routeResults["plan"]["itineraries"][0]["endTime"] / 1000)
                            else:
                                endTime = routeResults["route_summary"]["total_time"] / 60
                            routeApi = "https://developers.onemap.sg/privateapi/routingsvc/route?start={},{}&end={},{}" \
                                        "&routeType={}&token={}&date={}&time={}" \
                                        "&mode=TRANSIT&numItineraries=1".format(placeLatlng[0], placeLatlng[1], endLatitude, endLongitude, transportMode, apiKey,
                                        endTime.strftime("%Y-%m-%d"), endTime.strftime("%H:%M:%S")) 
                            
                            routeTasks.append(clientSession.get(routeApi, ssl=False))
            
                            response = await asyncio.gather(*routeTasks)
                            endRouteResultsRaw = response[0]
                            try:
                                endRouteResults = await endRouteResultsRaw.json()
                            except Exception:
                                continue

                            if transportMode == "pt":
                                estTime += routeResults["plan"]["itineraries"][0]["duration"] / 60
                                estEndTime = endRouteResults["plan"]["itineraries"][0]["duration"] / 60
                            else:
                                estTime += routeResults["route_summary"]["total_time"] / 60
                                estEndTime = endRouteResults["route_summary"]["total_time"] / 60

                            if estTime + estEndTime <= timeAllowance:
                                subList[i]["TravelDuration"] = estTime - activityTime
                                subList[i]["Duration"] = estTime
                                subList[i]["Category"] = category
                                subList[i]["EndDuration"] = estEndTime
                                recommendList.append(subList[i])
                            else:
                                skippedCount += 1

                    skipped[pageNum-1] += skippedCount
                    # Recursively call the function till a definite 
                    if skippedCount > 0:
                        recurIndex = startIndex + len(placesList) 
                        await getFinalDataset(orderedPlaces[recurIndex: recurIndex + skippedCount], recurIndex)
                
                await getFinalDataset(placesList, (pageNum-1)*displaySize)

        print("Final Check...")
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())           
        asyncio.run(CheckRealDuration(returnList[0], returnList[1], transportMode))

    return recommendList

@app.route("/funcs/planner-recommend-places", methods=['POST'])
def recommendPlacesPlanner():
    if request.method == 'POST':
        print("Start")
        userId = session["current_user"]["userId"]
        itiDate = request.form.get("date")
        timeAllowance = float(request.form.get("timeLeft") or 999)
        latitude = float(request.form.get("latitude"))
        longitude = float(request.form.get("longitude"))
        category = request.form.get("category")
        transportMode = request.form.get("transportMode")
        skipped = json.loads(request.form.get("skipped")) 
        pageNum = int(request.args.get("page")) or 1
        placesAdded = request.form.getlist("placesAdded[]") or []
        abovePlace = request.form.get("abovePlace")
        belowPlace = request.form.get("belowPlace")
        sectionIndex = request.form.get("section")
        startTime = request.form.get("startTime")
        startTime = "08:00"

        if sectionIndex is not None:
            sectionIndex = int(sectionIndex)

        startDatetime = datetime.strptime(itiDate + " " + startTime, "%Y-%m-%d %H:%M")

        resultDict = recommenderAlgorithm(userId, startDatetime, timeAllowance, 10, latitude, longitude, category, transportMode, skipped, pageNum, placesAdded, abovePlace, belowPlace, sectionIndex)
        
        print("Done")
    return json.dumps(resultDict)

@app.route("/funcs/explorer-recommend-places", methods=['POST'])
def recommendPlacesExplorer():
    categoriesIndexMap = ["Attractions"]

    if request.method == 'POST':
        print("Start")
        userId = session["current_user"]["userId"]
        latitude = float(request.form.get("latitude"))
        longitude = float(request.form.get("longitude"))
        startDatetime = datetime.now().strptime(request.form.get("startTime"), "%H:%M")
        endTime = datetime.now().strptime(request.form.get("endTime"), "%H:%M")
        transportMode = request.form.get("transportMode")
        endLatitude = float(request.form.get("endLatitude"))
        endLongitude = float(request.form.get("endLongitude"))

        timeAllowance = (endTime - startDatetime).seconds / 60
        originalAllowance = timeAllowance

        checkTime = startDatetime

        destinations = placesAdded = []
        abovePlace = None
        totalEateries = 0

        # Determine the direction of endPoint to startPoint
        vectorDirection = [1, 1]

        if endLatitude < latitude:
            vectorDirection[0] = -1
        if endLongitude < longitude:
            vectorDirection[1] = -1
        
        # Suggest eateries 1st. If time too little, check if there is any available places he/she can go
        if timeAllowance < 120:
            resultList = recommenderAlgorithmEndPoint(userId, startDatetime, timeAllowance, 1, latitude, longitude, endLatitude, endLongitude, "Eateries", transportMode, [0], 1, [], abovePlace)
            if len(resultList) > 0:
                destinations.append(resultList[0])
        # Recommend a place to eat and go if only has < 160min allowance
        elif timeAllowance < 230:
            resultDictEatery = recommenderAlgorithm(userId, startDatetime, 105, 1, latitude, longitude, "Eateries", transportMode, [0], 1, [], abovePlace)["list"][0]
            destinations.append(resultDictEatery)
            placesAdded = list(map(lambda x: x["Address"], destinations))
            abovePlace = resultDictEatery["Address"]
            timeAllowance -= resultDictEatery["Duration"]

            randomPlaceNum = random.randint(0, len(categoriesIndexMap)-1)
            lastLatlng = resultDictEatery["Latlng"].split(",")
            resultDictExplore = recommenderAlgorithmEndPoint(userId, startDatetime, timeAllowance, 1, lastLatlng[0], lastLatlng[1], endLatitude, endLongitude, categoriesIndexMap[randomPlaceNum], transportMode, [0], 1, placesAdded, abovePlace)
            if len(resultDictExplore) > 0:
                destinations.append(resultDictExplore[0])
        else:
            eatTimes = ["10:30", "15:00", "21:00"]
            foodCheck = 0
            for i in range(len(eatTimes)):
                if startDatetime > datetime.now().strptime(eatTimes[i], "%H:%M"):
                    foodCheck += 1

            def recommendShortEnd(timeAllowance, checkTime, foodCheck, totalEateries, placesAdded, abovePlace):
                print("Recommend by short")
                def getPlaceRecommend(timeAllw, latitude, longitude, category, placesAdded, abovePlace):
                    resultDict = recommenderAlgorithm(userId, startDatetime, timeAllw, 1, latitude, longitude, category, transportMode, [0], 1, placesAdded, abovePlace)["list"]
                    if len(resultDict) == 0:
                        return {"recal": True}
                    resultDict = resultDict[0]
                    currLatLng = resultDict["Latlng"].split(",")
                    latitude = currLatLng[0]
                    longitude = currLatLng[1]
                    destinations.append(resultDict)
                    return resultDict
                
                forceFoodDuration = None
                while True:
                    try:
                        print(f"Total: {len(destinations)}")
                    except Exception:
                        pass
                    print(f"Time: {timeAllowance}")
                    # Start heading back to end point when half the time is used up
                    if timeAllowance < originalAllowance*0.6:
                        recommendFarEnd(timeAllowance, checkTime, foodCheck, totalEateries, placesAdded, abovePlace)
                        break

                    if foodCheck == 0 and totalEateries < 3:
                        if forceFoodDuration is not None:
                            resultDictEatery = getPlaceRecommend(forceFoodDuration, latitude, longitude, "Eateries", placesAdded, abovePlace)
                            forceFoodDuration = None
                        else:
                            resultDictEatery = getPlaceRecommend(140, latitude, longitude, "Eateries", placesAdded, abovePlace)
                        placesAdded = list(map(lambda x: x["Address"], destinations))
                        abovePlace = resultDictEatery["Address"]
                        checkTime += timedelta(minutes=resultDictEatery["Duration"])
                        foodCheck += 1
                        totalEateries += 1
                        timeAllowance -= resultDictEatery["Duration"]
                    else:
                        # Recommend other places - attractions, entertainment e.t.c
                        def getOtherPlaces(othersTimeAllow, destinations, timeAllowance, checkTime, placesAdded, abovePlace, forceFoodDuration):
                            if othersTimeAllow < 140:
                                randomPlaceNum = random.randint(0, len(categoriesIndexMap)-1)
                                resultDict = getPlaceRecommend(othersTimeAllow, latitude, longitude, categoriesIndexMap[randomPlaceNum], placesAdded, abovePlace)
                                if resultDict.get("recal") != None:
                                    # If the food recommended before takes too much time, find a new eatery that is closer
                                    forceFoodDuration = destinations[-1]["Duration"]*0.8
                                    checkTime -= timedelta(minutes=destinations[-1]["Duration"])
                                    timeAllowance += resultDictEatery["Duration"]
                                    totalEateries -= 1
                                    destinations.pop()
                                else:
                                    placesAdded = list(map(lambda x: x["Address"], destinations))
                                    abovePlace = resultDict["Address"]
                                    othersTimeAllow -= resultDict["Duration"]
                                    timeAllowance -= resultDict["Duration"]
                                    checkTime += timedelta(minutes=resultDict["Duration"])

                            else:
                                placesCount = random.randint(1, 2)
                                shouldBreak = False
                                for _ in range(placesCount):
                                    randomPlaceNum = random.randint(0, len(categoriesIndexMap)-1)
                                    # Recommend a place with half the time allowance
                                    resultDict = getPlaceRecommend(othersTimeAllow / placesCount, latitude, longitude, categoriesIndexMap[randomPlaceNum], placesAdded, abovePlace)
                                    if resultDict.get("recal") != None:
                                        resultDict = getPlaceRecommend(othersTimeAllow, latitude, longitude, categoriesIndexMap[randomPlaceNum], placesAdded, abovePlace)
                                        shouldBreak = True

                                    placesAdded = list(map(lambda x: x["Address"], destinations))
                                    abovePlace = resultDict["Address"]
                                    othersTimeAllow -= resultDict["Duration"]
                                    timeAllowance -= resultDict["Duration"]
                                    checkTime += timedelta(minutes=resultDict["Duration"])
                                    if shouldBreak:
                                        break
                            return timeAllowance
                        
                        nextEatTime = eatTimes[totalEateries]
                        # If food has already been added before, recommend other places
                        otherPeriods = datetime.now().strptime(nextEatTime, "%H:%M") - checkTime
                        timeAllowance = getOtherPlaces(otherPeriods.seconds / 60, destinations, timeAllowance, checkTime, placesAdded, abovePlace, forceFoodDuration)
                        foodCheck -= 1
                        
            def recommendFarEnd(timeAllowance, checkTime, foodCheck, totalEateries, placesAdded, abovePlace):
                print("Recommend by long")
                def getPlaceRecommend(timeAllw, latitude, longitude, category, placesAdded, abovePlace):
                    pageNum = 1
                    while True:
                        checkScore = 0
                        resultList = recommenderAlgorithm(userId, startDatetime, timeAllw, 5, latitude, longitude, category, transportMode, [0], pageNum, placesAdded, abovePlace)["list"]
                        if len(resultList) == 0:
                            return {"recal": True}

                        if len(resultList) > 0:
                            for result in resultList:
                                # Check if the location is heading towards the end point
                                latLng = list(map(lambda x: float(x), result["Latlng"].split(",") ))
                                if vectorDirection[0] == 1:
                                    if latLng[0] > latitude or geopy.distance.distance((latLng[0], 0), (latitude, latLng[1])).km < 2:
                                        checkScore += 1
                                else:
                                    if latLng[0] <= latitude or geopy.distance.distance((latLng[0], 0), (latitude,0)).km < 2:
                                        checkScore += 1
                                if vectorDirection[1] == 1:
                                    if latLng[1] > longitude or geopy.distance.distance((0, latLng[1]), (0, longitude)).km < 2:
                                        checkScore += 1
                                else:
                                    if latLng[1] <= longitude or geopy.distance.distance((0, latLng[1]), (0, longitude)).km < 2:
                                        checkScore += 1
                                
                                if checkScore == 2:
                                    destinations.append(result)
                                    currLatLng = result["Latlng"].split(",")
                                    latitude = currLatLng[0]
                                    longitude = currLatLng[1]
                                    return result

                            pageNum += 1
                        else:
                            break
                    
                forceFoodDuration = None
                while timeAllowance >= 180:
                    print(f"Total: {len(destinations)}")
                    print(f"Time: {timeAllowance}")
                    # Food check 0 - Recommend food time
                    if foodCheck == 0 and totalEateries < 3:
                        if forceFoodDuration is not None:
                            resultDictEatery = getPlaceRecommend(forceFoodDuration, latitude, longitude, "Eateries", placesAdded, abovePlace)
                            forceFoodDuration = None
                        else:
                            resultDictEatery = getPlaceRecommend(140, latitude, longitude, "Eateries", placesAdded, abovePlace)
                        placesAdded = list(map(lambda x: x["Address"], destinations))
                        abovePlace = resultDictEatery["Address"]

                        checkTime += timedelta(minutes=resultDictEatery["Duration"])
                        foodCheck += 1
                        totalEateries += 1
                        timeAllowance -= resultDictEatery["Duration"]
                    else:
                        # Recommend other places - attractions, entertainment e.t.c
                        def getOtherPlaces(othersTimeAllow, destinations, timeAllowance, checkTime, placesAdded, abovePlace, forceFoodDuration):
                            if othersTimeAllow < 140:
                                randomPlaceNum = random.randint(0, len(categoriesIndexMap)-1)
                                resultDict = getPlaceRecommend(othersTimeAllow, latitude, longitude, categoriesIndexMap[randomPlaceNum], placesAdded, abovePlace, forceFoodDuration)
                                if resultDict.get("recal") != None:
                                    # If the food recommended before takes too much time, find a new eatery that is closer
                                    forceFoodDuration = destinations[-1]["Duration"]*0.8
                                    totalEateries -= 1
                                else:
                                    placesAdded = list(map(lambda x: x["Address"], destinations))
                                    abovePlace = resultDict["Address"]
                                    othersTimeAllow -= resultDict["Duration"]
                                    timeAllowance -= resultDict["Duration"]
                                    checkTime += timedelta(minutes=resultDict["Duration"])
                            else:
                                placesCount = random.randint(1, 2)
                                for _ in range(placesCount):
                                    randomPlaceNum = random.randint(0, len(categoriesIndexMap)-1)
                                    # Recommend a place with half the time allowance
                                    resultDict = getPlaceRecommend(othersTimeAllow / placesCount, latitude, longitude, categoriesIndexMap[randomPlaceNum], placesAdded, abovePlace)
                                    if resultDict.get("recal") != None:
                                        previous = destinations.pop()
                                        resultDict = getPlaceRecommend(othersTimeAllow, latitude, longitude, categoriesIndexMap[randomPlaceNum], placesAdded, abovePlace)
                                        shouldBreak = True

                                    placesAdded = list(map(lambda x: x["Address"], destinations))
                                    abovePlace = resultDict["Address"]
                                    othersTimeAllow -= resultDict["Duration"]
                                    timeAllowance -= resultDict["Duration"]
                                    checkTime += timedelta(minutes=resultDict["Duration"])
                                    if shouldBreak:
                                        break
                            return timeAllowance
                        
                        nextEatTime = eatTimes[totalEateries]
                        # If food has already been added before, recommend other places
                        otherPeriods = datetime.now().strptime(nextEatTime, "%H:%M") - checkTime
                        if not getOtherPlaces(otherPeriods.seconds / 60, destinations, timeAllowance, checkTime, placesAdded, abovePlace, forceFoodDuration):
                            break
                        foodCheck -= 1  

                # Try to recommend one more place
                resultList = {}
                if destinations[-1]["Category"] == "Eateries":
                    skipped = 0
                    randomPlaceNum = random.randint(0, len(categoriesIndexMap)-1)
                    print("Using algorithm 7")
                    resultList = recommenderAlgorithmEndPoint(userId, startDatetime, timeAllowance, 1, latitude, longitude, endLatitude, endLongitude, categoriesIndexMap[randomPlaceNum], transportMode, [skipped], 2, placesAdded, abovePlace)
                else:
                    print("Using algorithm 8")
                    resultList = recommenderAlgorithmEndPoint(userId, startDatetime, timeAllowance, 1, latitude, longitude, endLatitude, endLongitude, "Eateries", transportMode, [0], 1, placesAdded, abovePlace)
                if len(resultList) > 0:
                    destinations.append(resultList[0])

            # Check if the distance is considered far or short
            dist = geopy.distance.distance((latitude, longitude), (endLatitude, longitude)).km
            if dist <= 25:
                recommendShortEnd(timeAllowance, checkTime, foodCheck, totalEateries, placesAdded, abovePlace)
            else:
                recommendFarEnd(timeAllowance, checkTime, foodCheck, totalEateries, placesAdded, abovePlace)

        print("Done")
    return json.dumps(destinations)

@app.route("/funcs/reCalculate", methods=['POST'])
def reCalculateCards():
    latlngs = request.form.getlist("latlngs[]")
    routeType = request.form.get("routeType")
    tripDate = request.form.get("date")
    upperDuration = float(request.form.get("topDuration"))
    startTime = request.form.get("startTime") or "12:00"

    print(latlngs)

    parseTime = datetime.strptime(f"{tripDate} {startTime}", "%Y-%m-%d %H:%M") + timedelta(minutes=upperDuration)
    travelDurations = []

    async def apiGetTime():
        async with aiohttp.ClientSession() as clientSession:
            for i in range(len(latlngs)-1):
                if latlngs[i] == "":
                    break
                
                res = await clientSession.get(f"https://developers.onemap.sg/privateapi/routingsvc/route?start={latlngs[i]}&end={latlngs[i+1]}" \
                            f"&routeType={routeType}&token={apiKey}&date={tripDate}&time={parseTime.strftime('%H:%M:%S')}" \
                            f"&mode=TRANSIT&numItineraries=1", ssl=False)
                result = await res.json()

                print(result)
                if routeType == "pt" or routeType == "bus":
                    travelDurations.append(int(result["plan"]["itineraries"][0]["duration"] / 60))
                else:
                    travelDurations.append(int(result["route_summary"]["total_time"] / 60))

    asyncio.run(apiGetTime())
    return json.dumps(travelDurations)

@app.route("/funcs/reached-place", methods=['GET', 'POST'])
def reachedPlace():
    # Placeholder returned data
    getpoints(False)

@app.route("/funcs/bookmark-place", methods=['POST'])
def bookmarkPlace():

    return json.dumps({"success": True})

@app.route("/funcs/unbookmark-place", methods=['POST'])
def unbookmarkPlace():

    return json.dumps({"success": True})

def getAllWebscrapData():
    for cat in categoriesInfo:
        data = pandas.read_csv("csv/webcsv/"+categoriesInfo[cat]["filename"], encoding = "ISO-8859-1")
        allWebscrapData[cat] = data

@app.route("/funcs/search")
def search():
    query = request.args.get("s")
    page = int(request.args.get("page"))
    cat = request.args.get("cat")

    webScrapData = allWebscrapData[cat]
    return json.dumps(list(webScrapData[webScrapData["Name"].str.contains(query, na=False, case=False)].to_dict(orient='records')[(page-1)*10: (page)*10]))

@app.route("/funcs/clear-planner", methods=['POST'])
def clearPlanner():
    plannerId = request.args.get("id")
    if plannerId is not None:
        res = itinerariesCon.ClearPlanner(plannerId)
        return json.dumps(res)
    
    return json.dumps({"success": False, "error": "No planner id supplied"})

@app.route("/funcs/save-trip", methods=['POST'])
def saveTrip():
    if request.method == 'POST':
        itineraryId = request.form.get("id") or None
        userId = session["current_user"]["userId"]
        tripType = request.form.get("tripType")
        tripName = request.form.get("tripName")
        date = request.form.get("date")
        startTime = request.form.get("startTime")
        endTime = request.form.get("endTime") or "23:59"
        names = request.form.getlist("names[]")
        addresses = request.form.getlist("addresses[]")
        categories = request.form.getlist("categories[]")
        images = request.form.getlist("images[]")
        activitiesDuration = request.form.getlist("activityDuration[]")
        durations = request.form.getlist("duration[]")
        latlngs = request.form.getlist("latlngs[]")
        description = request.form.get("description") or None
        timeAllowance = float(request.form.get("timeAllowance") or 900) or None
        timeLeft = float(request.form.get("timeLeft") or 900) or None
        transportMode = request.form.get("transportMode")
        confirmed = request.form.get("confirmed").lower() == "true"
        status = request.form.get("status")
        plannerId = request.form.get("plannerId")
        hasEnd = request.form.get("hasEnd").lower() == "true"

        print(f"Planner id: {plannerId}")
        if not plannerId:
            plannerId = None

        if date == "Today":
            date = datetime.now()
        else:
            date = datetime.strptime(date, "%Y-%m-%d")

        places = []
        print(activitiesDuration)
        print(durations)
        for i in range(len(addresses)):
            activityDuration = activitiesDuration[i]
            duration = durations[i]
            travelDuration = None
            if not activityDuration:
                activityDuration = None
            else:
                activityDuration = int(activityDuration)
            if not duration:
                duration = None
            else:
                duration = float(duration)
                try:
                    travelDuration = duration - activityDuration
                except TypeError:
                    travelDuration = duration

            places.append({"Name": names[i], "Address": addresses[i], "Category": categories[i], "Image": images[i], "ActivityDuration": activityDuration, 
                            "TravelDuration": travelDuration, "TotalDuration": duration, "Latlng": latlngs[i]})

        itinerary = Itinerary(itineraryId, userId, tripName, date, startTime, endTime, tripType, transportMode, timeAllowance, timeLeft, confirmed, status, places, description, plannerId, hasEnd)
        itinerariesCon.SetItinerary(itinerary)
        returnIti = itinerariesCon.GetUnconfimredItinerary(userId, tripType)

    if tripType == "Planner":
        return json.dumps({"id": list(map(lambda x: str(x.getId()), returnIti)), "plannerId": returnIti[0].getPlannerId()})
    
    return json.dumps({"id": str(returnIti.getId())})

@app.route("/funcs/mark-track", methods=['POST'])
def markTracked():
    res = trackedPlacesCon.SetInfo(TrackedPlace(session["current_user"]["userId"], request.form.get("address"), request.form.get("name"), request.form.get("img"), request.form.get("category"), request.form.get("action")))
    return json.dumps(res)

@app.route("/funcs/admin/table_getSignedPlaces")
def tableGetSignedPlaces():
    args = request.args
    resultDict = signedPlaceCon.ViewListOfPlaces(args.get("search"), args.get("sort"), args.get("order"),
                                                 args.get("limit"), args.get("offset"))
    return json.dumps(resultDict)

@app.route("/funcs/generate-claimBonus-qrcode", methods=['POST'])
@app.route("/funcs/generate-usePoints-qrcode", methods=['POST'])
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

@app.route("/funcs/check-valid-placeId", methods=['POST'])
def checkValidPlace():
    if request.method == 'POST':
        placeId = request.form.get("placeId")
        place = signedPlaceCon.GetShopById(placeId)
        return json.dumps({"valid": place is not None}) 

# Api function to generate code when the shop cashier prints the receipt
@app.route("/funcs/gen-redeem-code", methods=['POST'])
def genRedeemCode():
    placeId = request.form.get("placeId")
    signedPlaceCon.GenNewCode(placeId)

# Scheduled tasks to run every week - Web scrap, training of data models
def scheduledJobs():
    # Encode label strings
    def encodeColumns(data):   
        for column_name in data.columns:
            if data[column_name].dtype != numpy.number:
                data[column_name] = globalPrefLE.fit_transform(data[column_name])

        return data

    def trainGlobalUserPreferenceModel():
        path = userCon.ExportGlobalUserPreferenceCSV()  # Supply the new data in db to the csv files
        data = encodeColumns(pandas.read_csv(path))

        inp = data.drop(columns=['Preference'])
        oup = data['Preference']

        # Usage of K-Neighbours algorithm - Many overlaps
        model = MultinomialNB()

        # Calculating average accuracy of current model
        meanAccuracyScore = 0
        try:
            model.fit(inp.values, oup)
            for _ in range(1, 6):
                inp_train, inp_test, oup_train, oup_test = train_test_split(inp, oup, test_size=0.2)
                model.fit(inp_train, oup_train)
                predictions = model.predict(inp_test)
                meanAccuracyScore += accuracy_score(oup_test, predictions)
            meanAccuracyScore /= 5

            # Saving the model and accuracy results
            model.fit(inp.values, oup)
        except ValueError as e:
            print(e)
            pass
        finally:
            joblib.dump(model, "csv/dbcsv/global-users-preferences.joblib")  # Saves the newly trained model as a file
            machineLearningReportCon.SetData(MachineLearningReport("GlobalUserPreferences", "Accuracy",
                                                                meanAccuracyScore))  # Save the accuracy score to db

    def trainFutureTrackedInfoModel():
        path = trackedPlacesCon.ExportYourTrackedInfoCSV()  # Supply the new data in db to the csv files
        data = encodeColumns(pandas.read_csv(path))

        inp = data.drop(columns=['Preference'])
        oup = data['Preference']

        # Usage of Decision Tree Regression - predict cuisines with today date
        model = DecisionTreeRegressor()

        # Calculating average accuracy of current model
        meanAccuracyScore = 0
        try:
            model.fit(inp.values, oup)
            for _ in range(1, 6):
                inp_train, inp_test, oup_train, oup_test = train_test_split(inp, oup, test_size=0.2)
                model.fit(inp_train, oup_train)
                predictions = model.predict(inp_test)
                meanAccuracyScore += accuracy_score(oup_test, predictions)
            meanAccuracyScore /= 5

            # Saving the model and accuracy results
            model.fit(inp.values, oup)
        except ValueError as e:
            print(e)
            pass
        finally:
            joblib.dump(model, "csv/dbcsv/future-tracked-info-preferences.joblib")  # Saves the newly trained model as a file
            machineLearningReportCon.SetData(MachineLearningReport("FutureTrackedInfoPreferences", "Accuracy",
                                                                meanAccuracyScore))  # Save the accuracy score to db

    def webScrap():
        print("I am web scrapping")

    trainGlobalUserPreferenceModel()
    trainFutureTrackedInfoModel()
    webScrap()

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


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
    warnings.simplefilter(action='ignore', category=FutureWarning)
    getAllWebscrapData()
    app.run()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
