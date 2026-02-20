from mmap import ACCESS_COPY

from account import account
from order_level import order_level
from orders import orders
from position import position


class nash:
    def __init__(self):
        self.accounts = {}
        self.orders = orders(max_accounts=10000, orders_per_account=20)
