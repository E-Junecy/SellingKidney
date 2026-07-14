from moves import SKILLS
from console import (
    cls, gotoxy, draw_rect,
    COLS, ROWS, R, GRN, YLW, BLU, RED, DIM, CYN, MAG
)
import msvcrt


def get_move_desc(name):
    info = SKILLS[name]
    if info["type"] == "attack":
        return f"{RED}造成{info['damage']}点伤害{R}"
    elif info["type"] == "buff":
        if info["effect"] == "qi":
            return f"{YLW}气量+1{R}"
        elif info["effect"] == "heal":
            return f"{GRN}血量+0.5{R}"
        elif info["effect"] == "shield":
            return f"{CYN}护盾+1{R}"
        elif info["effect"] == "damage_boost":
            return f"{MAG}下次攻击伤害+1{R}"
    elif info["type"] == "defend":
        return f"{BLU}挡住<{info['block_qi']}气的攻击{R}"
    elif info["type"] == "reflect":
        return f"{YLW}反弹伤害，冷却1回合{R}" if name == "反弹" else f"{MAG}永久禁用敌方反弹{R}"
    elif info["type"] == "special":
        return f"{MAG}永久禁用敌方反弹{R}"
    return ""


def show_result(player_won, filepath=None):
    cls()

    draw_rect(10, 8, COLS - 11, 18)

    gotoxy((COLS - 16) // 2, 11)
    if player_won:
        print(f"{GRN}★ 恭喜！你赢了！ ★{R}")
    else:
        print(f"{RED}☆ 你输了... ☆{R}")

    if filepath:
        gotoxy((COLS - 16) // 2, 14)
        print(f"{DIM}对战记录已计入历史{R}")

    gotoxy(1, ROWS - 1)
    print(f"{DIM}按任意键返回{R}", end="", flush=True)
    msvcrt.getch()
