from os import urandom

from cs50 import SQL
from flask import Flask, flash, redirect, url_for, render_template, request, session
from flask_session import Session
from helpers import login_required, validate_credential
from werkzeug.security import generate_password_hash, check_password_hash


# Configure application
app = Flask(__name__)
app.secret_key = ""

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
        

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")
