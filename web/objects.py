from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import math

class BankAccount():
    bid = 1

    def __init__(self, firstname : str, surname : str, password : str, email : str, bid : str = None):
        """bank account object

        Args:
            firstname (str): firstname
            surname (str): surname
            password (str): hashed password
            email (str): e-mail
            bid (str, optional): bank account id. Defaults to None.
        """
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
        else:
            raise ValueError("BID can't be empty.")
    
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
        """check bank account password with inserted password

        Args:
            password (str): password to be checked

        Returns:
            bool: True if the passwords are matched else False
        """
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

class TransactionList():
    def __init__(self, transaction_list):
        """bank account transaction list

        Args:
            transaction_list (list[dict]): list of transactions
        """
        self.transaction_list = transaction_list

    def to_output(self):
        """transform transaction list to specific format

        Returns:
            list[dict]: list with formated transactions
        """
        mod_transaction_list = list()
        for obj in self.transaction_list:
            mod_transaction_list.append(
                {
                "target-bid": obj["target-bid"],
                "currency-code": obj["currency-code"],
                "amount": obj["amount"],
                "date": datetime.strftime(obj["date"].replace(tzinfo=None), "%d.%m.%Y %H:%M:%S")
                }
            )
        mod_transaction_list.reverse()
        return mod_transaction_list

class CurrencyBalance():
    def __init__(self, currency_balance : dict):
        """bank account currency balances

        Args:
            currency_balance (dict): "currency-code": amount
        """
        self.currency_balance = currency_balance

    def to_output(self) -> dict:
        """transform currency balances to specific format

        Returns:
            dict: dict with formated currency balances
        """
        mod_currency_balance = dict()
        for key, value in self.currency_balance.items():
            mod_currency_balance[key] = f"{math.floor(value * 100) / 100:.2f}"
        return mod_currency_balance