from os import urandom

from cs50 import SQL
from flask import Flask, flash, redirect, url_for, render_template, request, session
from flask_session import Session
from helpers import login_required, validate_credential
from werkzeug.security import generate_password_hash, check_password_hash

# Configure application
app = Flask(__name__)
app.secret_key = b"frango_frito_151413"

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


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        if session.get("user_id") is None:
            return render_template("register.html")
        else:
            return redirect(url_for("index"))
    else:
        email = str(request.form.get("email"))
        password = str(request.form.get("password"))
        confirmPassword = str(request.form.get("confirmPassword"))
        # Validate
        if not validate_credential(email, "email") or not validate_credential(password, "password") or not validate_credential(confirmPassword, "password"):
            flash("Fields must not be empty", "error")
            return redirect(url_for("register"))
        # Verify DB
        if db.execute("SELECT * FROM users WHERE email = ?", email):
            flash("User already registered", "error")
            return redirect(url_for("register"))
        # Validate
        if password != confirmPassword:
            flash("Passwords didn't match", "error")
            return redirect(url_for("register"))

        password = generate_password_hash(password)
        session_id = str(urandom(64))
        db.execute("INSERT INTO users (email, hash, session_id) VALUES (?, ?, ?)", email, password, session_id)
        if db.execute("SELECT * FROM users WHERE email = ?", email):
            flash("Successfully registered.", "success")
            return redirect(url_for("login"))
        else:
            flash("Something went wrong.. Try again!", "error")
            return redirect(url_for("register"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if session.get("user_id") is None:
            return render_template("login.html")
        else:
            return render_template("index.html")
    else:
        email = str(request.form.get("email"))
        password = str(request.form.get("password"))
        # Validate
        if not validate_credential(email, "email") or not validate_credential(password, "password"):
            flash("Fields must not be empty", "error")
            return redirect(url_for("login"))
        # Query
        query = db.execute("SELECT * FROM users WHERE email = ?", email)
        # Validate
        if not query:
            flash("User not found", "error")
            return redirect(url_for("login"))    
        elif check_password_hash(query[0]["hash"], password):
            # Login ok
            session["user_id"] = query[0]["session_id"]
            session["id"] = query[0]["user_id"]
            return redirect(url_for("index"))
        else:
            flash("Password didn't fit well...", "error")
            return redirect(url_for("login"))

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html")


@app.route("/games", methods=["GET", "POST"])
@login_required
def games():
    if request.method == "GET":
        id = session.get("id")
        games = db.execute("SELECT name, game, id FROM sheets WHERE user_id = ?", id)
        return render_template("games.html", games=games)
    else:
        character = request.form.get("characters")
        return str(character)