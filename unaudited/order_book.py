from nash import nash
from sortedcontainers import SortedDict


class order_book:
    def __init__(self, _master: nash):
        self.positionReferance = {}
        self.topOfBook = [None, None]

        self.levels = [SortedDict(), SortedDict()]
        self.levelPrices = [self.levels[0].keys(), self.levelPrices[1].keys()]

        self.priceMapping = [lambda x: -x, lambda x: x]

        self.globalAccounts = _master.accounts
        self.globalOrders = _master.orders.orders

        self.fill_order = _master.fill_order

    def set_order_head(self, order_idx, head):
        self.globalOrders[order_idx][7] = head

    def set_order_tail(self, order_idx, tail):
        self.globalOrders[order_idx][8] = tail

    def add_order(self, idx, order):
        order_price, order_side, order_quantity = order[4:7]
        order_price = self.priceMapping[order_side](order_price)

        side_level = self.levels[order_side]
        side_level_prices = self.levelPrices[order_side]
        if order_price not in side_level:
            # head price, tail price, head order, tail order, cum orders, cum qty
            side_level[order_price] = [None, None, idx, idx, 1, order[6]]
            order_price_level = side_level[order_price]
            new_price_index = side_level_prices.index(order_price)
            num_prices = len(side_level_prices)

            head_price, tail_price = None, None

            # Handle links of head and tail prices, if they exist
            if new_price_index != 0:
                head_price = side_level_prices[new_price_index - 1]
                head_price_level = side_level[head_price]
                head_price_level[1] = order_price
                head_price_tail_order = head_price_level[3]
                self.globalOrders[head_price_tail_order][8] = idx

            if new_price_index + 1 != num_prices:
                tail_price = side_level_prices[new_price_index + 1]
                tail_price_level = side_level[tail_price]
                tail_price_level[0] = order_price
                tail_price_head_order = tail_price_level[2]
                self.globalOrders[tail_price_head_order][7] = idx

            order_price_level[0:2] = [head_price, tail_price]

            # Update the top of book price
            cur_tob = self.topOfBook[order_side]
            if cur_tob is None:
                self.topOfBook[order_side] = order_price
            elif order_price < cur_tob:
                cur_tob = order_price

        else:
            order_price_level = side_level[order_price]

            # For the head order of the tail price level of the new order,
            # set its head to that of the new order,
            # as it directly connects with it (new order is at the end of the queue at its price level,
            # so the first order at the immediately worse price level has to update its head link to it)
            tail_price_level = side_level[order_price_level[1]]
            tail_price_head_order = tail_price_level[2]
            self.set_order_head(order_idx=tail_price_head_order, head=idx)

            # set the tail of the order's price level to that of the new order
            order_price_level[3] = idx

            # update cumulative order count and order quantity
            order_price_level[4] += 1
            order_price_level[5] += order_quantity

    def remove_order(self, order_view):
        order_price, order_side = order_view[4:6]
        level_price = self.priceMapping[order_side](order_price)
        order_level = self.levels[level_price]

        head_link, tail_link = order_view[7:9]
        if head_link != -1:
            self.globalOrders[head_link][8] = tail_link
        if tail_link != -1:
            self.globalOrders[tail_link][7] = head_link

        order_level[4] -= 1
        if not order_level[4]:
            self.remove_price_level(side=order_side, price_level=level_price)

    def remove_price_level(self, side, price_level):
        """
        Removes a price level in the order book given its side and price.
        Returns True if the operation causes that side of the order book to become empty, otherwise False.
        """

        side_levels = self.levels[side]
        level = side_levels[price_level]
        level_prices = self.levelPrices[side]

        if level[4] != 0:
            raise Exception(
                "Attmpted to remove price level where an order(s) still exist"
            )
        head_price, tail_price = level[0:2]
        if head_price is not None:
            self.levels[head_price][1] = tail_price
        if tail_price is not None:
            self.levels[tail_price][0] = head_price
        del side_levels[price_level]

        if len(level_prices):
            self.topOfBook[side] = level_prices[0]
            return False
        else:
            self.topOfBook[side] = None
            return True

    def process_new_order(self, order_price, order_side, order_qty):
        opp_side = 1 - order_side
        tob_updated = True
        # Check for opposite price level not crossing or empty

        opp_levels = self.levels[opp_side]
        opp_prices = self.levelPrices[opp_side]
        not_crossing = lambda a, b: a < b if order_side == 0 else lambda a, b: -a > b

        fills = []
        while True:
            opp_tob = self.topOfBook[opp_side]
            if tob_updated:
                if opp_tob is None or not_crossing(opp_tob, order_price):
                    break
                tob_updated = False

            opp_level = opp_levels[opp_tob]
            opp_order_idx = opp_level[0]
            opp_order_view = self.globalOrders[opp_order_idx]

            fill_price = opp_order_view[4]
            fill_qty = min(order_qty, opp_order_view[6])

            if not fill_qty:
                break

            self.fill_order(order_view=opp_order_view, fills=[(fill_price, fill_qty)])
            order_qty -= fill_qty
            fills.append((fill_price, fill_qty))
            opp_level[5] -= fill_qty

            if not opp_order_view[6]:
                opp_level[4] -= 1
                if not opp_level[4]:
                    book_empty = self.remove_price_level(opp_side, opp_tob)
                    if book_empty:
                        break

                opp_order_tail = opp_order_view[8]
                opp_level[2] = opp_order_tail
                # The head of the tail order is rendered null here as it becomes the new top order (with no orders before it)
                self.globalOrders[opp_order_tail][7] = -1
            else:
                break
