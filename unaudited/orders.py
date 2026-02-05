import numpy as np


class orders:
    def __init__(self, cache_orders, orders_per_account):
        self.orders = np.empty(shape=(cache_orders, 9), dtype=np.int32)

        # mpid: [start_index, taken_orders, avbl_orders]
        self.mapping = {}
        self._ordersPerAccount = int(orders_per_account)

    def add_account(self, mpid):
        if mpid not in self.mapping:
            self.mapping[mpid] = len(self.mapping.keys()) * self._ordersPerAccount

    def add_order(
        self, timestamp, order_id, mpid, contract_id, price, side, qty, head=-1, tail=-1
    ):
        """
        Adds a new order given order parameters and returns a view into the new order
        """

        order_idx = self.mapping[mpid] + order_id
        self.orders[order_idx] = [
            timestamp,  # 0
            order_id,  # 1
            mpid,  # 2
            contract_id,  # 3
            price,  # 4
            side,  # 5
            qty,  # 6
            head,  # 7
            tail,  # 8
        ]

        return order_idx, self.orders[order_idx]
