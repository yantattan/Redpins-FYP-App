from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import timedelta, date
from Model import *
from controllers import *
import shelve
import random

# from controllers.Users import UserCon


app = Flask(__name__)
app.secret_key = "redp1n5Buffer"

#Init all controllers
# userCon = UserCon()


#For every different pages
@app.route("/")
def mainPage():
    #To render the page (pathing starts from templates folder after). After the filename, variables defined behind are
    #data that the site needs to use
    print("Hello world")
    return render_template("main.html", x="I am x", y="Meh")


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
