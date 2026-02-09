from order_book import order_book
from orders import orders


class nash:
    def __init__(self):
        self.accounts = {}

        self.orderBooks = {}

        self.orders = orders(_master=self, cache_orders=10000, orders_per_account=20)

    def create_account(self, mpid):
        if mpid in self.accounts:
            return False

        self.orders.add_account(mpid)

    def add_contract(self, contract_id):
        if contract_id not in self.orderBooks:
            self.orderBooks[contract_id] = order_book(_master=self)

    def add_order(self, timestamp, mpid, contract_id, price, side, qty):
        if mpid not in self.accounts:
            return False, 400  # 400: account not found

        if contract_id not in self.orderBooks:
            return False, 450

        acct = self.accounts[mpid]
        successful, result = acct.add_order(contract_id, price, side, qty)

        if not successful:
            return False, result

        new_order_idx, new_order_view = self.orders.add_order(
            timestamp=timestamp,
            order_id=result,
            mpid=mpid,
            contract_id=contract_id,
            price=price,
            side=side,
            qty=qty,
        )

        contract_clob = self.orderBooks[contract_id]
        fills = contract_clob.process_new_order(price, side, qty)
        fully_filled = self.fill_order(order_view=new_order_view, fills=fills)

        if not fully_filled:
            contract_clob.add_order(new_order_idx, new_order_view)

    def fill_order(self, order_view, fills):
        order_price, order_side = order_view[4:6]
        acct = self.accounts[order_view[2]]

        # log the fill in the margin manager
        for fill_price, fill_qty in fills:
            acct.positions[order_view[3]].fill_order(
                order_price, order_side, fill_price, fill_qty
            )
            order_view[6] -= fill_qty

        if order_view[6] == 0:
            acct.remove_order(order_view[1])
            return True
        return False
