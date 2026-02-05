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
                self.set_order_tail(order_idx=head_price_tail_order, tail=idx)

            if new_price_index + 1 != num_prices:
                tail_price = side_level_prices[new_price_index + 1]
                tail_price_level = side_level[tail_price]
                tail_price_level[0] = order_price
                tail_price_head_order = tail_price_level[2]
                self.set_order_head(order_idx=tail_price_head_order, head=idx)

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
