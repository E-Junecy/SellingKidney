from datetime import datetime
from pathlib import Path
import sys

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

    lines = [f"对战结果: {'玩家胜利' if player_won else 'AI胜利'}", f"时间: {now}", ""]
    for i, h in enumerate(history, 1):
        lines.append(f"第{i}回合: 玩家={h['player_move']} | AI={h['ai_move']}")
        lines.append(f"  玩家: HP={h['player_hp']:.1f} Qi={h['player_qi']} Shield={h['player_shield']}")
        lines.append(f"  AI:   HP={h['ai_hp']:.1f} Qi={h['ai_qi']} Shield={h['ai_shield']}")
        lines.append("")

    filepath.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n对战记录已保存到: {filepath}")


def show_history():
    files = sorted(HISTORY_DIR.glob("*.txt"))
    if not files:
        print("暂无历史记录")
        return
    print(f"\n共 {len(files)} 条历史记录:")
    for f in files:
        print(f"  {f.name}")


def clear_history():
    files = list(HISTORY_DIR.glob("*.txt"))
    if not files:
        print("没有历史记录可清除")
        return
    for f in files:
        f.unlink()
    print(f"已清除 {len(files)} 条历史记录")
