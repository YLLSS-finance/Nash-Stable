import numpy as np


class orders:
    def __init__(self, max_accounts, orders_per_account):
        self.maxAccounts = int(max_accounts)
        self.ordersPerAccount = int(orders_per_account)
        self.accountMapping = {}

        array_length = self.maxAccounts * self.ordersPerAccount

        self.timestamp = np.empty(array_length, dtype=np.int32)
        self.mpid = np.empty(array_length, dtype=np.int32)
        self.contractID = np.empty(array_length, dtype=np.int32)
        self.price = np.empty(array_length, dtype=np.int16)
        self.side = np.empty(array_length, dtype=np.int8)
        self.qty = np.empty(array_length, dtype=np.uint16)
        self.head = np.empty(array_length, dtype=np.int32)
        self.tail = np.empty(array_length, dtype=np.int32)
        self.marginManagerIdx = np.empty(array_length, dtype=np.int32)
        self.order_used = np.zeros(array_length, dtype=np.bool)

    def add_account(self, mpid):
        if mpid in self.accountMapping:
            return
        acct_start_idx = len(self.accountMapping.keys()) * self.ordersPerAccount
        self.accountMapping[mpid] = acct_start_idx
        return acct_start_idx
