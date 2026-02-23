from position import position


class margin_managers:
    def __init__(self, contract_cost_function):
        self.contractCostFunction = contract_cost_function
        self.marginManagers = []

    def allocate_margin_manager(self, user_balance):
        """
        Allocates a new margin manager given the balance of the user.
        WARNING: This does not check if the account already exists.
        """
        margin_manager_index = len(self.marginManagers)
        new_margin_manager = position(
            cost_function=self.contractCostFunction,
            user_balance=user_balance,
            position=[0, 0],
            index=margin_manager_index,
        )
        self.marginManagers.append(new_margin_manager)

        return margin_manager_index, new_margin_manager
