import os
from re import compile, fullmatch
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *

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
        
# EMAIL
def send(user, key) -> None:
    
    sg = SendGridAPIClient(api_key='')
    from_email = Email("setor.yabg@outlook.com")
    to_email = To(user)
    subject = "Shire_RPG password recovery"
    content = Content("text/plain", "Your new password is: " + key)
    mail = Mail(from_email, to_email, subject, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)
    return