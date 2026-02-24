from config import MAX_HP, MAX_FUEL


class Player:
    def __init__(self, name, x, color):
        self.name = name
        self.x = x
        self.hp = MAX_HP
        self.angle = 45
        self.power = 25
        self.fuel = MAX_FUEL
        self.color = color
        self.item_id = None
        self.active_item = None
        self.trails = []


class Item:
    def __init__(self, x, itype):
        self.x = x
        self.itype = itype


class Mine:
    def __init__(self, x, owner):
        self.x = x
        self.turns_left = 3
        self.owner = owner