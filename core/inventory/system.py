class InventorySystem:
    def __init__(self):
        self.inventories = {}

    def add_item(self, user_id: int, item_id: int, quantity: int) -> None:
        if user_id not in self.inventories:
            self.inventories[user_id] = {}
        
        if item_id not in self.inventories[user_id]:
            self.inventories[user_id][item_id] = 0
        
        self.inventories[user_id][item_id] += quantity

    def get_inventory(self, user_id: int) -> dict:
        return self.inventories.get(user_id, {})