from position import position


# TODO: Add slots
@dataclass
class account:
    def __init__(self):
        self.balance = [0, 0]
        self.positions = {}

        self.usedOrders = set()
        self.availableOrders = set([i for i in range(0, 20)])
