from game import battle
from history import show_history, clear_history
from console import (
    init_console, cls, gotoxy, write_at, clear_line, draw_rect,
    get_key, pause_at, COLS, ROWS, R, GRN, YLW, BLU, RED, DIM, WHT
)


def main_menu():
    global selected
    init_console()
    selected = 0
    options = [
        "开始游戏",
        "查看历史记录",
        "清除历史记录",
        "退出",
    ]
    while True:
        cls()
        title = "卖肾 - 回合制对战游戏"
        draw_rect(2, 0, COLS - 3, 4)
        gotoxy((COLS - len(title)) // 2, 2)
        print(f"{BLU}{title}{R}")

        draw_rect(10, 6, COLS - 11, 9)
        gotoxy((COLS - 10) // 2, 7)
        print(f"{DIM}选择你的命运{R}")

        start_y = 11
        for i, opt in enumerate(options):
            y = start_y + i * 4
            draw_rect(10, y, COLS - 11, y + 2)
            gotoxy(12, y + 1)
            if i == selected:
                print(f"{GRN}>>> {opt} <<<{R}")
            else:
                print(f"    {opt}")

        gotoxy(1, ROWS - 1)
        print(f"{DIM}v1.0 beta{R}")
        gotoxy(COLS - 30, ROWS - 1)
        print(f"{DIM}↑↓ 移动  Enter 确认  Esc 退出{R}")

        key = get_key()
        if key == "up" and selected > 0:
            selected -= 1
        elif key == "down" and selected < len(options) - 1:
            selected += 1
        elif key == "enter":
            if selected == 0:
                diff = select_difficulty()
                if diff is not None:
                    battle(diff)
                    post_battle(diff)
            elif selected == 1:
                show_history()
            elif selected == 2:
                confirm = confirm_dialog("确定要清除所有历史记录？")
                if confirm:
                    clear_history()
            elif selected == 3:
                cls()
                gotoxy((COLS - 6) // 2, ROWS // 2)
                print("再见！")
                break
        elif key == "esc":
            cls()
            gotoxy((COLS - 6) // 2, ROWS // 2)
            print("再见！")
            break

def select_difficulty():
    global selected
    selected = 0
    options = ["简单", "普通", "困难"]
    descs = [
        "AI随机出招",
        "AI参考最近3次对战历史",
        "AI参考最近6次对战历史，更智能",
    ]
    art = [
        "╭ ◜◝  ͡  ◜  ╮",
        "(    诶！   )",
        "╰ ◟ ͜ ╭◜◝  ͡ ◜  ͡ ◝ ╮",
        "    (    云朵!   )",
        "╭◜◝  ͡ ◜◝ ͡   ◜ ╮◞ ╯",
        "(   哒哒哒哒哒  )",
        "╰◟  ͜ ◞  ͜ ◟ ͜  ◞◞╯ ╭◜◝ ͡  ◜  ͡ ◝ ◝ ͡   ◜╮",
        "                (     好想玩原神    )",
        "╭◜◝ ͡  ◜◝ ͡   ◜ ╮ ╰◟ ◞ ͜  ◟ ͜  ◞◞ ͜  ◟ ╯",
        "(     云原神！  )",
        "╰◟ ͜  ◞ ͜  ◟ ͜  ◞◞╯",
        "₍ᐢ..ᐢ₎ᐝ",
    ]
    while True:
        cls()
        for i, line in enumerate(art):
            gotoxy((COLS - 50) // 2 + 5, 6 + i)
            print(f"{DIM}{line}{R}")

        gotoxy((COLS - 20) // 2, 1)
        print(f"{BLU}═══ 选择难度 ═══{R}")

        opt_y = 22
        box_w = 34
        gap = 2
        total_w = 3 * box_w + 2 * gap
        start_x = (COLS - total_w) // 2
        for i, (opt, desc) in enumerate(zip(options, descs)):
            x = start_x + i * (box_w + gap)
            draw_rect(x, opt_y, x + box_w, opt_y + 3)
            gotoxy(x + 2, opt_y + 1)
            if i == selected:
                print(f"{GRN}▶ {opt}{R}")
            else:
                print(f"  {opt}")
            gotoxy(x + 2, opt_y + 2)
            print(f"{DIM}{desc}{R}")

        gotoxy(1, ROWS - 1)
        print(f"{DIM}← → 切换  Enter 确认  Esc 返回{R}")

        key = get_key()
        if key == "left":
            selected = (selected - 1) % 3
        elif key == "right":
            selected = (selected + 1) % 3
        elif key == "enter":
            return selected + 1
        elif key == "esc":
            return None


def post_battle(diff):
    options = ["再来一局", "回到主菜单"]
    sel = 0
    while True:
        cls()
        gotoxy((COLS - 16) // 2, 10)
        print(f"{BLU}═══ 对战结束 ═══{R}")

        for i, opt in enumerate(options):
            y = 14 + i * 4
            draw_rect(10, y, COLS - 11, y + 2)
            gotoxy(12, y + 1)
            if i == sel:
                print(f"{GRN}>>> {opt} <<<{R}")
            else:
                print(f"    {opt}")

        gotoxy(1, ROWS - 1)
        print(f"{DIM}↑↓ 移动  Enter 确认{R}")

        key = get_key()
        if key == "up" and sel > 0:
            sel -= 1
        elif key == "down" and sel < len(options) - 1:
            sel += 1
        elif key == "enter":
            if sel == 0:
                battle(diff)
            else:
                break
        elif key == "esc":
            break


def confirm_dialog(msg):
    sel = 0
    while True:
        cls()
        draw_rect(10, 10, COLS - 11, 16)
        gotoxy((COLS - len(msg)) // 2, 12)
        print(msg)

        for i, opt in enumerate(["是", "否"]):
            x = (COLS // 2) - 16 + i * 32
            gotoxy(x, 14)
            if i == sel:
                print(f"{GRN}[{opt}]{R}")
            else:
                print(f" {opt} ")

        gotoxy(1, ROWS - 1)
        print(f"{DIM}← → 切换  Enter 确认{R}")

        key = get_key()
        if key == "left":
            sel = (sel - 1) % 2
        elif key == "right":
            sel = (sel + 1) % 2
        elif key == "enter":
            return sel == 0
        elif key == "esc":
            return False


if __name__ == "__main__":
    main_menu()
