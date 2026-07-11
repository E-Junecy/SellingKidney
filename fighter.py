from moves import SKILLS


class Fighter:
    def __init__(self):
        self.hp = 1.0
        self.max_hp = 2.0
        self.qi = 0
        self.shield = 0
        self.reflect_cooldown = 0
        self.reflect_disabled = False
        self.damage_bonus = False

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, damage):
        if self.shield > 0:
            absorbed = min(self.shield, damage)
            self.shield -= absorbed
            damage -= absorbed
        self.hp -= damage
        return damage

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def apply_buff(self, move_name):
        info = SKILLS[move_name]
        if info["effect"] == "qi":
            self.qi += info["value"]
        elif info["effect"] == "heal":
            self.heal(info["value"])
        elif info["effect"] == "shield":
            self.shield += info["value"]
        elif info["effect"] == "damage_boost":
            self.damage_bonus = True

    def use_move(self, move_name):
        info = SKILLS[move_name]
        self.qi -= info["qi_cost"]
        if move_name == "反弹":
            self.reflect_cooldown = 2
        if self.reflect_cooldown > 0:
            self.reflect_cooldown -= 1


def get_available_moves(fighter):
    moves = []
    for name, info in SKILLS.items():
        if fighter.qi >= info["qi_cost"]:
            if name == "反弹" and fighter.reflect_cooldown > 0:
                continue
            if name == "反弹" and fighter.reflect_disabled:
                continue
            moves.append(name)
    return moves
