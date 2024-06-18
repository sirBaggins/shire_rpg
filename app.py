from os import urandom

from cs50 import SQL
from flask import Flask, flash, redirect, url_for, render_template, request, session
from flask_session import Session
from flask_mail import Mail, Message
from helpers import login_required, validate_credential
from random import randint
from werkzeug.security import generate_password_hash, check_password_hash


# Database link
db = SQL("sqlite:///shire.db")

# Configure application
app = Flask(__name__)
app.secret_key = ""

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config.from_object(__name__)
Session(app)

# Configure mail
app.config["MAIL_SERVER"] = ""
app.config["MAIL_PORT"] = ""
app.config["MAIL_USERNAME"] = ""
app.config["MAIL_PASSWORD"] = ""
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_DEFAULT_SENDER"] = ("Shire_RPG", "")
mail = Mail(app)

# EMAIL
def send(user, key):
    message = Message(
        subject="Shire_RPG password recovery",
        recipients=[user],
    )
    message.body = "Did you forget your Shire_RPG password? It's been reset to " + key
    mail.send(message)
    return redirect(url_for("login"))

# INDEX
@app.route("/")
def index():
    return render_template("index.html")

# REGISTER
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

# LOGIN
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

# LOGOUT
@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("index"))

# SETTINGS
@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "GET":
        return render_template("settings.html")
    else:
        actual = request.form.get("actual")
        newPassword = request.form.get("password")
        confirmPassword = request.form.get("confirmPassword")

        if not validate_credential(actual, "password") or not validate_credential(newPassword, "password") or not validate_credential(confirmPassword, "password"):
            flash("fields may not be empty", "error")
            return redirect(url_for("settings"))
        
        hash = db.execute("SELECT hash FROM users WHERE user_id = ?", session["id"])
        if not check_password_hash(hash[0]["hash"], actual):
            flash("actual password didn't fit well", "error")
            return redirect(url_for("settings"))
        else:
            hash = generate_password_hash(newPassword)
            db.execute("UPDATE users SET hash=? WHERE user_id = ?", hash, session["id"])
        
        flash("DONE", "success")
        return redirect(url_for("settings"))


# SHEETS
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
    
# CREATE
@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "GET":
        return render_template("create.html")
    else:
        if request.form.get("btn") == "start":
            name = request.form.get("name")
            game = request.form.get("game")
            if not name or not game:
                flash("fields cannot be empty", "error")
                return redirect(url_for("create"))

            query = db.execute("SELECT id FROM sheets WHERE name = ? AND game = ? AND user_id = ?", name, game, session["id"])
            if query:
                flash("Character already exists", "error")
                return redirect(url_for("create"))
            else:
                db.execute("INSERT INTO sheets (user_id, name, game) VALUES (?, ?, ?)", session["id"], name, game)
                query = db.execute("SELECT * FROM sheets WHERE user_id = ? AND name = ? AND game = ?", session["id"], name, game)
                # Insert into game_data
                db.execute("INSERT INTO game_data (sheet_id, attribute, value, type) VALUES (?, ?, ?, ?)", query[0]["id"], "name", name, "basic")
                db.execute("INSERT INTO game_data (sheet_id, attribute, value, type) VALUES (?, ?, ?, ?)", query[0]["id"], "game", game, "basic")
                return redirect(url_for("games"))
        else:
            return redirect(url_for("create"))    

# CREATE SHEET
@app.route("/create1", methods=["GET", "POST"])
@login_required
def create1():
    id = request.args.get("id")

    if request.method == "GET":
        if not id:
            return redirect(url_for("games"))

        else:
            test = db.execute("SELECT user_id FROM sheets WHERE id = ?", id)
            if not test:
                return redirect(url_for("games"))
            else:
                if not test[0]["user_id"] == session["id"]:
                    return redirect(url_for("games"))
                else:
                    data = db.execute("SELECT * FROM game_data WHERE sheet_id = ?", id)
                    return render_template("create_content.html", data=data)
                    
    else:
        if request.form.get("btn") == "insert":
                attribute = request.form.get("attribute")
                value = request.form.get("value")
                id = request.form.get("sheet_id")
                _type = request.form.get("type")

                if not attribute or not value or not id or not _type:
                    flash("fields cannot be empty", "error")
                    return redirect(url_for("games"))
                
                test = db.execute("SELECT user_id FROM sheets WHERE id = ?", id)
                if test[0]["user_id"] == session["id"]:
                    if not db.execute("SELECT 1 FROM game_data WHERE sheet_id = ? AND attribute = ?", id, attribute):
                        db.execute("INSERT INTO game_data (sheet_id, attribute, value, type) VALUES (?, ?, ?, ?)", id, attribute, value, _type)
                        return redirect(url_for("create1") + "?id=" + id)
                    else:
                        db.execute("UPDATE game_data SET value=? WHERE sheet_id=? AND attribute=?", value, id, attribute)
                        return redirect(url_for("create1") + "?id=" + id)
                else:
                    flash("Forbbiden", "error")
                    return redirect(url_for("games"))

        elif request.form.get("btn") == "remove":
            attribute = request.form.get("attribute")
            id = request.form.get("sheet_id")

            if not attribute or not id:
                flash("attribute cannot be empty", "error")
                redirect(url_for("games"))

            test = db.execute("SELECT user_id FROM sheets WHERE id = ?", id)
            if test[0]["user_id"] == session["id"]:
                if db.execute("SELECT 1 FROM game_data WHERE sheet_id = ? AND attribute = ?", id, attribute):
                    db.execute("DELETE FROM game_data WHERE sheet_id = ? AND attribute = ?", id, attribute)
                    return redirect(url_for("create1") + "?id=" + id) # type: ignore
                else:
                    return redirect(url_for("create1") + "?id=" + id) # type: ignore
            else:
                return redirect(url_for("games"))

        else:
            flash("wrong post", "error")
            return redirect(url_for("create1"))

# DELETE SHEET
@app.route("/delete_sheet", methods=["GET", "POST"])
@login_required
def delete_sheet():
    id = request.args.get("id")
    if not id:
        return redirect(url_for("games"))

    else:
        if db.execute("SELECT 1 FROM sheets WHERE id = ? AND user_id = ?", id, session["id"]):
            db.execute("DELETE FROM sheets WHERE id = ? AND user_id = ?", id, session["id"])
            db.execute("DELETE FROM game_data WHERE sheet_id = ?", id)
            return redirect(url_for("games"))
        else:
            return redirect(url_for("games"))

# RENDER SHEET
@app.route("/sheet/<id>")
def render_sheet(id):
    if not id:
        return redirect(url_for("games"))
    else:
        if db.execute("SELECT 1 FROM sheets WHERE id = ? AND user_id = ?", id, session["id"]):
            query = db.execute("SELECT * FROM game_data WHERE sheet_id = ?", id)
            return render_template("sheet.html", data=query)
        else:
            return redirect(url_for("games"))
        
# HANDLE 404
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")

# ABOUT
@app.route("/about")
def about():
        return render_template("about.html")
   
# RESET PASSWORD
@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "GET":
        return render_template("reset_password.html")
    else:
        email = request.form.get("email")
        if not validate_credential(email, "email"):
            flash("email couldn't sneak in...", "error")
            return redirect(url_for("reset_password"))
        elif not db.execute("SELECT email FROM users WHERE email = ?", email):
            flash("email couldn't sneak in...", "error")
            return redirect(url_for("reset_password"))
        
        else:
            fresh_password = []
            for i in range(8):
                fresh_password.append(str(randint(0, 9)))
            settled = "".join(fresh_password)
            settled_hash = generate_password_hash(settled)

            db.execute("UPDATE users SET hash=? WHERE email = ?", settled_hash, email)
            send(email, settled)

            flash("Password reseted. Check spam folder.", "success")
            return redirect(url_for("login"))
