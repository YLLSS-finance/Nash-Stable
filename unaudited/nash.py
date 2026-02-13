from order_book import order_book
from orders import orders
from position import position


class nash:
    def __init__(self):
        self.accounts = {}

        self.orderBooks = {}
        self.contractHolders = {}

        self.orders = orders(_master=self, cache_orders=10000, orders_per_account=20)

    # admin
    def create_account(self, mpid):
        if mpid in self.accounts:
            return False, 000

        self.orders.add_account(mpid)
        return True, 100

    # admin
    def add_contract(self, contract_id):
        if contract_id not in self.orderBooks:
            self.orderBooks[contract_id] = order_book(_master=self)
            self.contractHolders[contract_id] = set()
            return True, 100
        return False, 000

    # admin
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
        return False, 000

    def add_order(self, timestamp, mpid, contract_id, price, side, qty):
        mpid = int(mpid)
        contract_id = int(contract_id)

        # Presence check for account and instrument
        if mpid not in self.accounts:
            return False, 400  # 400: account not found

        if contract_id not in self.orderBooks:
            return False, 450

        # Check for malformed input
        price = int(price)
        qty = int(qty)
        if price < 1 or price > 99 or side not in [0, 1] or qty < 1:
            return False, 800

        acct = self.accounts[mpid]
        if not acct.availableOrders:
            return False, 250

        new_pos = False
        if contract_id not in acct.positions:
            new_pos = True
            acct.positions[contract_id] = position(user_balance=acct.balance)

        position_manager = acct.positions[contract_id]
        if position_manager.insert_order(price, side, qty):
            order_id = acct.availableOrders.pop()
            acct.usedOrders.add(order_id)
        else:
            if new_pos:
                del acct.positions[contract_id]
            return False, 200

        new_order_idx, new_order_view = self.orders.add_order(
            timestamp=timestamp,
            order_id=order_id,
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

    def _acct_remove_order(self, acct, order_id):
        if order_id not in acct.usedOrders:
            return False

        acct.usedOrders.remove(order_id)
        acct.availableOrders.add(order_id)
        return True

    def remove_order(self, mpid, order_id):
        acct = self.accounts[mpid]
        if self._acct_remove_order(acct, order_id):
            order_exists, order_view = self.orders.get_order(
                mpid=mpid, order_id=order_id
            )

            if order_exists:
                self.orderBooks[order_view[3]].remove_order(order_view)

            return True, 100
        return False, 250

    def remove_contract_orders(self, mpid, contract_id, ignore_position=False):
        """
        Batch removes orders of an account with a specific contract ID.
        """
        if contract_id not in self.orderBooks:
            return
        if mpid not in self.contractHolders[contract_id]:
            return

        acct = self.accounts[mpid]
        if contract_id in acct.positions:
            position_manager = acct.positions[contract_id]
        else:
            # if there does not exist even a position manager pertaining to an instrument, there must not be any orders
            # as the former is required for the latter to exist!
            return

        rmv = []
        for order_id in acct.usedOrders:
            order_exists, order_view = self.orders.get_order(
                mpid=mpid, order_id=order_id
            )
            if not order_exists:
                continue

            if order_view[3] == contract_id:
                self.orderBooks[order_view[3]].remove_order(order_view)
                if not ignore_position:
                    position_manager.remove_order(
                        order_view[4], order_view[5], order_view[6]
                    )
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
            self._acct_remove_order(acct, order_view[1])
            return True
        return False
