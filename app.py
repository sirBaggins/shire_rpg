from cs50 import SQL
from flask import Flask, flash, redirect, url_for, render_template, request, session
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import login_required, validate_credential

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config.from_object(__name__)
Session(app)

# DATABASE LINK
db = SQL("sqlite:///shire.db")

# FUNCTIONS!!
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# INDEX
@app.route("/")
def index():
    return render_template("index.html")

#  REGISTER
@app.route("/register/", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        return "post register"

# LOGIN
@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        return "post login"

# LOGOUT
@app.route("/logout/")
@login_required
def logout():
    session.clear()
    return redirect("/")






# RENDER_SHEET
@app.route("/player/<sheet_id>/", methods=["GET"])
@login_required
def render_sheet(sheet_id):
    return sheet_id
