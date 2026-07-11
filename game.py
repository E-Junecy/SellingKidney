from moves import SKILLS
from fighter import Fighter, get_available_moves
from ai import ai_think
from history import save_history
from ui import show_status, show_moves, show_round_result, show_result


JIU_WEIGHT = 1.2


def resolve(p_move, a_move, p_bonus=False, a_bonus=False):
    p_type = SKILLS[p_move]["type"]
    a_type = SKILLS[a_move]["type"]

    if p_type == "attack" and a_type == "attack":
        if p_move == a_move:
            return 0, 0
        p_eff = SKILLS[p_move]["qi_cost"] + (JIU_WEIGHT if p_bonus else 0)
        a_eff = SKILLS[a_move]["qi_cost"] + (JIU_WEIGHT if a_bonus else 0)
        p_dmg = SKILLS[p_move]["damage"] + (1 if p_bonus else 0)
        a_dmg = SKILLS[a_move]["damage"] + (1 if a_bonus else 0)
        if p_eff > a_eff:
            return p_dmg, 0
        elif a_eff > p_eff:
            return 0, a_dmg
        return 0, 0

    if p_type == "attack" and a_type == "defend":
        if SKILLS[p_move]["qi_cost"] < SKILLS[a_move]["block_qi"]:
            return 0, 0
        return SKILLS[p_move]["damage"] + (1 if p_bonus else 0), 0

    if a_type == "attack" and p_type == "defend":
        if SKILLS[a_move]["qi_cost"] < SKILLS[p_move]["block_qi"]:
            return 0, 0
        return 0, SKILLS[a_move]["damage"] + (1 if a_bonus else 0)

    if p_type == "attack" and a_type == "reflect":
        if a_move == "反弹":
            return 0, SKILLS[p_move]["damage"] + (1 if p_bonus else 0)
        return SKILLS[p_move]["damage"] + (1 if p_bonus else 0), 0

    if a_type == "attack" and p_type == "reflect":
        return SKILLS[a_move]["damage"] + (1 if a_bonus else 0), 0

    if a_type == "attack" and p_type == "special":
        return 0, SKILLS[a_move]["damage"] + (1 if a_bonus else 0)

    if p_type == "attack" and a_type == "special":
        return SKILLS[p_move]["damage"] + (1 if p_bonus else 0), 0

    if a_type == "attack":
        return 0, SKILLS[a_move]["damage"] + (1 if a_bonus else 0)

    if p_type == "attack":
        return SKILLS[p_move]["damage"] + (1 if p_bonus else 0), 0

    return 0, 0


def handle_reflect(p_move, a_move, player, ai):
    if p_move == "破反" and a_move == "反弹":
        ai.reflect_disabled = True
    elif a_move == "破反" and p_move == "反弹":
        player.reflect_disabled = True


def get_player_move(player):
    available = get_available_moves(player)
    while True:
        try:
            choice = int(input("\n请选择招式编号: ")) - 1
            if 0 <= choice < len(available):
                return available[choice]
            print("无效选择，请重新输入")
        except ValueError:
            print("请输入数字")


def battle(difficulty):
    player = Fighter()
    ai = Fighter()
    history = []
    round_num = 0

    diff_names = {1: "简单", 2: "普通", 3: "困难"}
    print(f"\n{'='*50}")
    print(f"  对战开始！难度: {diff_names[difficulty]}")
    print(f"{'='*50}")

    while player.is_alive() and ai.is_alive():
        round_num += 1
        show_status(player, ai)
        show_moves(player)

        p_move = get_player_move(player)
        a_move = ai_think(ai, player, history, difficulty)

        p_type = SKILLS[p_move]["type"]
        a_type = SKILLS[a_move]["type"]

        player.use_move(p_move)
        ai.use_move(a_move)

        if a_type == "buff" and p_type == "buff":
            player.apply_buff(p_move)
            ai.apply_buff(a_move)
        elif a_type == "buff":
            ai.apply_buff(a_move)
        elif p_type == "buff":
            player.apply_buff(p_move)

        handle_reflect(p_move, a_move, player, ai)

        p_dmg, a_dmg = resolve(p_move, a_move, player.damage_bonus, ai.damage_bonus)
        p_hp_before, a_hp_before = player.hp, ai.hp
        player.take_damage(a_dmg)
        ai.take_damage(p_dmg)

        if p_type == "attack":
            player.damage_bonus = False
        if a_type == "attack":
            ai.damage_bonus = False

        show_round_result(p_move, a_move, player.hp - p_hp_before, ai.hp - a_hp_before)

        history.append({
            "round": round_num,
            "player_move": p_move,
            "ai_move": a_move,
            "player_hp": player.hp,
            "player_qi": player.qi,
            "player_shield": player.shield,
            "ai_hp": ai.hp,
            "ai_qi": ai.qi,
            "ai_shield": ai.shield,
        })

    player_won = ai.is_alive() == False and player.is_alive()
    show_result(player_won)
    save_history(player_won, history)
    return player_won
