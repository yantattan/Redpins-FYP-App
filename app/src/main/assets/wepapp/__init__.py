from urllib.error import HTTPError
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from apscheduler.scheduler import Scheduler
from io import BytesIO
import uuid

# Required libraries
from datetime import datetime, timedelta, date
from time import strftime
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
apiKey = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOjg1NDQsInVzZXJfaWQiOjg1NDQsImVtYWlsIjoieWFudGF0dGFuNzIxQGdtYWlsLmNvbSIsImZvcmV2ZXIiOmZhbHNlLCJpc3MiOiJodHRwOlwvXC9vbTIuZGZlLm9uZW1hcC5zZ1wvYXBpXC92MlwvdXNlclwvc2Vzc2lvbiIsImlhdCI6MTY1MDUwODg4MSwiZXhwIjoxNjUwOTQwODgxLCJuYmYiOjE2NTA1MDg4ODEsImp0aSI6ImE4OWQwZGQwNmM0MjExNTFkYzk5ODk4ZjE1MjlhYzY5In0.sLMl9j1EUUjMa9-LWgrDkRHQonIk9CxGBJMazxTNC8g"

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
    "Eateries": {"filename":"restaurants_info.csv", "category":"Eateries", "activityTime": 45}
}

# Functions to perform before showing the page
@app.route("/")
def homePage():
    # To render the page (pathing starts from templates folder after). After the filename, variables defined behind are
    # data that the site needs to use
    # session.pop("current_user", None)

    # yourLocation = geocoder.ip("me")
    # scheduledJobs()
    if session.get("current_user") is None:
        return redirect("/login")
    
    return render_template("home.html", y="Meh")

@app.route("/discover/<string:category>")
def discoverCategories(category):
    if category == "popular-places":
        print("Most popular")
    else:
        webScrapData = pandas.read_csv("csv/webcsv/"+categoriesInfo[category]["filename"], encoding = "ISO-8859-1")
        # trackedPlacesCon.

    return render_template("discoverCategories.html")

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


#Onboarding page
@app.route("/onboarding")
def onBoardingPage():
    return render_template("onboarding/onboarding01.html")

@app.route("/loading")
def loading():
    return render_template("includes/_loading.html")

# Itinerary planning pages
@app.route("/itineraries")
def showItineraries():
    return render_template("/itinerary/listItineraries.html")

@app.route("/itinerary/selectPlan")
def selectItineraryPlan():
    return render_template("itinerary/selectPlan.html")

@app.route("/itinerary/planning/planner", methods=['GET', 'POST'])
def planItinerary():
    return render_template("/itinerary/planItinerary.html")

@app.route("/itinerary/planning/explorer", methods=['GET', 'POST'])
def recommendItinerary():
    return render_template("/itinerary/autoItinerary.html")

@app.route("/itinerary/confirmation")
def confirmItinerary():
    return render_template("/itinerary/confirmItinerary.html")

@app.route("/itinerary/showTrip")
def showTrip():
    return render_template("/itinerary/showTrip.html")


# Preferences pages -- Send pref to db (Daoying)
@app.route("/preferences/1", methods=['GET', 'POST'])
def pref1():
    invalidRedirect = validateSession()
    if invalidRedirect is not None:
        print(invalidRedirect)
        return redirect(invalidRedirect)

    if request.method == 'POST':
        category = "Eateries"
        allPrefs = request.form.getlist("preferences[]")
        pref = Preferences(session["current_user"]["userId"], allPrefs, category)
        userCon.SetPreferences(pref)
        newUserInfo = userCon.SetSetupComplete(session["current_user"]["userId"])
        session["current_user"] = newUserInfo
        print(allPrefs)
        return redirect("/")
    else:
        print("Hello")
    return render_template("preferences/preference1.html")


@app.route("/yourReview/<string:address>", methods=['GET', 'POST'])
def editReview(address):
    review_form = ReviewForm(request.form)
    return render_template("editReview.html", form=review_form)


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
    print("Claim bonus reached")
    return render_template("/rewardPoints/claimBonus.html")

@app.route("/qrCode/use-points/<string:id>")
def qrCodeUsePoints(id):
    Total_price = " "
    Uid = session["current_user"]["userId"]
    resultDic = {"shopName": "MARINA BAY SANDS", "address": "123B PornHub Hub Singapore 512345"}
    result = userCon.GetUserPointsInfo(Uid)
    result2 = signedPlaceCon.GetShopInfo(resultDic["address"])
    discount = result2.getDiscount()
    uPoints = result.getPoints()
    # new_uPoints = uPoints - Total_price*(1 - discount)
    # userCon.SetPoints(Uid, new_uPoints, tierPoints  )
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

def calculateAndReturnList(userId, category, webScrapData, shortlistedPlaces, displaySize, activityTime, skipped):
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
                cuisines = dataRow["Cuisines"].split(",")
                for cuisine in cuisines:
                    try:
                        freqtrackedPlacesCuisine[cuisine] += 1
                    except KeyError:
                        freqtrackedPlacesCuisine[cuisine] = 1
        
        # Check for rerecommend places on top 5 searches 
        for place in yourTop5Search:
            rerecommendPoints = 0 # If >=0, can rerecommend
            dataRow = webScrapData.loc[webScrapData["Address"] == place["Address"].replace(", ", "|")]

            if len(dataRow.values) > 0:
                for action in place["Actions"]:
                    addPoints = actionPoints[action] * place["Actions"]["Searched"]["Frequency"]
                    rerecommendPoints += addPoints

                if rerecommendPoints >= 0:
                    rerecommend.append(dataRow["Restaurant_name"].values[0])

        # Score preferences based on regression of his preferences 
        for action in actionPoints:
            yourFuturePref = trackedInfoPreference.predict([trackedInfoLE.fit_transform([userId, "Eateries", action, str(datetime.now()) ])])[0]
            try:
                futuretrackedPlacesPoints[yourFuturePref] += 1
            except KeyError:
                futuretrackedPlacesPoints[yourFuturePref] = 1

        # START OF CHECK AGAINST LISTS
        scoredPlaces = []
        for place in shortlistedPlaces:
            netChance = 0   # -- Chance calculation for every place shortlisted
            if not place.Restaurant_name in list(webScrapData["Restaurant_name"]):
                # Low chance to try and exclude restaurants outside of our dataset
                netChance = 0.1
            else:
                # #1 - Check against global and your preference
                cuisinesMatch = 0
                yourPrefs = userCon.GetPreferences(userId, category)
                restaurantDetails = webScrapData.loc[webScrapData["Restaurant_name"] == place.Restaurant_name]
                restaurantCuisines = restaurantDetails["Cuisines"].values[0].split("|")

                for pref in top5Pref:
                    if pref in restaurantCuisines:
                        cuisinesMatch += 1 * globalPrefAccuracy
                for pref in yourPrefs.getPreferences():
                    if pref in restaurantCuisines:
                        cuisinesMatch += 2

                cuisinesMatch /= 15
                netChance += cuisinesMatch * 0.35

                # #2 - Check reviews
                reviews = reviewsCon.GetReviews(place.Address)
                if reviews is not None:
                    calRating = restaurantDetails["Rating"].values[0] * 0.25 + reviews * 0.75
                    calRating /= 5
                    # calRatingXVal = calRating * 0.5
                    # netChance += ((2 * calRatingXVal * (1 - calRatingXVal) + 0.5) * calRating) * 0.35
                    netChance += calRating * 0.25
                else:
                    calRating = restaurantDetails["Rating"].values[0] / 5
                    netChance += calRating * 0.25

                # #3 - Check against the cuisines & places recommended from your tracked history
                trackedMatch = 0
                if freqtrackedPlacesCuisine != {}:
                    if place.Restaurant_name in rerecommend:
                        trackedMatch += 5

                    for cuisine in restaurantCuisines:
                        trackedMatch += freqtrackedPlacesCuisine[cuisine]
                        trackedMatch += futuretrackedPlacesPoints[cuisine]

                trackedMatch /= 13
                
                netChance += trackedMatch * 0.2

                # #4 - Check if the places are our partners
                partnered = signedPlaceCon.CheckPlace(place.Restaurant_name)
                if partnered:
                    netChance += 0.2
            
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

def recommenderAlgorithm(userId, timeAllowance, displaySize, latitude, longitude, category, transportMode, activityTime, skipped, pageNum):
    recommendList = []

    def ShortlistByDistance(placesList, transportMode):
        pList = []
        for place in placesList.itertuples():
            # 1st stage shortlisting - Determined by roughly estimated average speed of transports
            # Find according to furthest distance possible (a and b distance)
            placeLatlng = place.Latlng.split("|")
            if len(placeLatlng) < 2:
                continue
            placeLatlng = list(map(lambda x: round(float(x), 7), placeLatlng))
            aDist = geopy.distance.distance((latitude, 0), (placeLatlng[0], 0)).km
            bDist = geopy.distance.distance((0, longitude), (0, placeLatlng[1])).km
            furDist = aDist + bDist

            estTime = (furDist // averageSpeeds[transportMode] + activityTime / 60) * 60
            if estTime <= timeAllowance:
                # 2nd stage shortlisting - Determined by the fastest route (actual timing needed)
                pList.append(place)
            
        return pList    

     # Shortlisted after calculating distance
    webScrapData = pandas.read_csv("csv/webcsv/"+categoriesInfo[category]["filename"], encoding = "ISO-8859-1")
    shortlistedPlaces = ShortlistByDistance(webScrapData, transportMode)

    if len(shortlistedPlaces) > 0:
        returnList = calculateAndReturnList(userId, category, webScrapData, shortlistedPlaces, displaySize, activityTime, skipped)

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
                        placeLatlng = place["Latlng"].split("|")
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
                            if transportMode == "pt":
                                estTime += routeResults["plan"]["itineraries"][0]["duration"] / 60
                            else:
                                estTime += routeResults["route_summary"]["total_time"] / 60

                            if estTime <= timeAllowance:
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

def recommenderAlgorithmEndPoint(userId, timeAllowance, displaySize, latitude, longitude, endLatitude, endLongitude, category, transportMode, activityTime, skipped, pageNum):
    recommendList = []

    def ShortlistByDistance(placesList, transportMode):
        pList = []
        for place in placesList.itertuples():
            # 1st stage shortlisting - Determined by roughly estimated average speed of transports
            # Find according to furthest distance possible (a and b distance)
            placeLatlng = place.Latlng.split("|")
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
                # 2nd stage shortlisting - Determined by the fastest route (actual timing needed)
                pList.append(place)
            
        return pList    

     # Shortlisted after calculating distance
    webScrapData = pandas.read_csv("csv/webcsv/"+categoriesInfo[category]["filename"], encoding = "ISO-8859-1")
    shortlistedPlaces = ShortlistByDistance(webScrapData, transportMode)

    if len(shortlistedPlaces) > 0:
        returnList = calculateAndReturnList(userId, category, webScrapData, shortlistedPlaces, displaySize, activityTime, skipped)

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
                        placeLatlng = place["Latlng"].split("|")
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
                                estTime += (routeResults["plan"]["itineraries"][0]["duration"] + endRouteResults["plan"]["itineraries"][0]["duration"]) / 60
                            else:
                                estTime += (routeResults["route_summary"]["total_time"] + endRouteResults["route_summary"]["total_time"]) / 60

                            if estTime <= timeAllowance:
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

    return recommendList

@app.route("/funcs/planner-recommend-places", methods=['POST'])
def recommendPlacesPlanner():
    if request.method == 'POST':
        print("Start")
        userId = session["current_user"]["userId"]
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")
        timeAllowance = int(request.form.get("timeAllowance"))
        category = request.form.get("category")
        transportMode = request.form.get("transportMode")
        skipped = json.loads(request.form.get("skipped")) 
        pageNum = int(request.args.get("page")) or 1

        activityTime = categoriesInfo[category]["activityTime"]
        if timeAllowance < 105:
            activityTime = round(activityTime * 0.75)

        resultDict = recommenderAlgorithm(userId, timeAllowance, 10, latitude, longitude, category, transportMode, activityTime, skipped, pageNum)

        print("Done")
    return json.dumps(resultDict)

@app.route("/funcs/explorer-recommend-places", methods=['POST'])
def recommendPlacesExplorer():
    categoriesIndexMap = ["Eateries"]

    if request.method == 'POST':
        print("Start")
        userId = session["current_user"]["userId"]
        latitude = float(request.form.get("latitude"))
        longitude = float(request.form.get("longitude"))
        timeAllowance = int(request.form.get("timeAllowance"))
        transportMode = request.form.get("transportMode")
        endLatitude = float(request.form.get("endLatitude"))
        endLongitude = float(request.form.get("endLongitude"))

        destinations = []
        totalEateries = 0
        
        # Suggest eateries 1st. If time too little, check if there is any available places he/she can go
        activityTime = 45
        if timeAllowance < 120:
            if timeAllowance < 105:
                activityTime = round(activityTime * 0.75)

            resultList = recommenderAlgorithmEndPoint(userId, timeAllowance, 1, latitude, longitude, endLatitude, endLongitude, "Eateries", transportMode, activityTime, [0], 1)
            if len(resultList) > 0:
                destinations.append(resultList[0])
        # Recommend a place to eat and go if only has < 160min allowance
        elif timeAllowance < 180:
            activityTime = 30
            resultDictEatery = recommenderAlgorithm(userId, 80, 1, latitude, longitude, "Eateries", transportMode, activityTime, [0], 1)["list"][0]
            destinations.append(resultDictEatery)
            timeAllowance -= resultDictEatery["Duration"]

            activityTime = 45
            randomPlaceNum = random.randint(0, len(categoriesIndexMap)-1)
            lastLatlng = resultDictEatery["Latlng"].split("|")
            resultDictExplore = recommenderAlgorithmEndPoint(userId, timeAllowance, 1, lastLatlng[0], lastLatlng[1], endLatitude, endLongitude, categoriesIndexMap[randomPlaceNum], transportMode, activityTime, [0], 1)
            if len(resultDictExplore) > 0:
                destinations.append(resultDictExplore[0])
            activityTime = 45
        else:
            foodCheck = 0
            checkTime = datetime.now()

            def recommendShortEnd(timeAllowance, checkTime, foodCheck, totalEateries, activityTime):
                vectorDirection = [1, 1]
                originalTimeAllowance = timeAllowance

                if endLatitude < latitude:
                    vectorDirection[0] = -1
                if endLongitude < longitude:
                    vectorDirection[1] = -1
                
                while timeAllowance >= 180:
                    if foodCheck == 0:
                        print("Using algorithm 1")
                        resultDictEatery = recommenderAlgorithm(userId, 140, 1, latitude, longitude, "Eateries", transportMode, activityTime, [0], 1)["list"][0]
                        destinations.append(resultDictEatery)
                        timeAllowance -= resultDictEatery["Duration"]
                        checkTime += timedelta(minutes=resultDictEatery["Duration"])
                        foodCheck += 1
                        totalEateries += 1
                    else:
                        # If time left is already halfway, start leading them back
                        if timeAllowance <= originalTimeAllowance / 2:
                            print("Using algorithm 2")
                            recommendFarEnd(timeAllowance, checkTime, foodCheck, totalEateries, activityTime)
                            return
                        # Recommend places at any direction in the tophalf
                        else:
                            eatTimes = ["10 30 00", "3 30 00", "9 00 00"]
                            def getOtherPlaces(timeAllowance, checkTime):
                                randomPlaceNum = random.randint(0, len(categoriesIndexMap)-1)
                                if timeAllowance < 120:
                                    print("Using algorithm 3")
                                    resultDict = recommenderAlgorithm(userId, timeAllowance, 1, latitude, longitude, categoriesIndexMap[randomPlaceNum], transportMode, activityTime, [0], 1)["list"][0]
                                    destinations.append(resultDict)
                                    timeAllowance -= resultDict["Duration"]
                                    checkTime += timedelta(minutes=resultDict["Duration"])
                                else:
                                    placesCount = random.randint(1, 2)
                                    for i in range(placesCount):
                                        print("Using algorithm 4")
                                        resultDict = recommenderAlgorithm(userId, timeAllowance / placesCount, 1, latitude, longitude, categoriesIndexMap[randomPlaceNum], transportMode, activityTime, [0], 1)["list"]
                                        if len(resultDict) == 0 and i == 2:
                                            resultDict = recommenderAlgorithm(userId, timeAllowance, 1, latitude, longitude, categoriesIndexMap[randomPlaceNum], transportMode, activityTime, [0], 1)["list"][0]
                                        else:
                                            resultDict = resultDict[0]
                                        
                                        destinations.append(resultDict)
                                        timeAllowance -= resultDict["Duration"]
                                        checkTime += timedelta(minutes=resultDict["Duration"])
                            
                            nextEatTime = 0
                            if foodCheck == 1:
                                nextEatTime = eatTimes[totalEateries-1]
                                # If food has already been added before, recommend other places
                                otherPeriods = datetime.now().strptime(nextEatTime, "%H %M %S") - checkTime
                                if otherPeriods.seconds / 60 > 60: 
                                    getOtherPlaces(otherPeriods.seconds / 60, checkTime)
                                foodCheck += 1
                            elif totalEateries < 3:
                                # Recommend eateries after
                                i = 0
                                pageNum = 1
                                print("Using algorithm 5")
                                resultDictEatery = recommenderAlgorithm(userId, 140, 5, latitude, longitude, "Eateries", transportMode, activityTime, [0], pageNum)["list"]
                                while True:
                                    try:
                                        if resultDictEatery[i]["Restaurant_name"] not in list(map(lambda x: x["Restaurant_name"], destinations)):
                                            destinations.append(resultDictEatery[i])
                                            totalEateries += 1
                                            break   
                                        else:
                                            i += 1
                                    except IndexError:
                                        pageNum += 1
                                        i = 0
                                        print("Using algorithm 6")
                                        resultDictEatery = recommenderAlgorithm(userId, 140, 5, latitude, longitude, "Eateries", transportMode, activityTime, [0], pageNum)["list"]

                                timeAllowance -= resultDictEatery[i]["Duration"]
                                checkTime += timedelta(minutes=resultDictEatery[i]["Duration"])
                                totalEateries += 1
                                foodCheck -= 1
                            else:
                                break
                    
                if timeAllowance > 100:
                    resultList = {}
                    randomPlaceNum = random.randint(0, len(categoriesIndexMap)-1)
                    if destinations[-1]["Category"] == "Eateries":
                        activityTime = 45
                        skipped = 0
                        found = False
                        while True:
                            checkScore = 0
                            print("Using algorithm 7")
                            resultList = recommenderAlgorithmEndPoint(userId, timeAllowance, 5, latitude, longitude, endLatitude, endLongitude, categoriesIndexMap[randomPlaceNum], transportMode, activityTime, [skipped], 2)
                            if len(resultList) > 0:
                                for place in resultList:
                                    checkScore = 0
                                    # Check if the location is heading towards the end point
                                    latLng = list(map(lambda x: float(x), place["Latlng"].split("|")))
                                    if vectorDirection[0] == 1:
                                        if latLng[0] > latitude or geopy.distance.distance((latLng[0], 0), (latitude,0)).km < 1:
                                            checkScore += 1
                                    else:
                                        if latLng[0] <= latitude or geopy.distance.distance((latLng[0], 0), (latitude,0)).km < 1:
                                            checkScore += 1
                                    if vectorDirection[1] == 1:
                                        if latLng[1] > longitude or geopy.distance.distance((0, latLng[1]), (0, longitude)).km < 1:
                                            checkScore += 1
                                    else:
                                        if latLng[1] <= longitude or geopy.distance.distance((0, latLng[1]), (0, longitude)).km < 1:
                                            checkScore += 1

                                    print(checkScore)
                                    if checkScore == 2:
                                        destinations.append(resultList[0])
                                        found = True
                                        break
                                    else:
                                        skipped += 1
                                
                                if found:
                                    break

                            else:
                                break

                    else:
                        activityTime = round(activityTime * 0.75)
                        print("Using algorithm 8")
                        resultList = recommenderAlgorithmEndPoint(userId, timeAllowance, 1, latitude, longitude, endLatitude, endLongitude, "Eateries", transportMode, activityTime, [0], 1)

            def recommendFarEnd(timeAllowance, checkTime, foodCheck, totalEateries, activityTime):
                vectorDirection = [1, 1]

                if endLatitude < latitude:
                    vectorDirection[0] = -1
                if endLongitude < longitude:
                    vectorDirection[1] = -1

                while timeAllowance >= 180:
                    if foodCheck == 0:
                        resultDictEatery = recommenderAlgorithm(userId, 140, 1, latitude, longitude, "Eateries", transportMode, activityTime, [0], 1)["list"][0]
                        destinations.append(resultDictEatery)
                        timeAllowance -= resultDictEatery["Duration"]
                        checkTime += timedelta(minutes=resultDictEatery["Duration"])
                        foodCheck += 1
                        totalEateries += 1
                    else:
                        eatTimes = ["10 30 00", "3 30 00", "9 00 00"]
                        def getOtherPlaces(timeAllowance, checkTime):
                            if timeAllowance < 200:
                                randomPlaceNum = random.randint(0, len(categoriesIndexMap)-1)
                                resultDict = recommenderAlgorithm(userId, timeAllowance, 1, latitude, longitude, categoriesIndexMap[randomPlaceNum], transportMode, activityTime, [0], 1)["list"][0]
                                destinations.append(resultDict)
                                timeAllowance -= resultDict["Duration"]
                                checkTime += timedelta(minutes=resultDict["Duration"])
                            else:
                                placesCount = random.randint(1, 2)
                                for _ in range(placesCount):
                                    randomPlaceNum = random.randint(0, len(categoriesIndexMap)-1)
                                    resultDict = recommenderAlgorithm(userId, timeAllowance / placesCount, 1, latitude, longitude, categoriesIndexMap[randomPlaceNum], transportMode, activityTime, [0], 1)["list"][0]
                                    destinations.append(resultDict)
                                    timeAllowance -= resultDict["Duration"]
                                    checkTime += timedelta(minutes=resultDict["Duration"])
                        
                        nextEatTime = 0
                        if foodCheck == 1:
                            nextEatTime = eatTimes[totalEateries-1]
                            # If food has already been added before, recommend other places
                            otherPeriods = datetime.now().strptime(nextEatTime, "%H %M %S") - checkTime
                            getOtherPlaces(otherPeriods.seconds / (60*60), checkTime)
                            foodCheck += 1
                        elif totalEateries < 3:
                            # Recommend eateries after
                            i = 0
                            pageNum = 1
                            resultDictEatery = recommenderAlgorithm(userId, 140, 5, latitude, longitude, "Eateries", transportMode, activityTime, [0], pageNum)["list"]
                            while True:
                                try:
                                    if resultDictEatery[i]["Restaurant_name"] not in list(map(lambda x: x["Restaurant_name"], destinations)):
                                        destinations.append(resultDictEatery[i])
                                        totalEateries += 1
                                        break   
                                    else:
                                        i += 1
                                except IndexError:
                                    pageNum += 1
                                    i = 0
                                    resultDictEatery = recommenderAlgorithm(userId, 140, 5, latitude, longitude, "Eateries", transportMode, activityTime, [0], pageNum)["list"]

                            timeAllowance -= resultDictEatery[i]["Duration"]
                            checkTime += timedelta(minutes=resultDictEatery[i]["Duration"])
                            totalEateries += 1
                            foodCheck -= 1
                        else:
                            break
                    
                if timeAllowance > 60:
                    resultList = {}
                    randomPlaceNum = random.randint(0, len(categoriesIndexMap)-1)
                    if destinations[-1]["Category"] == "Eateries":
                        activityTime = 45
                        while True:
                            checkScore = 0
                            resultList = recommenderAlgorithmEndPoint(userId, timeAllowance, 1, latitude, longitude, endLatitude, endLongitude, categoriesIndexMap[randomPlaceNum], transportMode, activityTime, [0], 1)
                            if len(resultList) > 0:
                                # Check if the location is heading towards the end point
                                latLng = resultList[0]["Latlng"].split("|")
                                if vectorDirection[0] == 1:

                                    if latLng[0] > latitude or geopy.distance.distance((latLng[0] - latitude), (0,0)) < 1:
                                        checkScore += 1
                                else:
                                    if latLng[0] <= latitude or geopy.distance.distance((latLng[0] - latitude), (0,0)) < 1:
                                        checkScore += 1
                                if vectorDirection[1] == 1:
                                    if latLng[1] > longitude or geopy.distance.distance((latLng[1] - longitude), (0,0)) < 1:
                                        checkScore += 1
                                else:
                                    if latLng[1] <= longitude or geopy.distance.distance((latLng[1] - longitude), (0,0)) < 1:
                                        checkScore += 1
                                
                                if checkScore == 2:
                                    destinations.append(resultList[0])
                            else:
                                break

                    else:
                        activityTime = round(activityTime * 0.75)
                        resultList = recommenderAlgorithmEndPoint(userId, timeAllowance, 1, latitude, longitude, endLatitude, endLongitude, "Eateries", transportMode, activityTime, [0], 1)

            # Check if the distance is considered far or short
            dist = geopy.distance.distance((latitude, longitude), (endLatitude, longitude)).km
            if dist <= 25:
                print("Recommend by short")
                recommendShortEnd(timeAllowance, checkTime, foodCheck, totalEateries, activityTime)
            else:
                print("Recommend by long")
                recommendFarEnd(timeAllowance, checkTime, foodCheck, totalEateries, activityTime)

        print("Done")
    return json.dumps(destinations)

@app.route("/funcs/reached-place", methods=['GET', 'POST'])
def reachedPlace():
    # Placeholder returned data
    getpoints(False)

@app.route("/funcs/save-trip", methods=['POST'])
def autoSaveTrip():
    if request.method == 'POST':
        userId = session["current_user"]["userId"]
        tripType = request.form.get("tripType")
        tripName = request.form.get("tripName")
        date = request.form.get("date")
        names = request.form.get("names")
        addresses = request.form.get("addresses")
        activitiesDuration = request.form.get("activityDuration")
        durations = request.form.get("duration")
        timeAllowance = float(request.form.get("timeAllowance"))
        timeLeft = float(request.form.get("timeLeft"))
        transportMode = request.form.get("transportMode")

        if date == "Today":
            date = datetime.now()

        places = []
        for i in range(len(addresses)):
            places.append({"Name": names[i], "Address": addresses[i], "ActivityDuration": activitiesDuration[i], 
                            "TotalDuration": durations[i]})

        itinerary = Itinerary(None, userId, tripName, date, tripType, transportMode, timeAllowance, timeLeft, places)
        itinerariesCon.SetItinerary(itinerary)

def trackPlaces(places, names, storeMean, sessionId):
    # Track down the destinations for future recommendation algorithm
    if sessionId == session.get("session_id"):
        for i in range(len(places)):
            res = trackedPlacesCon.SetInfo(TrackedPlace(session["current_user"]["userId"], places[i], names[i], storeMean))
            return res
    
    return {"success": False, "error": "Your session is invalid. Please login again"}

@app.route("/funcs/post-places", methods=['POST'])
def recommendPlace():
    finalResult = {}
    trackPlaces(request.form.get("destinations"), request.form.get("storeMean"))

    return json.dumps(finalResult)


@app.route("/funcs/mark-tracked", methods=['POST'])
def markTracked():
    res = trackPlaces([request.form.get("address")], [request.form.get("name")], request.form.get("action"), request.form.get("sessionId"))
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
    app.run()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
