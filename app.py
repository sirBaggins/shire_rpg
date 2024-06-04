from cs50 import SQL
from flask import Flask, flash, redirect, url_for, render_template, request, session
from flask_session import Session
from helpers import login_required, validate_credential
from werkzeug.security import generate_password_hash, check_password_hash

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config.from_object(__name__)
Session(app)

# Database link
db = SQL("sqlite:///shire.db")

# INDEX
@app.route("/")
def index():
        return render_template("index.html")
