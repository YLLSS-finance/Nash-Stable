class contract:
    def __init__(self, contract_id, contract_name, contract_ticks):
        self.contractID = contract_id
        self.contractName = contract_name
        self.contractTicks = int(contract_ticks)
        self.costFunction = [lambda x: x, lambda x: self.contractTicks - x]

        self.book = []
