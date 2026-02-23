from mmap import ACCESS_COPY
from this import s

from account import account
from order_level import order_level
from orders import orders
from position import position


class nash:
    def __init__(self):

        self.ordersPerAccount = 20
        self.accounts = {}
        self.orders = orders(
            max_accounts=10000, orders_per_account=self.ordersPerAccount
        )
        self.marginManagers = {}

    def add_account(self, mpid):
        if mpid in self.accounts:
            return False
        self.accounts[mpid] = account
