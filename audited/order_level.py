from orders import orders as orders
from sortedcontainers import SortedDict

# An Order Level stores orders from a particular side (buy/long or sell/short) in price order from best to worst
# here we want an order level to be able to:
# add an order given the new order idx
# remove an order, also given the order idx
# fill an oncoming order, given its limit price and quantity.
#
# In all cases we return the change of the tob-of-book incurred by the operation(s) first before we do anything else
# (deltaPrice/False for all orders in the book being removed)

class orderLevel:
    def __init__(self, orders=orders, margin_managers=list, side):
        self.orders = orders
        self.marginManagers = margin_managers
        self.sign = -1 if side == 0 else 1

        # converted_price: [head_price, tail_price, head_order, tail_order, cum_orders, cum_qty]
        # remember that lower converted price == better
        # if a new price is better than the current tob, the price delta is current_tob - new_tob
        self.book = SortedDict()
        self.prices = self.book.keys()
        # the top of book shall be the value of the top-of-book price key in self.book
        # this way filling can occur directly without going through a dict key lookup which is comparatively slow

        self.tobPrice = None
        self.tobContent = None

    def add_order(self, order_idx):
        order_price = self.orders.prices[order_idx] * self.sign
        tob_change = 0

        # the order price is new
        if order_price not in self.book:
            self.book[order_price] = []
            book_length = len(self.prices)
            new_price_idx = self.prices.index(order_price)

            head_price, tail_price = None, None
            order_head, order_tail = -1, -1
            if new_price_idx != 0 and book_length:
                head_price = self.prices[new_price_idx - 1]
                head_price_tail_order_idx = self.book[head_price][3]
                self.orders.tail[head_price_tail_order_idx] = order_idx
                order_head = head_price_tail_order_idx

            if new_price_idx + 1 < book_length:
                tail_price = self.prices[new_price_idx + 1]
                tail_price_head_order_idx = self.book[tail_price][2]
                self.orders.head[tail_price_head_order_idx] = order_idx
                order_tail = tail_price_head_order_idx

            self.orders.head[order_idx] = order_head
            self.orders.tail[order_idx] = order_tail

            self.book[order_price] = [head_price, tail_price, order_idx, order_idx, 1, self.orders.qty]

            if self.tobPrice is None:
                tob_change = order_price if self.sign == 1 else -order_price
                self.tobPrice = order_price
                self.tobContent = self.book[order_price]

            elif order_price < self.tobPrice:
                tob_change = self.tobPrice - order_price
                self.tobPrice = order_price
                self.tobContent = self.book[order_price]
