from order_book import order_book
from orders import orders


class nash:
    def __init__(self):
        self.accounts = {}

        self.orderBooks = {}
        self.contractHolders = {}

        self.orders = orders(_master=self, cache_orders=10000, orders_per_account=20)

    def create_account(self, mpid):
        if mpid in self.accounts:
            return False

        self.orders.add_account(mpid)
        return True

    def add_contract(self, contract_id):
        if contract_id not in self.orderBooks:
            self.orderBooks[contract_id] = order_book(_master=self)
            self.contractHolders[contract_id] = set()

        return False, 500

    def resolve_contract(self, contract_id, value):
        if contract_id in self.orderBooks:
            holders = self.contractHolders[contract_id]
            for holder_mpid in holders:
                self.accounts[holder_mpid].positions[contract_id].resolve(
                    contract_id, value
                )

                self.remove_contract_orders(
                    mpid=holder_mpid, contract_id=contract_id, ignore_position=True
                )
            return True, 100
        return False, 500

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

        self.contractHolders[contract_id].add(mpid)

        contract_clob = self.orderBooks[contract_id]
        fills = contract_clob.process_new_order(price, side, qty)
        fully_filled = self.fill_order(order_view=new_order_view, fills=fills)

        if not fully_filled:
            contract_clob.add_order(new_order_idx, new_order_view)

    def remove_order(self, mpid, order_id):
        acct = self.accounts[mpid]
        successful, return_code = acct.removeOrder(order_id)
        if successful:
            order_exists, order_view = self.orders.get_order(
                mpid=mpid, order_id=order_id
            )
            if order_exists:
                self.orderBooks[order_view[3]].remove_order(order_view)

        return successful, return_code

    def remove_contract_orders(self, mpid, contract_id, ignore_position=False):
        """
        Batch removes orders of an account with a specific contract ID.
        """
        if contract_id not in self.orderBooks:
            return
        if mpid not in self.contractHolders[contract_id]:
            return

        acct = self.accounts[mpid]
        rmv = []
        for order_id in acct.usedOrders:
            order_exists, order_view = self.orders.get_order(
                mpid=mpid, order_id=order_id
            )
            if not order_exists:
                continue

            if order_view[3] == contract_id:
                self.orderBooks[order_view[3]].remove_order(order_view)
                rmv.append(order_id)

        for rmv_id in rmv:
            acct.usedOrders.remove(rmv_id)

    def fill_order(self, order_view, fills):
        """
        Fills an order given its view and a list of fills [(price, qty), ...].
        Returns True if the order is fully filled by the operation, False otherwise.
        """

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
