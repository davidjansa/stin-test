import pytest
from web.objects import BankAccount, CurrencyBalance, TransactionList
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone

# FIXTURES ---------------------------------------------------

@pytest.fixture()
def account():
    hashed_passwd = generate_password_hash("test")
    return BankAccount("test_firstname", "test_surname", hashed_passwd, "test_email@mail.com", "9999")

@pytest.fixture()
def cb():
    currency_balance = {
        "CZK": 250.222,
        "EUR": 100.129,
        "USD": 10
    }
    return CurrencyBalance(currency_balance)

@pytest.fixture()
def tl():
    transaction_list = [
        {
            "target-bid": "9999",
            "currency-code": "CZK",
            "amount": "-1000.00",
            "date": datetime(2023, 12, 27, 23, 55, 59, 340, tzinfo=timezone.utc)
        },
        {
            "target-bid": "9999",
            "currency-code": "EUR",
            "amount": "+900.55",
            "date": datetime(2024, 12, 27, 23, 55, 59, 340, tzinfo=None)
        }
    ]
    return TransactionList(transaction_list)

# TESTS ------------------------------------------------------

# BankAccount

def test_bid_empty_setter_invalid(account : BankAccount):
    """test setting account bid to empty string - raises ValueError"""
    with pytest.raises(ValueError) as e_info:
        account.bid = ""

def test_firstname_empty_setter_invalid(account : BankAccount):
    """test setting account firstname to empty string - raises ValueError"""
    with pytest.raises(ValueError) as e_info:
        account.firstname = ""

def test_surname_empty_setter_invalid(account : BankAccount):
    """test setting account surname to empty string - raises ValueError"""
    with pytest.raises(ValueError) as e_info:
        account.surname = ""

def test_password_empty_setter_invalid(account : BankAccount):
    """test setting account password to empty string - raises ValueError"""
    with pytest.raises(ValueError) as e_info:
        account.password = ""

def test_check_password_valid(account : BankAccount):
    """test valid password checking"""
    assert account.check_password("test")

def test_check_password_invalid(account : BankAccount):
    """test invalid password checking"""
    assert not account.check_password("wrong_password")

def test_email_invalid_setter(account : BankAccount):
    """test setting account e-mail to empty string - raises ValueError"""
    with pytest.raises(ValueError) as e_info:
            account.email = ""

def test_email_setter_at_sign_invalid(account : BankAccount):
    """test setting account e-mail without at sign - raises ValueError"""
    with pytest.raises(ValueError) as e_info:
        account.email = "without at sign"

def test_email_setter_len_invalid(account : BankAccount):
    """test setting account e-mail invalid format - raises ValueError"""
    with pytest.raises(ValueError) as e_info:
        account.email = "@len"

# CurrencyBalance

def test_currency_balance_to_output_valid(cb : CurrencyBalance):
    """test valid currency balance formatting"""
    valid_dictionary = {
        "CZK": "250.22",
        "EUR": "100.12",
        "USD": "10.00"
    }
    assert valid_dictionary == cb.to_output()
    
# TransactionList
def test_transaction_list_to_output_valid(tl : TransactionList):
    """test valid transaction list formatting"""
    valid_list = [
        {
            "target-bid": "9999",
            "currency-code": "EUR",
            "amount": "+900.55",
            "date": "27.12.2024 23:55:59"
        },
        {
            "target-bid": "9999",
            "currency-code": "CZK",
            "amount": "-1000.00",
            "date": "27.12.2023 23:55:59"
        }
    ]
    assert valid_list == tl.to_output()