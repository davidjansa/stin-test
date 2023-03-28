from werkzeug.security import check_password_hash
from datetime import datetime

class BankAccount:
    # static bid
    bid = 1

    def __init__(self, firstname : str, surname : str, password : str, email : str, bid : str = None):
        if bid is None:
            self.bid = f"{BankAccount.bid:04}"
            BankAccount.bid += 1
        else:
            self.bid = bid
        self.firstname = firstname
        self.surname = surname
        self.password = password
        self.email = email

    # bid

    @property
    def bid(self):
        return self._bid
    
    @bid.setter
    def bid(self, bid : str):
        if bid != "":
            self._bid = bid
    
    # firstname
    
    @property
    def firstname(self):
        return self._firstname
    
    @firstname.setter
    def firstname(self, firstname : str):
        if firstname != "":
            self._firstname = firstname
        else:
            raise ValueError("Firstname can't be empty.")

    # surname

    @property
    def surname(self):
        return self._surname
    
    @surname.setter
    def surname(self, surname : str):
        if surname != "":
            self._surname = surname
        else:
            raise ValueError("Surname can't be empty.")
    
    # password

    @property
    def password(self):
        return self._password
    
    @password.setter
    def password(self, password : str):
        if password != "":
            self._password = password
        else:
            raise ValueError("Password can't be empty.")
        
    def check_password(self, password : str) -> bool:
        return check_password_hash(self.password, password)
        
    # email
    
    @property
    def email(self):
        return self._email
    
    @email.setter
    def email(self, email : str):
        if '@' in email and len(email) > 5:
            self._email = email
        else:
            raise ValueError("E-mail format is not valid.")
        
    # __repr__

    def __repr__(self):
        return {
            "bid": self.bid,
            "email": self.email,
            "firstname": self.firstname,
            "surname": self.surname,
            "password": self.password
            }
    
    # __str__

class Transaction():
    def __init__(self, bid : str, target_bid : str, currency_code : str, amount : float, date : datetime):
        self.bid = bid
        self.target_bid = target_bid
        self.currency_code = currency_code
        self.amount = amount
        self.date = date

    # __repr__

    def __repr__(self):
        return {
            "bid": self.bid,
            "target-bid": self.target_bid,
            "currency-code": self.currency_code,
            "amount": self.amount,
            "date": self.date
            }
    
    # __str__

class Balance():
    def __init__(self, bid : str, currency_balance : dict):
        self.bid = bid
        self.currency_balance = currency_balance
    
    # __repr__

    def __repr__(self):
        return {
            "bid": self.bid,
            "currency_balance": self.currency_balance
            }