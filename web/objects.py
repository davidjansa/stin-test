from werkzeug.security import check_password_hash
import datetime

class BankAccount():
    # static bid
    bid = 0

    def __init__(self, firstname : str, surname : str, password : str, email : str):
        self.bid = f"{BankAccount.bid:04}"
        self.firstname = firstname
        self.surname = surname
        self.password = password
        self.email = email

        BankAccount.bid += 1

    # bid

    @property
    def bid(self):
        return self._bid
    
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
        return f"{self.bid};{self.firstname};{self.surname};{self.password};{self.email}"
    
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
        return f"{self.bid};{self.target_bid};{self.currency_code};{self.amount};{self.datetime}"
    
    # __str__
    