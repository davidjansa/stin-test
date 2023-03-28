from flask import Blueprint, render_template, redirect, url_for, request, session
import random
from .objects import BankAccount, Transaction
from . import account_db, transaction_db, exchange_db, ggemail, ggpass
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from bson import ObjectId
import urllib

routes = Blueprint("routes", __name__)

# LOGIN

@routes.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

@routes.route("/login_send_code", methods=["POST"])
def login_send_code():
    form_email = request.form.get("email_input")
    form_password = request.form.get("password_input")

    # find account in db
    ac = account_db.find_one({"email": form_email})

    # verify account
    if ac is not None:
        ba = BankAccount(ac["firstname"], ac["surname"], ac["password"], ac["email"], ac["bid"])
        if ba.check_password(form_password):
            code = f"{random.randint(1111,9999)}"
            send_code(ba.email, code)
            session["code"] = code
    
    return render_template("login.html")

def send_code(email : str, code : str):
    msg = MIMEText(f"Here is your 2pa code: {code}")
    msg["Subject"] = "STONKSTER code authorization"
    msg["From"] = ggemail
    msg["To"] = email
    smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    smtp_server.login(ggemail, ggpass)
    smtp_server.sendmail(ggemail, email, msg.as_string())
    smtp_server.quit()

@routes.route("/login_login", methods=["POST"])
def login_login():
    form_email = request.form.get("email_input")
    form_password = request.form.get("password_input")
    form_code = request.form.get("code_input")

    # find account in db
    ac = account_db.find_one({"email": form_email})

    # verify account
    if ac is not None:
        ba = BankAccount(ac["firstname"], ac["surname"], ac["password"], ac["email"], ac["bid"])
        if ba.check_password(form_password) and form_code == session["code"]:
            session.clear()
            session["ba"] = {
                "bid" : ba.bid,
                "name": f"{ba.firstname} {ba.surname}"
            }
            # download data
            exchange_download()

            return redirect(url_for("routes.index"))
    
    render_template("login.html")

# INDEX

@routes.route('/')
@routes.route("/index", methods=["GET"])
def index():
    if session.get("ba", None) == None:
        return redirect(url_for("routes.login_page"))
    else: return render_template("index.html")

@routes.route("/send_transaction", methods=["POST"])
def send_transaction():
    form_tobid = request.form.get("tobid_input")
    form_curr = request.form.get("curr_input")
    form_amount = request.form.get("amount_input")


    
    return render_template("index.html")

@routes.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("routes.login_page"))

# CNB DOWNLOAD
def exchange_download() -> None:
    today = datetime.now().strftime("%d.%m.%Y")
    url = f"https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt?date={today}"
    data = urllib.request.urlopen(url).read().decode()
    lines = data.split('\n')
    # date
    date = datetime.strptime(lines[0].split(' ')[0], "%d.%m.%Y")

    # same document check (date)
    prev_doc = exchange_db.find_one({"_id": ObjectId("6421fb6fe6e010756d82f2a1")})
    if prev_doc["date"] == date:
        return

    # result dict (document)
    d = {
        "date": date,
        "currency-rates": dict()
    }
    # parse data
    for curr in lines[2:-2]:
        curr_data = curr.split('|')
        curr_code = curr_data[3]
        curr_amount = int(curr_data[2])
        curr_rate = float(curr_data[4].replace(',','.'))
        d["currency-rates"][curr_code] = curr_rate / curr_amount
    
    # send data to db
    exchange_db.insert_one(d)