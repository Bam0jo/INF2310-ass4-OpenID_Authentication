import identity.web
import requests
import os
from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
import secrets

# The following variables are required for the app to run.

# TODO: Use the Azure portal to register your application and generate client id and secret credentials.
CLIENT_ID = "9a1c42ac-ad9f-4a8e-bc90-e4cd9463fdae"
CLIENT_SECRET = "SGP8Q~sagCLHR6AWbVPHMz6kezZC9DhISwREcdc7"

# TODO: Figure out your authentication authority id.
AUTHORITY = "https://login.microsoftonline.com/0cff9966-b3c0-4a41-9874-3c22e287ab4c"


# TODO: generate a secret. Used by flask session for protecting cookies.
superSecret = secrets.token_hex(16)
SESSION_SECRET = superSecret

# TODO: Figure out what scopes you need to use
SCOPES = ["User.Read","User.ReadBasic.All","User.ReadWrite"] 

# TODO: Figure out the URO where Azure will redirect to after authentication. After deployment, this should
#  be on your server. The URI must match one you have configured in your application registration.
REDIRECT_URI = "http://localhost:5000/getAToken"


REDIRECT_PATH = "/getAToken"










app = Flask(__name__)

app.config['SECRET_KEY'] = SESSION_SECRET
app.config['SESSION_TYPE'] = 'filesystem'
app.config['TESTING'] = True
app.config['DEBUG'] = True
Session(app)

# The auth object provide methods for interacting with the Microsoft OpenID service.
auth = identity.web.Auth(session=session,
                         authority=AUTHORITY,
                         client_id=CLIENT_ID,
                         client_credential=CLIENT_SECRET)





######################################################################
#                          Unsure if needed                          #
######################################################################


from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


######################################################################






@app.route("/login")
def login():
    # TODO: Use the auth object to log in.
    
    loginStuff = auth.log_in(
        scopes=SCOPES, 
        redirect_uri=REDIRECT_URI,
        prompt="select_account"
    )
    
    response = loginStuff
    return render_template("login.html", **response)


@app.route(REDIRECT_PATH)
def auth_response():
    # TODO: Use the flask request object 
    # and auth object to complete the authentication.

    completeStuff = auth.complete_log_in(request.args)
    # print(f"COMPLETE STUFF:   {completeStuff}")

    if "error" in completeStuff:
        return render_template("auth_error.html",result=completeStuff)
    return redirect("/")




@app.route("/logout")
def logout():
    # TODO: Use the auth object to log out and redirect to the home page
    
    return redirect(auth.log_out(url_for("index", _external=True)))




@app.route("/")
def index():
    # TODO: use the auth object to get the profile of the logged in user.

    if not auth.get_user():
        return redirect("/login")
    
    return render_template('index.html', user=auth.get_user())








@app.route("/profile", methods=["GET"])
def get_profile():

    # TODO: Check that the user is logged in and add credentials to the http request.
    if not auth.get_user():
        return redirect("/login")
    
    token = auth.get_token_for_user(SCOPES)

    result = requests.get(
        'https://graph.microsoft.com/v1.0/me',
        headers={'Authorization': 'Bearer ' + token['access_token']}
    )

    # print(f"TOKEN:  {token}")
    print(f"GET USER: {auth.get_user()}")

    return render_template('profile.html', 
                           user=result.json(), 
                           result=result)




@app.route("/profile", methods=["POST"])
def post_profile():

    # TODO: check that the user is logged in and add credentials to the http request.
    if not auth.get_user():
        return redirect("/login")

    token = auth.get_token_for_user(SCOPES)
    result = requests.patch(
        'https://graph.microsoft.com/v1.0/users/' + request.form.get("id"),
        json=request.form.to_dict(),
        headers={'Authorization': 'Bearer ' + token['access_token']}
    )
    
    # TODO: add credentials to the http request.
    profile = requests.get(
        'https://graph.microsoft.com/v1.0/me',
        headers={'Authorization': 'Bearer ' + token['access_token']}
    )
    return render_template('profile.html',
                           user=profile.json(),
                           result=result)





@app.route("/users")
def get_users():
    # TODO: Check that user is logged in and add credentials to the request.

    if not auth.get_user():
        return redirect("/login")


    token = auth.get_token_for_user(SCOPES)
    result = requests.get(
        'https://graph.microsoft.com/v1.0/users',
        headers={'Authorization': 'Bearer ' + token['access_token']}
    )
    return render_template('users.html', result=result.json())


if __name__ == "__main__":
    app.run()
