from re import match
from flask import redirect, render_template, request, session
from functools import wraps


# CONSTANTS
EMAIL_PATTERN = r"^[\w\.-]+@[\w\.-]+\.\w+$"

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
            if not match(EMAIL_PATTERN, credential):
                return False
            else:
                return True
        case _:
            return False
