from orders import orders


class nash:
    def __init__(self):
        self.accounts = {}

        self.orderBooks = {}

        self.orders = orders(cache_orders=10000, orders_per_account=20)

    def create_account(self, mpid):
        if mpid in self.accounts:
            return False

    def add_order(self, timestamp, mpid, contract_id, price, side, qty):
        if mpid not in self.accounts:
            return False, 299

        acct = self.accounts[mpid]
        successful, result = acct.add_order(contract_id, price, side, qty)

        if not successful:
            return False, result

        new_order_idx, new_order = self.orders.add_order(
            timestamp=timestamp,
            order_id=result,
            mpid=mpid,
            contract_id=contract_id,
            price=price,
            side=side,
            qty=qty,
        )
