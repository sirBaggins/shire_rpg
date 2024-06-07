from re import compile, fullmatch

from cs50 import SQL
from flask import redirect, request, session, redirect
from functools import wraps


# CONSTANTS
EMAIL_PATTERN = compile(r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+")

# REQUIRE LOGIN
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# VALIDATE CREDENTIAL
def validate_credential(credential, type):
    # refuse null
    if not credential:
        return False
    # pattern verifier
    match type:
        case "username":
            if len(credential) < 4 or len(credential) > 20:
                return False
            else:
                return True        
        case "password":
            if len(credential) < 8 or len(credential) > 16:
                return False
            else:
                return True
        case "email":
            if not fullmatch(EMAIL_PATTERN, credential):
                return False
            else:
                return True
        case _:
            raise ValueError("Invalid type", type)
        

