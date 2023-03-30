import pytest
from flask import session
from web import create_app, account_db
from web.objects import BankAccount, TransactionList, CurrencyBalance
from werkzeug.security import generate_password_hash
from datetime import datetime

# FIXTURES ---------------------------------------------------

@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    yield app

@pytest.fixture()
def client(app):
    with app.test_client() as client:
        return client
    
@pytest.fixture()
def ba_test():
    return {
            "bid": "TEST",
            "name": "test",
            "currency-balance": {
                "CZK": "0"
            },
            "transaction-list": [
                {"target-bid": "test", "currency-code": "test", "amount": "test", "date": "test"}
            ]
        }

# TESTS ------------------------------------------------------
    
# login and logout

def test_get_login_page_valid(client):
    """test valid http get request to /login route"""
    response = client.get("/login")
    assert response.request.path == "/login"
    
def test_get_login_page_after_logout_valid(client):
    """test valid http post request to /logout route - should redirect to /login route"""
    response = client.post("/logout", follow_redirects=True)
    assert response.request.path == "/login"
    
def test_login_login_page_invalid(client):
    """test invaid http post request to /login_login route without valid data - should return login page title"""    
    response = client.post("/login_login", data={}, follow_redirects=True)
    assert "WELCOME TO STONKSTER" in response.get_data(as_text=True)
    
def test_login_login_page_valid(client):
    """test valid http post request to /login_login route with valid data - should redirect to /index route"""
    form_data = {
        "email_input": "test@test.com",
        "password_input": "test",
        "code_input": "1111"
    }
    
    with client.session_transaction() as session:
        session["code"] = "1111"
    
    response = client.post("/login_login", data=form_data, follow_redirects=True)
    
    assert response.request.path == "/index"    
    
    
def test_login_send_code_invalid_email(client):
    """test invalid http post request to /login_send_code route without valid e-mail - should return login page title"""
    form_data = {
        "email_input": "invalid_email",
        "password_input": "test"
    }
    response = client.post("login_send_code", data=form_data, follow_redirects=True)
    
    assert "WELCOME TO STONKSTER" in response.get_data(as_text=True)

# index

def test_get_index_page_without_session_invalid(client):
    """test invalid http get request to /index route without valid session - should redirect to /login route"""
    response = client.get("/index", follow_redirects=True)
    assert response.request.path == "/login"
    
def test_get_index_page_with_session_valid(client, ba_test):
    """test valid http get request to /index route with valid session - should return valid index page account bid input field"""
    with client.session_transaction() as session:
        session["ba"] = ba_test
    response = client.get("/index")
    assert '<input id="bid_input" type="text" name="bid_input" value="TEST" readonly size="4">' in response.get_data(as_text=True)
    
# transaction

def test_send_transaction_no_tobid_invalid(client, ba_test):
    """test invalid http post request to /send_transaction route with invalid tobid form input - should return flashed error message"""
    with client.session_transaction() as session:
        session["ba"] = ba_test
        
    form_data = {
        "tobid_input": None
    }
    response = client.post("/send_transaction", data=form_data)
    
    with client.session_transaction() as session:
        flash_message = dict(session['_flashes']).get('message')
    
    assert flash_message == "Error in 'to bid' input."
    
def test_send_transaction_invalid_tobid(client, ba_test):
    """test invalid http post request to /send_transaction route with invalid tobid form input - should return flashed error message"""
    with client.session_transaction() as session:
        session["ba"] = ba_test
        
    form_data = {
        "tobid_input": "1111",
    }
    response = client.post("/send_transaction", data=form_data)
    
    with client.session_transaction() as session:
        flash_message = dict(session['_flashes']).get('message')
    
    assert flash_message == "Target account (1111) does not exist."
    
def test_send_transaction_no_curr(client, ba_test):
    """test invalid http post request to /send_transaction route with invalid currency form input - should return flashed error message"""
    with client.session_transaction() as session:
        session["ba"] = ba_test
        
    form_data = {
        "tobid_input": "9999",
        "curr_input": None
    }
    response = client.post("/send_transaction", data=form_data)
    
    with client.session_transaction() as session:
        flash_message = dict(session['_flashes']).get('message')
    
    assert flash_message == "Error in 'currency' input."
    
def test_send_transaction_invalid_curr(client, ba_test):
    """test invalid http post request to /send_transaction route with invalid currency form input - should return flashed error message"""
    with client.session_transaction() as session:
        session["ba"] = ba_test
        
    form_data = {
        "tobid_input": "9999",
        "curr_input": ""
    }
    response = client.post("/send_transaction", data=form_data)
    
    with client.session_transaction() as session:
        flash_message = dict(session['_flashes']).get('message')
    
    assert flash_message == "Inserted currency () does not exist in database."
    
def test_send_transaction_invalid_str_amount(client, ba_test):
    """test invalid http post request to /send_transaction route with invalid amount form input - should return flashed error message"""
    with client.session_transaction() as session:
        session["ba"] = ba_test
        
    form_data = {
        "tobid_input": "9999",
        "curr_input": "CZK",
        "amount_input": "no_float"
    }
    response = client.post("/send_transaction", data=form_data)
    
    with client.session_transaction() as session:
        flash_message = dict(session['_flashes']).get('message')
    
    assert flash_message == "Error in 'amount' input."

def test_send_transaction_invalid_none_amount(client, ba_test):
    """test invalid http post request to /send_transaction route with invalid amount form input - should return flashed error message"""
    with client.session_transaction() as session:
        session["ba"] = ba_test
        
    form_data = {
        "tobid_input": "9999",
        "curr_input": "CZK",
        "amount_input": None
    }
    
    with pytest.raises(TypeError) as e_info:
        response = client.post("/send_transaction", data=form_data, follow_redirects=True)
        
def test_valid_send_transaction_no_primary_transfer(client, ba_test):
    """test valid http post request to /send_transaction route with no primary transfer - should return flashed informative message"""
    form_data = {
        "tobid_input": "9999",
        "curr_input": "CZK",
        "amount_input": "10.0",
        "trans_input": "0"
    }
    
    with client.session_transaction() as session:
        session["ba"] = ba_test
        
    response = client.post("/send_transaction", data=form_data)
    
    with client.session_transaction() as session:
        flash_message = dict(session['_flashes']).get('message')
        
    assert flash_message == "You do not have enough resources."