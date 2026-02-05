from position import position

# order schema:
# [timestamp, order_id, mpid, instrument_id, price, side, qty, prio]
#      0          1       2         3          4     5     6    7


class account:
    def __init__(
        self,
        _master,
        mpid,
        balance,
        prio,
    ):
        self.mpid = int(mpid)

        # balance, used margin
        self.balance = [balance, 0]
        self.prio = prio

        # instrument_ID: position_manager
        # ALL ORDER MANIPULATIONS MUST BE REPORTED HERE
        self.positions = {}

        self.orders = {}
        self.availableOrders = set([i for i in range(0, 20)])

        self.orderBooks = _master.orderBooks

    def add_order(self, timestamp, instrument_id, price, side, qty):
        if not self.availableOrders:
            return False, 250

        order_ID = self.availableOrders.pop()
        if instrument_id not in self.positions:
            self.positions[instrument_id] = position(
                user_balance=self.balance, position=[0, 0]
            )

            self.orderBooks[instrument_id].positionReferance[self.mpid] = (
                self.positions[instrument_id]
            )

        if self.positions[instrument_id].insert_order(price=price, side=side, qty=qty):
            new_order = [
                timestamp,
                order_ID,
                self.mpid,
                instrument_id,
                price,
                side,
                qty,
                self.prio,
            ]

            self.orders[order_ID] = new_order
            return True, new_order

        return False, 200

    def log_fill(self, instrument, price, side, qty):
        """
        This manipulates the position manager only
        """

    def remove_order(self, order_id):
        if order_id not in self.orders:
            return False

        order = self.orders[order_id]
        del self.orders[order_id]
        return order
