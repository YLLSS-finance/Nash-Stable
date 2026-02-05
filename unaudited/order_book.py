from sortedcontainers import SortedDict


class order_book:
    def __init__(self, _master):
        self.positionReferance = {}
        self.topOfBook = [None, None]

        self.levels = [SortedDict(), SortedDict()]
        self.levelPrices = [self.levels[0].keys(), self.levelPrices[1].keys()]

        self.priceMapping = [lambda x: -x, lambda x: x]

        self.globalAccounts = _master.accounts
        self.globalOrders = _master.orders

    def set_order_head(self, order_idx, head):
        self.globalOrders.orders[order_idx][7] = head

    def set_order_tail(self, order_idx, tail):
        self.globalOrders.orders[order_idx][8] = tail

    def add_order(self, idx, order):
        order_side = order[5]
        order_price = self.priceMapping[order_side](order[4])

        side_level = self.levels[order_side]
        side_level_prices = self.levelPrices[order_side]
        if order_price not in side_level:
            # head price, tail price, head order, tail order, cum orders, cum qty
            side_level[order_price] = None
            new_price_index = side_level_prices.index(order_price)
            num_prices = len(side_level_prices)

            head_price, tail_price = None, None

            if new_price_index != 0:
                head_price = side_level_prices[new_price_index - 1]
                head_price_level = side_level[head_price]
                head_price_level[1] = order_price
                head_price_tail_order = head_price_level[3]
                self.set_order_tail(order_idx=head_price_tail_order, tail=idx)

            if new_price_index + 1 != num_prices:
                tail_price = side_level_prices[new_price_index + 1]
                tail_price_level = side_level[tail_price]
                tail_price_level[0] = order_price
                tail_price_head_order = tail_price_level[2]
                self.set_order_head(order_idx=tail_price_head_order, head=idx)

            # Update the top of book price
            cur_tob = self.topOfBook[order_side]
            if cur_tob is None:
                self.topOfBook[order_side] = order_price
            elif order_price < cur_tob:
                cur_tob = order_price

        else:
            order_price_level = side_level[order_price]
            tail_price_level = side_level[order_price_level[1]]
            tail_price_tail_order = tail_price_level[3]
            self.set_order_head(order_idx=tail_price_tail_order, head=idx)
