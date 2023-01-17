from flask import Flask, render_template, g, redirect, url_for, Response, jsonify, request, abort
from flask_oidc import OpenIDConnect
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from okta import UsersClient
import config

from sqlalchemy.orm import Session


app = Flask(__name__)
app.config["OIDC_CLIENT_SECRETS"] = 
app.config["OIDC_COOKIE_SECURE"] = False
app.config["OIDC_CALLBACK_ROUTE"] = "/oidc/callback"
app.config["OIDC_SCOPES"] = ["openid", "email", "profile"]
app.config["SECRET_KEY"] = "{{ LONG_RANDOM_STRING }}"
app.config["OIDC_ID_TOKEN_COOKIE_NAME"] = "oidc_token"
oidc = OpenIDConnect(app)
okta_client = UsersClient("https://vivapoc.okta.com", "")

CORS(app, resources={r"/*": {"origin": "*"}})

app.config.from_object(config)
db = SQLAlchemy()
migrate = Migrate()

#ORM
db.init_app(app)
migrate.init_app(app, db)
import models
from models import OktaUser

#
# @app.before_request
# def before_request():
#     if oidc.user_loggedin:
#         g.user = okta_client.get_user(oidc.user_getfield("sub"))
#     else:
#         g.user = None

trusted_proxies = ('127.0.0.1')

@app.before_request
def limit_remote_addr():
    remote = request.remote_addr
    print(remote, 'remote')
    print(request.headers.getlist('X-Forwarded-For'), 'xff')

    if remote not in trusted_proxies:
        abort(403)  # Forbidden


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
@oidc.require_login
def dashboard():
    return render_template("dashboard.html")


@app.route("/login/<sessionID>")
@oidc.require_login
def login(sessionID):
    if oidc.user_loggedin:
        g.user = okta_client.get_user(oidc.user_getfield("sub"))
    else:
        g.user = None
    q = OktaUser(sessionID=sessionID, username=g.user.profile.firstName)
    db.session.add(q)
    db.session.commit()
    return render_template("out.html")
    # return redirect("http://localhost:5173/")
    # return redirect(url_for('dashboard'))

@app.route("/auth/<sessionID>")
# @oidc.require_login
def auth(sessionID):
    try:
        q = OktaUser.query.filter(OktaUser.sessionID == sessionID).first()
        return {
            "username": q.username
        }
    except:
        abort(404)

