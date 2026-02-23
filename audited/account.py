from position import position


# TODO: Add slots
class account:
    __slots__ = (
        "balance",
        "positions",
        "usedOrders",
        "availableOrders",
        "orderStartIdx",
    )

    def __init__(self, order_start_idx, num_orders):
        self.balance = [0, 0]
        self.positions = {}

        self.usedOrders = set()
        self.availableOrders = set([i for i in range(0, 20)])

        self.orderStartIdx = order_start_idx
