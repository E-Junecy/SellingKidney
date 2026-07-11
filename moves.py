SKILLS = {
    "空气炮": {"type": "attack", "qi_cost": 0, "damage": 0.5},
    "\u201c嘣\u201d": {"type": "attack", "qi_cost": 1, "damage": 1},
    "\u201c劈\u201d": {"type": "attack", "qi_cost": 2, "damage": 1},
    "\u201c砍\u201d": {"type": "attack", "qi_cost": 3, "damage": 1.5},
    "聚气": {"type": "buff", "qi_cost": 0, "effect": "qi", "value": 1},
    "治疗": {"type": "buff", "qi_cost": 0, "effect": "heal", "value": 0.5},
    "叠盾": {"type": "buff", "qi_cost": 1, "effect": "shield", "value": 1},
    "\u201c酒\u201d": {"type": "buff", "qi_cost": 1, "effect": "damage_boost", "value": 1},
    "防御": {"type": "defend", "qi_cost": 0, "block_qi": 3},
    "超级防": {"type": "defend", "qi_cost": 1, "block_qi": 6},
    "反弹": {"type": "reflect", "qi_cost": 0},
    "破反": {"type": "special", "qi_cost": 0, "effect": "break_reflect"},
}

SKILL_TYPES = {
    "attack": "攻击",
    "buff": "增益",
    "defend": "防御",
    "reflect": "反弹",
    "special": "特殊",
}
