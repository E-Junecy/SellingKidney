import os
import msvcrt
import ctypes
import time
import re

kernel32 = ctypes.windll.kernel32

R = "\033[0m"
RED = "\033[91m"
GRN = "\033[92m"
YLW = "\033[93m"
BLU = "\033[94m"
MAG = "\033[95m"
CYN = "\033[96m"
WHT = "\033[97m"
DIM = "\033[90m"


class COORD(ctypes.Structure):
    _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]


class SMALL_RECT(ctypes.Structure):
    _fields_ = [("Left", ctypes.c_short), ("Top", ctypes.c_short),
                 ("Right", ctypes.c_short), ("Bottom", ctypes.c_short)]


class CONSOLE_CURSOR_INFO(ctypes.Structure):
    _fields_ = [("dwSize", ctypes.c_ulong), ("bVisible", ctypes.c_bool)]


class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
    _fields_ = [
        ("dwSize", COORD),
        ("dwCursorPosition", COORD),
        ("wAttributes", ctypes.c_ushort),
        ("srWindow", SMALL_RECT),
        ("dwMaximumWindowSize", COORD),
    ]


COLS = 120
ROWS = 30


def init_console():
    kernel32.SetConsoleOutputCP(65001)
    kernel32.SetConsoleCP(65001)
    handle = kernel32.GetStdHandle(-11)

    # 1. 先设置缓冲区大小为 120×30
    buf_size = COORD(ctypes.c_short(COLS), ctypes.c_short(ROWS))
    kernel32.SetConsoleScreenBufferSize(handle, buf_size)

    # 2. 再设置窗口大小为 120×30
    window_rect = SMALL_RECT(ctypes.c_short(0), ctypes.c_short(0),
                              ctypes.c_short(COLS - 1), ctypes.c_short(ROWS - 1))
    kernel32.SetConsoleWindowInfo(handle, True, ctypes.byref(window_rect))

    # 3. 启用虚拟终端处理（ANSI 转义序列支持）
    mode = ctypes.c_ulong()
    kernel32.GetConsoleMode(handle, ctypes.byref(mode))
    kernel32.SetConsoleMode(handle, mode.value | 0x0004)

    # 4. 隐藏光标
    ci = CONSOLE_CURSOR_INFO(1, False)
    kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))


def cls():
    os.system("cls")


def gotoxy(x, y):
    handle = kernel32.GetStdHandle(-11)
    coord = COORD(ctypes.c_short(x), ctypes.c_short(y))
    kernel32.SetConsoleCursorPosition(handle, coord)


def write_at(x, y, text):
    gotoxy(x, y)
    print(text, end="", flush=True)


def clear_line(y, width=COLS):
    gotoxy(0, y)
    print(" " * width, end="", flush=True)


def draw_rect(x1, y1, x2, y2):
    gotoxy(x1, y1)
    print("\u2554" + "\u2550" * (x2 - x1 - 1) + "\u2557")
    for y in range(y1 + 1, y2):
        gotoxy(x1, y)
        print("\u2551" + " " * (x2 - x1 - 1) + "\u2551")
    gotoxy(x1, y2)
    print("\u255a" + "\u2550" * (x2 - x1 - 1) + "\u255d")


def draw_hp_bar(current, maximum, shield=0, length=20):
    ratio = max(0, current / maximum) if maximum > 0 else 0
    filled = int(ratio * length)
    empty = length - filled
    if ratio > 0.6:
        color = GRN
    elif ratio > 0.3:
        color = YLW
    else:
        color = RED
    shield_str = ""
    if shield > 0:
        full = int(shield)
        half = 1 if shield % 1 >= 0.5 else 0
        shield_str = f" {WHT}{'■' * full}{DIM}{'░' * half}{R}"
    return f"{color}{'█' * filled}{'░' * empty}{R}{shield_str} {current:.1f}/{maximum:.1f}"


def draw_stats_left(x, y, label, hp, max_hp, shield, qi, tags=""):
    tag_str = " " + tags if tags else ""
    write_at(x, y, f"{label}  HP {draw_hp_bar(hp, max_hp, shield)}  Qi={qi}{tag_str}")


def draw_stats_right(x, y, label, hp, max_hp, shield, qi, tags=""):
    tag_str = " " + tags if tags else ""
    text = f"HP {draw_hp_bar(hp, max_hp, shield)}  Qi={qi}{tag_str}  {label}"
    visible_len = len(strip_ansi(text))
    gotoxy(max(0, COLS - visible_len - 2), y)
    print(text, end="", flush=True)


def get_stats_tags(fighter):
    tags = []
    if fighter.reflect_cooldown > 0:
        tags.append(f"{YLW}[反弹冷却]{R}")
    elif fighter.reflect_disabled:
        tags.append(f"{RED}[反弹失效]{R}")
    if fighter.damage_bonus:
        tags.append(f"{MAG}[伤害+1]{R}")
    return "".join(tags)


def draw_ai_stats(y=1):
    clear_line(y)
    clear_line(y + 1)


def draw_player_stats(y=28):
    clear_line(y)
    clear_line(y + 1)


def get_key():
    ch = msvcrt.getch()
    if ch in (b'\x00', b'\xe0'):
        ch2 = msvcrt.getch()
        if ch2 == b'H':
            return "up"
        elif ch2 == b'P':
            return "down"
        elif ch2 == b'K':
            return "left"
        elif ch2 == b'M':
            return "right"
        return "unknown"
    if ch == b'\r':
        return "enter"
    if ch == b'\x1b':
        return "esc"
    return ch.decode("utf-8", errors="ignore")


def pause_at(x, y, msg="按任意键返回"):
    gotoxy(x, y)
    print(msg, end="", flush=True)
    msvcrt.getch()


def strip_ansi(text):
    return re.sub(r'\033\[[0-9;]*m', '', text)
