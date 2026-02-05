from position import position


class account:
    def __init__(self):
        self.balance = [0, 0]
        self.positions = {}

        self.usedOrders = set()
        self.availableOrders = set([i for i in range(0, 20)])

    def add_order(self, contract_id, price, side, qty):
        # Process operation of adding an order to an account.
        # If this function returns true, an add order operation MUST be conducted in the main order array
        # and order book.

        if not self.availableOrders:
            return False, 250

        if contract_id not in self.positions:
            self.positions[contract_id] = position(user_balance=self.balance)

        position_manager = self.positions[contract_id]
        if position_manager.insert_order(price, side, qty):
            order_id = self.availableOrders.pop()
            self.usedOrders.add(order_id)
            return True, self.availableOrders.pop()
        else:
            # Insufficient margin
            return False, 200

    def remove_order(self, order_id):
        if order_id not in self.usedOrders:
            return False, 250

        self.usedOrders.remove(order_id)
        return True, 100
