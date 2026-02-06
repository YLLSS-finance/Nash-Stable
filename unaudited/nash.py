from _typeshed import FileDescriptor
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

    def fill_order(self, order_view, fills):
        order_price, order_side = order_view
        acct = self.accounts[order_view[2]]

        if order_view[6] == 0:
            acct.remove_order()

        # log the fill in the margin manager
        for fill_price, fill_qty in fills:
            acct.positions[order_view[3]].fill_order(
                order_price, order_side, fill_price, fill_qty
            )
            order_view[6] -= fill_qty


#
