from game import battle
from history import show_history, clear_history


def select_difficulty():
    print("\n选择难度:")
    print("  1. 简单 - AI随机出招")
    print("  2. 普通 - AI参考最近3次对战历史")
    print("  3. 困难 - AI参考最近6次对战历史，更智能")
    while True:
        try:
            diff = int(input("\n请选择难度 (1-3): "))
            if diff in (1, 2, 3):
                return diff
            print("请输入1-3")
        except ValueError:
            print("请输入数字")


def post_battle(diff):
    while True:
        print("\n  1. 再来一局")
        print("  2. 回到主菜单")
        while True:
            post = input("\n请选择: ").strip()
            if post in ("1", "2"):
                break
            print("请输入1或2")
        if post == "1":
            battle(diff)
        else:
            break


def main_menu():
    while True:
        print(f"\n{'='*50}")
        print("  自制游戏：卖肾")
        print(f"{'='*50}")
        print("  1. 开始游戏")
        print("  2. 查看历史记录")
        print("  3. 清除历史记录")
        print("  4. 退出")
        print(f"{'='*50}")

        choice = input("\n请选择: ").strip()

        if choice == "1":
            diff = select_difficulty()
            battle(diff)
            post_battle(diff)
        elif choice == "2":
            show_history()
        elif choice == "3":
            if input("确定要清除所有历史记录吗？(y/n): ").strip().lower() == "y":
                clear_history()
        elif choice == "4":
            print("再见！")
            break
        else:
            print("无效选择")


if __name__ == "__main__":
    main_menu()
