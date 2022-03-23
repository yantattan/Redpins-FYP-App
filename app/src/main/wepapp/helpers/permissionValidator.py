from flask import Flask, request, redirect, url_for, session


def validateLoggedIn():
    if session.get("current_user") is None:
        return redirect("/login")

    
def validateAdmin():
    validateLoggedIn()
    if session["current_user"].get("role") != "Admin":
        return redirect("/login")

