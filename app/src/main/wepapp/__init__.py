from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import timedelta, date
from Model import *
from controllers import *
import pandas
import geocoder
import requests
import random

# from controllers.Users import UserCon


app = Flask(__name__)
app.secret_key = "redp1n5Buffer"

#Init all controllers
# userCon = UserCon()


def initOneMapAPI():
    df = {
        "Address": "",
        "blk_no": "336B",
        "street": "Geylang St 69"
    }
    df['Address'] = df['blk_no'] + " " + df['street']

    # Append address and get the coordinates of the location
    routingJson = requests.get("https://developers.onemap.sg/privateapi/routingsvc/route?"
                               "start=1.319728,103.8421&"
                               "end=1.319728905,103.8421581&"
                               "routeType=walk&"
                               "token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOjg1NDQsInVzZXJfaWQiOjg1NDQsImVtYWlsIjoieWFudGF0dGFuNzIxQGdtYWlsLmNvbSIsImZvcmV2ZXIiOmZhbHNlLCJpc3MiOiJodHRwOlwvXC9vbTIuZGZlLm9uZW1hcC5zZ1wvYXBpXC92MlwvdXNlclwvc2Vzc2lvbiIsImlhdCI6MTY0NjgxNDMxNywiZXhwIjoxNjQ3MjQ2MzE3LCJuYmYiOjE2NDY4MTQzMTcsImp0aSI6IjE4ZWI2MDVmYzU2MGU5YzcwZGY0MjEyNDMxN2I1MzM5In0.GsQO_VeKSFiw0gJbJENmhnM1obpN-KxVcGw1C2PUw8g")
    resultsdict = eval(routingJson.text)
    print(resultsdict)
    # if len(resultsdict['results']) > 0:
    #     return resultsdict['results'][0]['LATITUDE'], resultsdict['results'][0]['LONGITUDE']
    # else:
    #     pass


# Functions to perform before showing the page
@app.route("/")
def mainPage_get():
    yourLocation = geocoder.ip("me")
    initOneMapAPI()
    return render_template("main.html", locationCoords=",".join("%.11f" %coord for coord in yourLocation.latlng), y="Meh")


# Functions to perform after submitting information
@app.route("/", methods=['GET', 'POST'])
def mainPage_post():
    #To render the page (pathing starts from templates folder after). After the filename, variables defined behind are
    #data that the site needs to use
    initOneMapAPI()
    return redirect("/")



@app.route("/login")
def login_get():
    #To render the page (pathing starts from templates folder after). After the filename, variables defined behind are
    #data that the site needs to use
    return render_template("login.html")


@app.route("/login", methods=['GET', 'POST'])
def login_post():
    #To render the page (pathing starts from templates folder after). After the filename, variables defined behind are
    #data that the site needs to use
    login_form = User(request.form)

    # if request.method == 'POST' and login_form.validate():
    #     userCon.Login(login_form)
    return redirect("/")


#Form submit methods starts here
@app.route("/", methods=['GET', 'POST'])
def formSubmit():
    sample_form = SampleForm(request.form)
    if request.method == 'POST' and sample_form.validate():
        #Operations starts here
        x = 0
    return redirect("/")


if __name__ == '__main__':
    app.run()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
