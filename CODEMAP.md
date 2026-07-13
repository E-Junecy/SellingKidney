# 卖肾 - 代码地图

本文档记录每个文件、函数、数据结构的作用和行号，供 AI 快速定位修改点。

---

## 文件依赖关系

```
main.py ──→ game.py ──→ ai.py ──→ moves.py
                  │        │        fighter.py
                  │        │
                  ├──→ fighter.py
                  ├──→ history.py
                  ├──→ ui.py
                  └──→ console.py

minimax.py (预留，当前未被任何文件 import)
```

---

## moves.py — 招式数据定义（无逻辑，纯数据）

| 行号 | 变量 | 说明 |
|------|------|------|
| 1-14 | `SKILLS` | dict，key=招式名，value=dict。所有招式的属性定义在此处 |
| 16-22 | `SKILL_TYPES` | type 字段的中文映射 |

**SKILLS 每个条目的字段：**
- `type`: "attack" / "buff" / "defend" / "reflect" / "special"
- `qi_cost`: 气量消耗（int）
- `damage`: 伤害值（仅 attack 类型，float）
- `block_qi`: 防御阈值（仅 defend 类型，int，挡住 qi_cost < block_qi 的攻击）
- `effect`: buff 的具体效果 "qi" / "heal" / "shield" / "damage_boost"
- `value`: buff 的数值

**修改指南：**
- 新增招式：在 SKILLS dict 中加一条
- 改伤害/消耗/防御阈值：直接改对应字段
- 新增招式类型：在 SKILLS 和 SKILL_TYPES 都要加，同时需要在 game.py resolve() 和 ai.py 评分逻辑中处理

---

## fighter.py — Fighter 角色类

| 行号 | 内容 | 说明 |
|------|------|------|
| 4 | `class Fighter` | 玩家和 AI 共用同一个类 |
| 5-12 | `__init__` | 初始属性：hp=1.0, max_hp=2.0, qi=0, shield=0, reflect_cooldown=0, reflect_disabled=False, damage_bonus=False |
| 14-15 | `is_alive()` | 返回 hp > 0 |
| 17-23 | `take_damage(damage)` | 护盾优先吸收，剩余扣血。返回实际扣血量 |
| 25-26 | `heal(amount)` | 回血，不超过 max_hp |
| 28-37 | `apply_buff(move_name)` | 根据 SKILLS[effect] 执行增益：加气/回血/加盾/伤害+1 |
| 39-45 | `use_move(move_name)` | 扣气量；反弹设 cooldown=2 并立即 -1（即本回合用完，下回合不能用） |
| 48-57 | `get_available_moves(fighter)` | 返回当前可用招式列表。过滤条件：气量不足 / 反弹冷却中 / 反弹已失效 |

**修改指南：**
- 改初始属性：改 `__init__`
- 改回血上限：改 `heal()` 的 `min(self.max_hp, ...)`
- 改反弹冷却回合数：改 `use_move()` 第43行的 `= 2`（设为 N 则冷却 N-1 回合）
- 新增 buff 类型：在 `apply_buff()` 加 elif 分支

---

## game.py — 战斗核心逻辑

| 行号 | 内容 | 说明 |
|------|------|------|
| 15 | `JIU_WEIGHT = 1.2` | 酒增益在对攻时的等效气量加成 |
| 18-65 | `resolve(p_move, a_move, p_bonus, a_bonus)` | **核心回合结算函数**。返回 (p_dmg, a_dmg) 即双方受到的伤害。处理所有攻击对攻/攻击vs防御/攻击vs反弹/攻击vs特殊 的判定 |
| 68-72 | `handle_reflect(p_move, a_move, player, ai)` | 破反 vs 反弹的特殊处理：成功时设对方 reflect_disabled=True |
| 75-86 | `draw_battle_ui(player, ai, title)` | 绘制战斗界面框架（双方状态条 + 可选标题） |
| 89-153 | `get_player_move(player, ai)` | 招式选择菜单。支持滚动（max_visible=17）。返回选中的招式名 |
| 156-208 | `animate_round(...)` | 回合动画：血条平滑变化 + 结果文字。用 time.sleep 做动画帧 |
| 211-276 | `battle(difficulty)` | **战斗主循环**。每回合：玩家选招 → AI出招 → 扣气/加buff → handle_reflect → resolve结算 → 扣血/清增益 → 动画 → 记录历史。循环直到一方死亡。最后保存历史并显示结果 |

**resolve() 判定逻辑详解（18-65行）：**
1. 双方都是 attack：等效气量(实际气量+酒加成)高者胜，相同则抵消。胜者伤害 = 基础伤害 + 酒增益(+1)
2. 一方 attack 一方 defend：attack 的 qi_cost < defend 的 block_qi 时被挡住
3. 一方 attack 一方 reflect(反弹)：攻击方伤害反弹给攻击方自己（即攻击方受伤）
4. 一方 attack 一方 special(破反)：攻击直接命中，破反不影响攻击
5. 以上都不满足（都是非攻击招式）：无事发生

**battle() 每回合执行顺序（227-270行）：**
1. get_player_move → ai_think 获取双方招式
2. use_move → 扣气 + 反弹冷却
3. apply_buff → buff 类招式生效
4. handle_reflect → 破反判定
5. resolve → 伤害计算
6. take_damage → 实际扣血
7. 清除 damage_bonus（攻击招式用完就消失）
8. animate_round → 动画显示
9. 追加到 history

**修改指南：**
- 改对攻判定规则：改 resolve() 22-33行
- 改防御判定：改 resolve() 35-43行（注意 block_qi 用的是 `<` 不是 `<=`）
- 改反弹逻辑：改 resolve() 45-51行 + handle_reflect()
- 改每回合执行顺序：改 battle() 235-258行
- 改战斗 UI 布局：改 draw_battle_ui() + animate_round()
- 改动画速度：改 animate_round() 的 time.sleep 参数
- 改招式选择菜单：改 get_player_move()

---

## ai.py — AI 策略

| 行号 | 内容 | 说明 |
|------|------|------|
| 7-19 | `_analyze_player(history, lookback)` | 分析玩家最近 N 回合倾向：攻击率、治疗率、各招式使用次数 |
| 22-29 | `_weighted_pick(scores, temperature)` | Softmax 采样：按 scores 加权随机选取招式，temperature 越大越随机 |
| 32-162 | `ai_think(ai, player, history, difficulty)` | **AI 主决策函数**。根据 difficulty 走不同策略 |

**ai_think() 详细逻辑：**
- **difficulty=1（简单）**：第35-36行，直接 random.choice，完全随机
- **difficulty=2（普通）**：lookback=3，分析最近3回合
- **difficulty=3（困难）**：lookback=6，分析最近6回合。注意：**未使用 minimax**

**评分系统（55-161行）：**
为每个可用招式计算 score，最后用 Softmax 选一个：
- **攻击类**（60-91行）：基础+1分；考虑玩家是否用反弹(-4)、防御(-2)、是否有更高攻击(+3)、玩家是否在治疗(+3)、玩家上回合用buff(+2)
- **防御类**（93-100行）：反弹失效时+3；玩家偏好攻击时+2
- **反弹**（102-112行）：玩家攻击率>0.5 时+5，>0.3 时+2
- **聚气**（115-128行）：无数据时+3；缺气时+3~4；玩家治疗时+4
- **叠盾/治疗/酒**（129-140行）：各自条件
- **破反**（142-143行）：基础+0.5
- **被打了的修正**（145-155行）：上回合掉血 → 降低非治疗buff、提高防御/反弹/攻击
- **玩家上回合攻击修正**（157-160行）：降低非治疗buff

**修改指南：**
- 改 AI 难度差异：改 lookback 参数（第48行）
- 改某个招式的 AI 偏好权重：改对应 score += 的值
- 新增招式 AI 逻辑：在 scores 字典初始化后加对应 elif 分支
- 改采样随机性：改 _weighted_pick 的 temperature 参数（默认2.0）
- 如果要集成 minimax：需要在 ai_think 中 difficulty==3 时调用 minimax.find_best_move()

---

## minimax.py — Minimax 搜索（预留，未集成）

| 行号 | 内容 | 说明 |
|------|------|------|
| 4-37 | `class GameState` | 轻量游戏状态，用 __slots__ 优化内存。完整复制当前战斗状态 |
| 40-49 | `get_moves(qi, reflect_cd, reflect_disabled)` | 类似 fighter.py 的 get_available_moves，但不依赖 Fighter 对象 |
| 52-154 | `simulate(state, ai_move, player_move)` | 模拟一回合，返回新 GameState。逻辑与 game.py resolve() 基本一致 |
| 157-202 | `evaluate(state)` | 评估函数：返回分数（正=AI优势）。考虑血量差、气量差、护盾差、反弹状态、酒增益、玩家倾向 |
| 205-280 | `minimax(state, depth, alpha, beta, is_ai_turn)` | Alpha-Beta 剪枝搜索。AI层取max，玩家层取avg（按倾向加权） |
| 283-285 | `find_best_move(state, depth)` | 入口：调用 minimax 返回最优招式 |
| 288-320 | `state_from_fighter(ai, player, player_tendencies)` | 将 Fighter 对象转为 GameState |

**修改指南：**
- 改评估权重：改 evaluate() 的各项系数
- 改搜索深度：改 find_best_move 的 depth 参数（默认3）
- 集成到 ai.py：在 ai_think 中 difficulty==3 时调用 `from minimax import state_from_fighter, find_best_move`，将 state 传入

---

## console.py — 控制台底层操作（Windows 专用）

| 行号 | 内容 | 说明 |
|------|------|------|
| 9-17 | 颜色常量 | R/RED/GRN/YLW/BLU/MAG/CYN/WHT/DIM，ANSI 转义码 |
| 43-44 | `COLS=120, ROWS=30` | 控制台窗口尺寸常量，影响所有 UI 布局 |
| 47-68 | `init_console()` | 设置 UTF-8 编码、窗口大小、启用 VT100、隐藏光标 |
| 71-72 | `cls()` | 清屏 |
| 75-78 | `gotoxy(x, y)` | 移动光标到指定坐标 |
| 81-83 | `write_at(x, y, text)` | 在指定位置打印 |
| 86-88 | `clear_line(y)` | 清空一行 |
| 91-98 | `draw_rect(x1, y1, x2, y2)` | 画矩形边框（Unicode box drawing） |
| 101-116 | `draw_hp_bar(...)` | 生成血条字符串：彩色方块 + 护盾标记 + 数值 |
| 119-121 | `draw_stats_left(...)` | 左对齐状态栏（AI 用） |
| 124-129 | `draw_stats_right(...)` | 右对齐状态栏（玩家用） |
| 132-140 | `get_stats_tags(fighter)` | 生成状态标签：[反弹冷却] / [反弹失效] / [伤害+1] |
| 153-170 | `get_key()` | 读取按键，返回 "up"/"down"/"left"/"right"/"enter"/"esc"/字符 |
| 173-176 | `pause_at(x, y)` | 在指定位置显示"按任意键"并等待 |
| 179-180 | `strip_ansi(text)` | 去除 ANSI 颜色码，用于计算可见文本长度 |

**修改指南：**
- 改窗口尺寸：改 COLS/ROWS（第43-44行），同时需要改 init_console() 的缓冲区设置
- 改颜色方案：改第9-17行的 ANSI 码
- 改按键绑定：改 get_key() 返回值映射
- 改血条样式：改 draw_hp_bar() 的字符和逻辑

---

## ui.py — 游戏 UI 展示

| 行号 | 内容 | 说明 |
|------|------|------|
| 10-29 | `get_move_desc(name)` | 返回招式的彩色描述文字（供招式选择菜单显示） |
| 32-49 | `show_result(player_won, filepath)` | 战斗结束结果画面：显示输赢 + 历史保存提示 |

**修改指南：**
- 改招式描述文字：改 get_move_desc() 对应分支
- 改结果画面：改 show_result()

---

## history.py — 历史记录管理

| 行号 | 内容 | 说明 |
|------|------|------|
| 11-12 | `HISTORY_DIR` | history/ 目录路径，自动创建 |
| 15-28 | `save_history(player_won, history)` | 保存对战记录到文件。文件名：时间_win/lose.txt |
| 31-74 | `show_history()` | 分页显示历史记录文件列表（page_size=22） |
| 77-89 | `clear_history()` | 删除所有历史记录 |

**修改指南：**
- 改文件名格式：改 save_history() 第16行的 strftime
- 改文件内容格式：改 save_history() 第20-25行的 lines 拼接
- 改分页大小：改 show_history() 第44行的 page_size

---

## main.py — 入口 / 主菜单

| 行号 | 内容 | 说明 |
|------|------|------|
| 9-71 | `main_menu()` | 主菜单循环：开始游戏/查看历史/清除历史/退出 |
| 73-132 | `select_difficulty()` | 难度选择界面（简单/普通/困难），含 ASCII art |
| 135-166 | `post_battle(diff)` | 战后菜单：再来一局/回到主菜单 |
| 169-196 | `confirm_dialog(msg)` | 确认弹窗（是/否） |

**修改指南：**
- 改菜单选项：改 main_menu() 的 options 列表
- 改 ASCII art：改 select_difficulty() 的 art 列表
- 改版本号：改第41行的 "v1.0 beta"

---

## 关键设计约束

1. **仅 Windows**：console.py 依赖 msvcrt 和 kernel32，不兼容 Linux/Mac
2. **控制台尺寸固定**：COLS=120 ROWS=30，所有 UI 坐标硬编码，改尺寸需要全局调整
3. **minimax.py 未集成**：hard 难度实际只比 normal 多看了3回合历史，minimax 是预留代码
4. **酒增益双重作用**：伤害+1（damage_bonus）+ 对攻时等效气量+1.2（JIU_WEIGHT），两者独立
5. **反弹冷却机制**：use_move 设 cooldown=2 然后立即 -1，所以实际冷却1回合。get_available_moves 检查 cooldown > 0
6. **防御判定用 <**：attack 的 qi_cost 必须 < block_qi 才被挡住（等于时攻击穿透）
7. **resolve() 和 minimax simulate() 是重复实现**：改回合结算规则时两处都要改
8. **buff 先结算再 resolve**：battle() 中 apply_buff 在 resolve 之前调用，所以酒的 damage_bonus 在当回合 resolve 时就生效
9. **招式名含 Unicode 引号**：`"嘣"` `"劈"` `"砍"` `"酒"` 用的是中文全角引号 `\u201c\u201d`
