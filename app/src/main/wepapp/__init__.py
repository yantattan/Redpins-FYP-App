from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_socketio import SocketIO, emit
from datetime import datetime, timedelta, date
import DbContext
from Model import *
from controllers import *
import pandas
import geocoder
import requests
import random
import json
from controllers.TrackedPlaces import TrackedPlacesCon
from controllers.Users import UserCon

app = Flask(__name__)
app.secret_key = "redp1n5Buffer"

# Init all controllers
userCon = UserCon()
trackedPlacesCon = TrackedPlacesCon()


def initOneMapAPI(yourLocation):
    address = "336B street Geylang St 69"
    
    # Append address and get the coordinates of the location
    location = ",".join([str(x) for x in yourLocation])
    today = datetime.today()
    print(location)
    routingJson = requests.get("https://developers.onemap.sg/privateapi/routingsvc/route?"
                               "start=" + location + "&"
                               "end=1.319728905,103.8421581&"
                               "routeType=drive&"
                               "token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOjg1NDQsInVzZXJfaWQiOjg1NDQsImVtYWlsIjoieWFudGF0dGFuNzIxQGdtYWlsLmNvbSIsImZvcmV2ZXIiOmZhbHNlLCJpc3MiOiJodHRwOlwvXC9vbTIuZGZlLm9uZW1hcC5zZ1wvYXBpXC92MlwvdXNlclwvc2Vzc2lvbiIsImlhdCI6MTY0NzQxMTA0NSwiZXhwIjoxNjQ3ODQzMDQ1LCJuYmYiOjE2NDc0MTEwNDUsImp0aSI6ImJjNTBmNzFlOWZmOTYyMWE3NThiNjRkOGE0OGFiMTk0In0.lSAYegznUtlA36wrOkIMVNWTvOUzkxIh7KdjLwO6FbM&"
                               "date="+ today.strftime("%Y-%m-%d") +"&"
                               "time="+ today.strftime("%H:%M:%S") +"&"
                               "mode=TRANSIT")
    resultsdict = json.loads(routingJson.text)
    print(json.dumps(resultsdict, indent=4))
    # if len(resultsdict['results']) > 0:
    #     return resultsdict['results'][0]['LATITUDE'], resultsdict['results'][0]['LONGITUDE']
    # else:
    #     pass


# Functions to perform before showing the page
@app.route("/", methods=['GET', 'POST'])
def mainPage():
    # To render the page (pathing starts from templates folder after). After the filename, variables defined behind are
    # data that the site needs to use
    yourLocation = geocoder.ip("me")
    print(yourLocation.latlng)
    if request.method == 'POST':
        initOneMapAPI(yourLocation.latlng)
        return redirect("/")
    # For functions to perform before loading of site
    else:
        initOneMapAPI(yourLocation.latlng)
        if session.get("current_user") is None:
            return redirect("/login")

        yourLocation = geocoder.ipinfo("")
        print(yourLocation.latlng)
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
            session["current_user"] = userInfo
            return redirect("/")

        return render_template("accounts/login.html", form=login_form, error="Invalid username or password")

    return render_template("accounts/login.html", form=login_form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    register_form = RegisterForm(request.form)
    if request.method == 'POST':
        if register_form.validate():
            userModel = User(register_form.username.data, register_form.email.data, register_form.contact.data, register_form.password.data)
            registerResponse = userCon.Register(userModel)
            if registerResponse.get("error"):
                return render_template("accounts/register.html", form=register_form, error=registerResponse["error"])
            else:
                return redirect("/login")

        return render_template("accounts/register.html", form=register_form, error="Invalid fields submitted")

    return render_template("accounts/register.html", form=register_form)

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
