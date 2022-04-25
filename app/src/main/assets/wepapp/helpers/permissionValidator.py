from flask import session


def validateSession():
    if session.get("current_user") is None:
        return "/login"

def validateLoggedIn():
    invalidRedirect = validateSession()
    if invalidRedirect is not None:
        return invalidRedirect

    if not session["current_user"].get("setupComplete"):
        return "/preferences/1"
    
def validateAdmin():
    validateLoggedIn()
    if session["current_user"].get("role") != "Admin":
        return "/"

def validatePlaceAdmin():
    invalidRedirect = validateLoggedIn()
    if invalidRedirect is not None:
        return invalidRedirect

    if session["current_user"].get("role") != "Place Admin":
        return "/"

