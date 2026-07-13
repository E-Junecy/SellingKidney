from datetime import datetime
from pathlib import Path
import sys
from console import cls, gotoxy, pause_at, strip_ansi, COLS, ROWS, R, DIM

if getattr(sys, 'frozen', False):
    _BASE = Path(sys.executable).parent
else:
    _BASE = Path(__file__).parent

HISTORY_DIR = _BASE / "history"
HISTORY_DIR.mkdir(exist_ok=True)


def save_history(player_won, history):
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    result = "win" if player_won else "lose"
    filepath = HISTORY_DIR / f"{now}_{result}.txt"

    lines = ["\u5bf9\u6218\u7ed3\u679c: " + ("\u73a9\u5bb6\u80dc\u5229" if player_won else "AI\u80dc\u5229"), f"\u65f6\u95f4: {now}", ""]
    for i, h in enumerate(history, 1):
        lines.append(f"\u7b2c{i}\u56de\u5408: \u73a9\u5bb6={h['player_move']} | AI={h['ai_move']}")
        lines.append(f"  \u73a9\u5bb6: HP={h['player_hp']:.1f} Qi={h['player_qi']} Shield={h['player_shield']}")
        lines.append(f"  AI:   HP={h['ai_hp']:.1f} Qi={h['ai_qi']} Shield={h['ai_shield']}")
        lines.append("")

    filepath.write_text("\n".join(lines), encoding="utf-8")
    return filepath


def show_history():
    cls()
    files = sorted(HISTORY_DIR.glob("*.txt"))
    if not files:
        gotoxy((COLS - 12) // 2, 14)
        print(f"{DIM}\u6682\u65e0\u5386\u53f2\u8bb0\u5f55{R}")
        pause_at(1, ROWS - 1)
        return

    gotoxy((COLS - 20) // 2, 2)
    print(f"\u5171 {len(files)} \u6761\u5386\u53f2\u8bb0\u5f55:")

    start_y = 4
    page_size = 22
    page = 0
    total_pages = (len(files) + page_size - 1) // page_size

    while True:
        cls()
        gotoxy((COLS - 20) // 2, 2)
        print(f"\u5171 {len(files)} \u6761\u5386\u53f2\u8bb0\u5f55:")

        page_files = files[page * page_size:(page + 1) * page_size]
        for i, f in enumerate(page_files):
            gotoxy(5, start_y + i)
            print(f"  {f.name}")

        gotoxy(1, ROWS - 1)
        if total_pages > 1:
            print(f"{DIM}\u2190\u2192 \u7ffb\u9875  Esc \u8fd4\u56de{R}", end="", flush=True)
        else:
            print(f"{DIM}\u6309\u4efb\u610f\u952e\u8fd4\u56de{R}", end="", flush=True)

        key = __import__("msvcrt").getch()
        if key == b'\x1b':
            break
        elif key in (b'\x00', b'\xe0'):
            ch2 = __import__("msvcrt").getch()
            if ch2 == b'M' and page < total_pages - 1:
                page += 1
            elif ch2 == b'K' and page > 0:
                page -= 1
        else:
            break


def clear_history():
    cls()
    files = list(HISTORY_DIR.glob("*.txt"))
    if not files:
        gotoxy((COLS - 16) // 2, 14)
        print(f"{DIM}\u6ca1\u6709\u5386\u53f2\u8bb0\u5f55\u53ef\u6e05\u9664{R}")
        pause_at(1, ROWS - 1)
        return
    for f in files:
        f.unlink()
    gotoxy((COLS - 20) // 2, 14)
    print(f"\u5df2\u6e05\u9664 {len(files)} \u6761\u5386\u53f2\u8bb0\u5f55")
    pause_at(1, ROWS - 1)
