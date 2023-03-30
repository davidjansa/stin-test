from flask import Blueprint, render_template, redirect, url_for, request, session, flash, get_flashed_messages
import random
from .objects import BankAccount, TransactionList, CurrencyBalance
from . import account_db, balance_db, transaction_db, exchange_db, ggemail, ggpass, main_currency
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from bson import ObjectId
import urllib

routes = Blueprint("routes", __name__)

# LOGIN

@routes.route("/login", methods=["GET"])
def login_page():
    """route for rendering login.html page

    Returns:
        str: render login.html page
    """
    return render_template("login.html")

@routes.route("/login_send_code", methods=["POST"])
def login_send_code():
    """route for sending 2 phase authorization code to inserted e-mail

    Returns:
        str: render login.html page
    """
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
    
    return redirect(url_for("routes.login_page"))

def send_code(email : str, code : str):
    """send generated code to e-mail

    Args:
        email (str): e-mail where the code should be sended
        code (str): code
    """
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
    """route for logging in the bank account

    Returns:
        str: if account exists -> redirect to routes.index else render login.html 
    """
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

            # bank account
            session["ba"] = {
                "bid" : ba.bid,
                "name": f"{ba.firstname} {ba.surname}",
                "currency-balance": {},
                "transaction-list": []
            }

            # refresh data
            refresh_account_data()

            # load currencies
            refresh_exchange_data()

            # download data
            exchange_download()

            return redirect(url_for("routes.index"))
    
    return redirect(url_for("routes.login_page"))

# INDEX

@routes.route('/')
@routes.route("/index", methods=["GET"])
def index():
    """route for rendering index.html page

    Returns:
        str: if bank account is in session -> rendex index.html page else redirect to routes.login_page
    """
    if session.get("ba", None) == None:
        return redirect(url_for("routes.login_page"))
    else: 
        return render_template("index.html")

@routes.route("/send_transaction", methods=["POST"])
def send_transaction():
    """route for sending transaction

    Returns:
        str: if any of the inserted data is None or invalid -> flash message and render index.html
        else make transition, flash message and render index.html
    """
    # target bid
    form_tobid = request.form.get("tobid_input")
    if form_tobid is None:
        flash("Error in 'to bid' input.")
        return redirect(url_for("routes.index"))
    # find bid in database
    if  account_db.find_one({"bid": form_tobid}) is None and form_tobid != "9999":
        flash(f"Target account ({form_tobid}) does not exist.")
        return redirect(url_for("routes.index"))

    # currency
    form_curr = request.form.get("curr_input")
    if form_curr is None:
        flash("Error in 'currency' input.")
        return redirect(url_for("routes.index"))
    form_curr = form_curr.upper()
    # check if currency exists in db
    if exchange_db.find_one({"_id": ObjectId("6421fb6fe6e010756d82f2a1")})["currency-rates"].get(form_curr, None) is None and form_curr != main_currency:
        flash(f"Inserted currency ({form_curr}) does not exist in database.")
        return redirect(url_for("routes.index"))
    
    # amount
    try:
        form_amount = float(request.form.get("amount_input"))
    except ValueError:
        form_amount = None
    if form_amount is None:
        flash("Error in 'amount' input.")
        return redirect(url_for("routes.index"))
    
    # primary transfer
    form_transfer = bool(request.form.get("trans_input"))
    
    # make transaction via inserted currency
    if make_transaction(session["ba"]["bid"], form_tobid, form_curr, form_amount, form_transfer):
        flash("The transaction was successful.")
        return redirect(url_for("routes.index"))
        
    flash("You do not have enough resources.")
    return redirect(url_for("routes.index"))

@routes.route("/logout", methods=["POST"])
def logout():
    """route for logout
    clear session and redirect back to login page

    Returns:
        str: redirect to routes.login_page
    """
    session.clear()
    return redirect(url_for("routes.login_page"))

# CNB DOWNLOAD
def exchange_download() -> None:
    """download exchange rates from CNB and save it in the database
    if the file with the same date is in database -> do not save it
    """
    today = datetime.now().strftime("%d.%m.%Y")
    url = f"https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt?date={today}"
    try:
        data = urllib.request.urlopen(url).read().decode()
    except:
        return
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
    exchange_db.update_one({"_id": ObjectId("6421fb6fe6e010756d82f2a1")}, {"$set": {"date": d["date"], "currency-rates": d["currency-rates"]}})

def refresh_exchange_data():
    """get exchange rate data from database and save it in session
    """
    session["curr-codes"] = list()
    exchange = exchange_db.find_one({"_id": ObjectId("6421fb6fe6e010756d82f2a1")})["currency-rates"]
    for key in exchange.keys():
        session["curr-codes"].append(key)

# GET DATA FROM DB
def refresh_account_data() -> None:
    """refresh account data - load data from database into session
    """
    ba = session.get("ba", None)
    if ba is None:
        return
    
    balance = balance_db.find_one({"bid": ba["bid"]})
    if balance != session["ba"]["currency-balance"] and balance:
        session["ba"]["currency-balance"] = CurrencyBalance(balance["currency-balance"]).to_output()
    
    transaction = transaction_db.find_one({"bid": ba["bid"]})
    if transaction != session["ba"]["transaction-list"] and transaction:
        session["ba"]["transaction-list"] = TransactionList(transaction["transaction-list"]).to_output()

def make_transaction(bid : str, target_bid : str, currency : str, amount : float, use_main_currency : bool = False) -> bool:
    """accomplish transaction -> update databse

    Args:
        bid (str): bank account id (sending)
        target_bid (str): bank accoutn id (target)
        currency (str): currency
        amount (float): amount
        use_main_currency (bool, optional): True -> if not enough resources in inserted currency -> use main currency (exchanged). Defaults to False.

    Returns:
        bool: if transaction is accomplished -> True else False
    """
    res = False
    # account balance
    balance = balance_db.find_one({"bid": bid})
    transaction = None
    # insert money
    if balance:
        if bid == target_bid:
            # check if account has inserted currency
            if balance["currency-balance"].get(currency, None):
                balance_db.update_one({"bid": bid}, {"$inc": {f"currency-balance.{currency}": amount}})
            else:
                balance_db.update_one({"bid": bid}, {"$set": {f"currency-balance.{currency}": amount}})
            # add to transaction db
            transaction_db.update_one({"bid": bid}, {"$push": {"transaction-list": {"target-bid": bid, "currency-code": currency, "amount": f"+{amount:.2f}", "date": datetime.now()}}})
            res = True
        # send money
        else:
            # check if account has inserted currency
            if balance["currency-balance"].get(currency, None):
                # check if selected currency has enough resources
                if balance["currency-balance"][currency] >= amount:
                    balance_db.update_one({"bid": bid}, {"$inc": {f"currency-balance.{currency}": -amount}})
                    transaction_db.update_one({"bid": bid}, {"$push": {"transaction-list": {"target-bid": target_bid, "currency-code": currency, "amount": f"-{amount:.2f}", "date": datetime.now()}}})
                    res = True
            # use main currency 
            if use_main_currency and not res:
                exchanged_amount = amount * exchange_db.find_one({"_id": ObjectId("6421fb6fe6e010756d82f2a1")})["currency-rates"][currency]
                if balance["currency-balance"][main_currency] >= exchanged_amount:
                    balance_db.update_one({"bid": bid}, {"$inc": {f"currency-balance.{main_currency}": -exchanged_amount}})
                    transaction_db.update_one({"bid": bid}, {"$push": {"transaction-list": {"target-bid": target_bid, "currency-code": main_currency, "amount": f"-{exchanged_amount:.2f}", "date": datetime.now()}}})
                    res = True

    # if changed -> refresh data
    if res:
        refresh_account_data()

    return res