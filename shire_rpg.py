from flask import Flask, flash, redirect, url_for, render_template, request, session
from flask_session import Session


# Configure application
app = Flask(__name__)
app.secret_key = b"frango_frito_151413"

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config.from_object(__name__)
Session(app)
