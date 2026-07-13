from moves import SKILLS
from fighter import Fighter, get_available_moves
from ai import ai_think
from history import save_history
from ui import show_result
from console import (
    cls, gotoxy, write_at, clear_line, get_key, pause_at, draw_rect,
    draw_hp_bar, draw_stats_left, draw_stats_right, get_stats_tags,
    strip_ansi, COLS, ROWS, R, GRN, YLW, BLU, RED, DIM, WHT
)
import time
import msvcrt


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
        if a_move == "\u53cd\u5f39":
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
    if p_move == "\u7834\u53cd" and a_move == "\u53cd\u5f39":
        ai.reflect_disabled = True
    elif a_move == "\u7834\u53cd" and p_move == "\u53cd\u5f39":
        player.reflect_disabled = True


def draw_battle_ui(player, ai, title=None):
    cls()
    ai_tags = get_stats_tags(ai)
    p_tags = get_stats_tags(player)

    draw_stats_left(1, 1, f"{RED}AI{R}", ai.hp, ai.max_hp, ai.shield, ai.qi, ai_tags)
    draw_stats_right(1, ROWS - 2, f"{BLU}玩家{R}", player.hp, player.max_hp, player.shield, player.qi, p_tags)

    if title:
        title_clean = strip_ansi(title)
        gotoxy((COLS - len(title_clean)) // 2, 13)
        print(title)


def get_player_move(player, ai):
    available = get_available_moves(player)
    items = []
    descs = []
    for name in available:
        info = SKILLS[name]
        cost = info["qi_cost"]
        cost_str = f" ({cost}气)" if cost > 0 else ""
        items.append(f"{name}{cost_str}")
        from ui import get_move_desc
        descs.append(get_move_desc(name))

    sel = 0
    scroll = 0
    max_visible = 17

    while True:
        draw_battle_ui(player, ai)

        start_y = 4
        gotoxy((COLS - 10) // 2, 3)
        print(f"{BLU}选择招式{R}")

        visible = items[scroll:scroll + max_visible]
        visible_descs = descs[scroll:scroll + max_visible]

        for i, (item, desc) in enumerate(zip(visible, visible_descs)):
            y = start_y + i
            idx = scroll + i
            if idx == sel:
                gotoxy(15, y)
                print(f"{GRN}>>> {item}{R}")
                gotoxy(65, y)
                print(f"{desc}")
            else:
                gotoxy(15, y)
                print(f"    {item}")
                gotoxy(65, y)
                print(f"{DIM}{desc}{R}")

        if scroll > 0:
            gotoxy(15, start_y - 1)
            print(f"{DIM}  ▲ 还有上面的...{R}")
        if scroll + max_visible < len(items):
            gotoxy(15, start_y + max_visible)
            print(f"{DIM}  ▼ 还有下面的...{R}")

        gotoxy(1, ROWS - 1)
        print(f"{DIM}↑↓ 移动  Enter 确认  Esc 取消{R}")

        key = get_key()
        if key == "up":
            if sel > 0:
                sel -= 1
                if sel < scroll:
                    scroll = sel
        elif key == "down":
            if sel < len(items) - 1:
                sel += 1
                if sel >= scroll + max_visible:
                    scroll = sel - max_visible + 1
        elif key == "enter":
            return available[sel]
        elif key == "esc":
            return available[0]


def animate_round(p_move, a_move, player, ai, p_hp_change, a_hp_change):
    ai_tags = get_stats_tags(ai)
    p_tags = get_stats_tags(player)

    p_hp_before = player.hp - p_hp_change
    a_hp_before = ai.hp - a_hp_change

    cls()

    bar_ai_y = 1
    bar_p_y = ROWS - 2

    gotoxy(1, bar_ai_y)
    print(f"{RED}AI{R}  HP {draw_hp_bar(a_hp_before, ai.max_hp, ai.shield)}  Qi={ai.qi}{ai_tags}", end="", flush=True)
    gotoxy(1, bar_p_y)
    print(f"{BLU}玩家{R}  HP {draw_hp_bar(p_hp_before, player.max_hp, player.shield)}  Qi={player.qi}{p_tags}", end="", flush=True)

    title = f"{p_move}  vs  {a_move}"
    gotoxy((COLS - len(p_move) - 7 + len(a_move)) // 2, 13)
    print(f"{BLU}{p_move}{R}  vs  {RED}{a_move}{R}", end="", flush=True)

    time.sleep(0.3)

    steps = 8
    for step in range(1, steps + 1):
        time.sleep(0.05)
        p_now = p_hp_before + p_hp_change * step / steps
        a_now = a_hp_before + a_hp_change * step / steps
        gotoxy(1, bar_ai_y)
        clear_line(bar_ai_y)
        print(f"{RED}AI{R}  HP {draw_hp_bar(a_now, ai.max_hp, ai.shield)}  Qi={ai.qi}{ai_tags}", end="", flush=True)
        gotoxy(1, bar_p_y)
        clear_line(bar_p_y)
        print(f"{BLU}玩家{R}  HP {draw_hp_bar(p_now, player.max_hp, player.shield)}  Qi={player.qi}{p_tags}", end="", flush=True)

    msg = ""
    if p_hp_change < 0:
        msg = f"{RED}玩家受到{abs(p_hp_change):.1f}点伤害{R}"
    elif a_hp_change < 0:
        msg = f"{RED}AI受到{abs(a_hp_change):.1f}点伤害{R}"
    elif p_move == "\u7834\u53cd" and a_move == "\u53cd\u5f39":
        msg = f"{MAG}AI永久失去了反弹能力{R}"
    elif a_move == "\u7834\u53cd" and p_move == "\u53cd\u5f39":
        msg = f"{MAG}玩家永久失去了反弹能力{R}"
    else:
        msg = f"{DIM}无事发生{R}"

    gotoxy((COLS - len(strip_ansi(msg))) // 2, 15)
    print(msg, end="", flush=True)

    gotoxy(1, ROWS - 1)
    print(f"{DIM}按任意键继续{R}", end="", flush=True)
    msvcrt.getch()


def battle(difficulty):
    player = Fighter()
    ai = Fighter()
    history = []
    round_num = 0

    diff_names = {1: "简单", 2: "普通", 3: "困难"}
    cls()
    draw_rect(10, 10, COLS - 11, 18)
    gotoxy((COLS - 20) // 2, 13)
    print(f"{BLU}对战开始！难度: {diff_names[difficulty]}{R}")

    gotoxy(1, ROWS - 1)
    print(f"{DIM}按任意键开始{R}", end="", flush=True)
    msvcrt.getch()

    while player.is_alive() and ai.is_alive():
        round_num += 1
        p_move = get_player_move(player, ai)
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

        animate_round(p_move, a_move, player, ai, player.hp - p_hp_before, ai.hp - a_hp_before)

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
    filepath = save_history(player_won, history)
    show_result(player_won, filepath)
    pause_at(1, ROWS - 1)
    return player_won
