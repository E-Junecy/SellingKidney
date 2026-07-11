import math
import random
from moves import SKILLS
from fighter import get_available_moves


def _analyze_player(history, lookback=6):
    recent = history[-lookback:] if len(history) >= lookback else history
    if not recent:
        return 0, 0, 0, {}
    atk_count = sum(1 for h in recent if SKILLS[h["player_move"]]["type"] == "attack")
    heal_count = sum(1 for h in recent if SKILLS[h["player_move"]].get("effect") == "heal")
    atk_rate = atk_count / len(recent)
    heal_rate = heal_count / len(recent)
    tendencies = {}
    for h in recent:
        pm = h["player_move"]
        tendencies[pm] = tendencies.get(pm, 0) + 1
    return atk_rate, heal_rate, len(recent), tendencies


def _weighted_pick(scores, temperature=2.0):
    moves = list(scores.keys())
    vals = [scores[m] for m in moves]
    max_v = max(vals)
    exp_vals = [math.exp((v - max_v) / temperature) for v in vals]
    total = sum(exp_vals)
    weights = [e / total for e in exp_vals]
    return random.choices(moves, weights=weights, k=1)[0]


def ai_think(ai, player, history, difficulty):
    available = get_available_moves(ai)

    if difficulty == 1:
        return random.choice(available)

    if player.reflect_disabled and "破反" in available:
        available.remove("破反")

    player_max_atk_qi = 0
    for name, info in SKILLS.items():
        if info["type"] == "attack" and info["qi_cost"] > player_max_atk_qi:
            player_max_atk_qi = info["qi_cost"]
    if player_max_atk_qi < 3 and "超级防" in available:
        available.remove("超级防")

    atk_rate, heal_rate, sample_size, tendencies = _analyze_player(history, lookback=6 if difficulty == 3 else 3)

    last = history[-1] if history else None
    ai_lost_hp = False
    if last and len(history) > 1:
        ai_lost_hp = last.get("ai_hp", 1.0) < history[-2].get("ai_hp", 1.0)

    scores = {m: 0.0 for m in available}

    for move in available:
        m_type = SKILLS[move]["type"]

        if m_type == "attack":
            scores[move] += 1.0

            if sample_size == 0:
                scores[move] += 1.0
            else:
                if player.reflect_disabled:
                    scores[move] += 3.0
                else:
                    scores[move] -= 1.5

                has_higher_atk = False
                has_buff = False
                for pm in tendencies:
                    pm_type = SKILLS[pm]["type"]
                    if pm_type == "defend" and SKILLS[move]["qi_cost"] < SKILLS[pm].get("block_qi", 0):
                        scores[move] -= 2.0
                    elif pm == "反弹":
                        scores[move] -= 4.0
                    elif pm_type == "attack" and SKILLS[move]["qi_cost"] > SKILLS[pm]["qi_cost"]:
                        has_higher_atk = True
                    elif pm_type == "buff":
                        has_buff = True
                if has_higher_atk:
                    scores[move] += 3.0
                if has_buff:
                    scores[move] += 2.0

                if last and (last.get("player_move") == "治疗" or heal_rate > 0.4):
                    scores[move] += 3.0
                if last and last.get("player_move") and SKILLS[last["player_move"]]["type"] == "buff":
                    scores[move] += 2.0

        elif m_type == "defend":
            scores[move] += 0.5
            if ai.reflect_disabled:
                scores[move] += 3.0
            if sample_size > 0:
                for pm in tendencies:
                    if SKILLS[pm]["type"] == "attack":
                        scores[move] += 2.0

        elif move == "反弹":
            scores[move] += 0.5
            if not ai.reflect_disabled:
                if sample_size > 0:
                    if atk_rate > 0.5:
                        scores[move] += 5.0
                    elif atk_rate > 0.3:
                        scores[move] += 2.0
                    for pm in tendencies:
                        if SKILLS[pm]["type"] == "attack":
                            scores[move] += 3.0

        elif m_type == "buff":
            if move == "聚气":
                scores[move] += 1.0
                if sample_size == 0:
                    scores[move] += 3.0
                elif ai.reflect_disabled and ai.qi < 4:
                    scores[move] += 4.0
                elif atk_rate < 0.3 and heal_rate < 0.3:
                    scores[move] += 4.0
                elif ai.qi < 1:
                    scores[move] += 3.0
                elif ai.qi < 3:
                    scores[move] += 1.5
                if last and (last.get("player_move") == "治疗" or heal_rate > 0.4):
                    scores[move] += 4.0
            elif move == "叠盾":
                scores[move] += 0.5
                if ai.shield < 2:
                    scores[move] += 1.0
            elif move == "治疗":
                scores[move] += 0.5
                if ai.hp < 1.0:
                    scores[move] += 3.0
            elif move == "\u201c酒\u201d":
                scores[move] += 0.5
                if not ai.damage_bonus and ai.qi >= 2:
                    scores[move] += 2.0

        elif move == "破反":
            scores[move] += 0.5

    if last and ai_lost_hp:
        for move in available:
            m_type = SKILLS[move]["type"]
            if m_type == "buff" and move != "治疗":
                scores[move] -= 4.0
            elif m_type == "defend":
                scores[move] += 3.0
            elif move == "反弹" and not ai.reflect_disabled:
                scores[move] += 3.0
            elif m_type == "attack":
                scores[move] += 2.0

    if last and SKILLS[last["player_move"]]["type"] == "attack":
        for move in available:
            if SKILLS[move]["type"] == "buff" and move != "治疗":
                scores[move] -= 2.5

    return _weighted_pick(scores)
