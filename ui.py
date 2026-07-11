from moves import SKILLS, SKILL_TYPES
from fighter import get_available_moves


def show_status(player, ai):
    p_tag = ""
    if player.reflect_cooldown > 0:
        p_tag = " [反弹冷却]"
    elif player.reflect_disabled:
        p_tag = " [反弹已失效]"
    if player.damage_bonus:
        p_tag += " [下次攻击招式伤害+1]"
    a_tag = ""
    if ai.reflect_cooldown > 0:
        a_tag = " [反弹冷却]"
    elif ai.reflect_disabled:
        a_tag = " [反弹已失效]"
    if ai.damage_bonus:
        a_tag += " [下次攻击招式伤害+1]"

    print(f"\n{'='*50}")
    print(f"  玩家: HP={player.hp:.1f}/{player.max_hp:.1f}  Qi={player.qi}  Shield={player.shield}{p_tag}")
    print(f"  AI:   HP={ai.hp:.1f}/{ai.max_hp:.1f}  Qi={ai.qi}  Shield={ai.shield}{a_tag}")
    print(f"{'='*50}")


def show_moves(player):
    available = get_available_moves(player)
    cooling = []
    if player.reflect_cooldown > 0 and not player.reflect_disabled:
        cooling.append("反弹（冷却中）")

    print("\n可用招式:")
    for i, name in enumerate(available, 1):
        info = SKILLS[name]
        cost = info["qi_cost"]
        stype = SKILL_TYPES[info["type"]]

        if info["type"] == "attack":
            desc = f"造成{info['damage']}点伤害"
        elif info["type"] == "buff":
            if info["effect"] == "qi":
                desc = "气量+1"
            elif info["effect"] == "heal":
                desc = "血量+0.5"
            elif info["effect"] == "shield":
                desc = "护盾+1"
            elif info["effect"] == "damage_boost":
                desc = "下次攻击招式伤害+1"
        elif info["type"] == "defend":
            desc = f"挡住≤{info['block_qi']}气的攻击"
        elif info["type"] == "reflect":
            desc = "反弹伤害，使用后冷却1回合" if name == "反弹" else "若敌方用反弹，永久禁用其反弹"

        cost_str = f"（消耗{cost}气）" if cost > 0 else ""
        print(f"  {i}. [{stype}] {name} - {desc}{cost_str}")

    if cooling:
        print("\n冷却中:")
        for name in cooling:
            print(f"  - {name}")


def show_round_result(p_move, a_move, p_hp_change, a_hp_change):
    print(f"\n玩家使用: {p_move} | AI使用: {a_move}")

    if a_hp_change < 0:
        print(f"  AI受到{abs(a_hp_change):.1f}点伤害")
    if p_hp_change < 0:
        print(f"  玩家受到{abs(p_hp_change):.1f}点伤害")

    if a_hp_change == 0 and p_hp_change == 0:
        if p_move == "破反" and a_move == "反弹":
            print(f"  AI永久失去了反弹能力")
        elif a_move == "破反" and p_move == "反弹":
            print(f"  玩家永久失去了反弹能力")
        else:
            print(f"  无事发生")


def show_result(player_won):
    print(f"\n{'='*50}")
    print("  恭喜！你赢了！" if player_won else "  你输了...")
    print(f"{'='*50}")
