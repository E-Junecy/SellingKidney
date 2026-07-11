from moves import SKILLS


class GameState:
    __slots__ = ("ai_hp", "ai_qi", "ai_shield", "ai_reflect_cd", "ai_reflect_disabled", "ai_damage_bonus",
                 "player_hp", "player_qi", "player_shield", "player_reflect_cd", "player_reflect_disabled",
                 "player_damage_bonus", "player_atk_tendency", "player_def_tendency", "player_buf_tendency")

    def __init__(self, ai_hp=1.0, ai_qi=0, ai_shield=0, ai_reflect_cd=0, ai_reflect_disabled=False,
                 ai_damage_bonus=False,
                 player_hp=1.0, player_qi=0, player_shield=0, player_reflect_cd=0, player_reflect_disabled=False,
                 player_damage_bonus=False,
                 player_atk_tendency=0.0, player_def_tendency=0.0, player_buf_tendency=0.0):
        self.ai_hp = ai_hp
        self.ai_qi = ai_qi
        self.ai_shield = ai_shield
        self.ai_reflect_cd = ai_reflect_cd
        self.ai_reflect_disabled = ai_reflect_disabled
        self.ai_damage_bonus = ai_damage_bonus
        self.player_hp = player_hp
        self.player_qi = player_qi
        self.player_shield = player_shield
        self.player_reflect_cd = player_reflect_cd
        self.player_reflect_disabled = player_reflect_disabled
        self.player_damage_bonus = player_damage_bonus
        self.player_atk_tendency = player_atk_tendency
        self.player_def_tendency = player_def_tendency
        self.player_buf_tendency = player_buf_tendency

    def copy(self):
        return GameState(
            self.ai_hp, self.ai_qi, self.ai_shield, self.ai_reflect_cd, self.ai_reflect_disabled,
            self.ai_damage_bonus,
            self.player_hp, self.player_qi, self.player_shield, self.player_reflect_cd, self.player_reflect_disabled,
            self.player_damage_bonus,
            self.player_atk_tendency, self.player_def_tendency, self.player_buf_tendency,
        )


def get_moves(qi, reflect_cd, reflect_disabled):
    moves = []
    for name, info in SKILLS.items():
        if qi >= info["qi_cost"]:
            if name == "反弹" and reflect_cd > 0:
                continue
            if name == "反弹" and reflect_disabled:
                continue
            moves.append(name)
    return moves


def simulate(state, ai_move, player_move):
    s = state.copy()

    s.ai_qi = s.ai_qi - SKILLS[ai_move]["qi_cost"]
    if ai_move == "反弹":
        s.ai_reflect_cd = 2
    if s.ai_reflect_cd > 0:
        s.ai_reflect_cd -= 1

    s.player_qi = s.player_qi - SKILLS[player_move]["qi_cost"]
    if player_move == "反弹":
        s.player_reflect_cd = 2
    if s.player_reflect_cd > 0:
        s.player_reflect_cd -= 1

    p_type = SKILLS[player_move]["type"]
    a_type = SKILLS[ai_move]["type"]

    if a_type == "buff":
        effect = SKILLS[ai_move]["effect"]
        if effect == "qi":
            s.ai_qi += SKILLS[ai_move]["value"]
        elif effect == "heal":
            s.ai_hp = min(2.0, s.ai_hp + SKILLS[ai_move]["value"])
        elif effect == "shield":
            s.ai_shield += SKILLS[ai_move]["value"]
        elif effect == "damage_boost":
            s.ai_damage_bonus = True

    if p_type == "buff":
        effect = SKILLS[player_move]["effect"]
        if effect == "qi":
            s.player_qi += SKILLS[player_move]["value"]
        elif effect == "heal":
            s.player_hp = min(2.0, s.player_hp + SKILLS[player_move]["value"])
        elif effect == "shield":
            s.player_shield += SKILLS[player_move]["value"]
        elif effect == "damage_boost":
            s.player_damage_bonus = True

    if ai_move == "破反" and player_move == "反弹":
        s.player_reflect_disabled = True
    elif player_move == "破反" and ai_move == "反弹":
        s.ai_reflect_disabled = True

    JIU_WEIGHT = 1.2

    p_dmg, a_dmg = 0, 0

    if a_type == "attack" and p_type == "attack":
        if ai_move == player_move:
            pass
        else:
            a_eff = SKILLS[ai_move]["qi_cost"] + (JIU_WEIGHT if s.ai_damage_bonus else 0)
            p_eff = SKILLS[player_move]["qi_cost"] + (JIU_WEIGHT if s.player_damage_bonus else 0)
            a_dmg = SKILLS[ai_move]["damage"] + (1 if s.ai_damage_bonus else 0)
            p_dmg = SKILLS[player_move]["damage"] + (1 if s.player_damage_bonus else 0)
            if p_eff > a_eff:
                a_dmg = 0
            elif a_eff > p_eff:
                p_dmg = 0
            else:
                p_dmg = 0
                a_dmg = 0
    elif a_type == "attack" and p_type == "defend":
        if SKILLS[ai_move]["qi_cost"] >= SKILLS[player_move]["block_qi"]:
            a_dmg = SKILLS[ai_move]["damage"] + (1 if s.ai_damage_bonus else 0)
    elif p_type == "attack" and a_type == "defend":
        if SKILLS[player_move]["qi_cost"] >= SKILLS[ai_move]["block_qi"]:
            p_dmg = SKILLS[player_move]["damage"] + (1 if s.player_damage_bonus else 0)
    elif a_type == "attack" and p_type == "reflect":
        a_dmg = SKILLS[ai_move]["damage"] + (1 if s.ai_damage_bonus else 0)
    elif a_type == "attack" and p_type == "special":
        a_dmg = SKILLS[ai_move]["damage"] + (1 if s.ai_damage_bonus else 0)
    elif p_type == "attack" and a_type == "reflect":
        p_dmg = SKILLS[player_move]["damage"] + (1 if s.player_damage_bonus else 0)
    elif p_type == "attack" and a_type == "special":
        p_dmg = SKILLS[player_move]["damage"] + (1 if s.player_damage_bonus else 0)
    elif a_type == "attack":
        a_dmg = SKILLS[ai_move]["damage"] + (1 if s.ai_damage_bonus else 0)
    elif p_type == "attack":
        p_dmg = SKILLS[player_move]["damage"] + (1 if s.player_damage_bonus else 0)

    if p_type == "attack":
        s.player_damage_bonus = False
    if a_type == "attack":
        s.ai_damage_bonus = False

    if a_dmg > 0:
        if s.player_shield > 0:
            absorbed = min(s.player_shield, a_dmg)
            s.player_shield -= absorbed
            a_dmg -= absorbed
        s.player_hp -= a_dmg

    if p_dmg > 0:
        if s.ai_shield > 0:
            absorbed = min(s.ai_shield, p_dmg)
            s.ai_shield -= absorbed
            p_dmg -= absorbed
        s.ai_hp -= p_dmg

    return s


def evaluate(state):
    if state.ai_hp <= 0:
        return -10000
    if state.player_hp <= 0:
        return 10000

    score = 0.0

    score += (state.ai_hp - state.player_hp) * 100
    score += (state.ai_qi - state.player_qi) * 3
    score += (state.ai_shield - state.player_shield) * 20

    if not state.ai_reflect_disabled:
        score += 8
    if not state.player_reflect_disabled:
        score -= 8

    if state.ai_hp <= 0.5:
        score -= 20
    if state.player_hp <= 0.5:
        score += 20

    patk = state.player_atk_tendency
    pdef = state.player_def_tendency
    pbuf = state.player_buf_tendency

    if patk > 0.5:
        score += 15
    elif patk > 0.3:
        score += 8
    if pdef > 0.5:
        score -= 10
    if pbuf > 0.4:
        score += 10

    if state.ai_damage_bonus:
        score += 15
    if state.player_damage_bonus:
        score -= 10

    if state.ai_hp < 0.7:
        score += 5
    if state.player_hp < 0.7:
        score += 5

    return score


def minimax(state, depth, alpha, beta, is_ai_turn):
    if depth == 0 or state.ai_hp <= 0 or state.player_hp <= 0:
        return evaluate(state), None

    if is_ai_turn:
        moves = get_moves(state.ai_qi, state.ai_reflect_cd, state.ai_reflect_disabled)
        if not moves:
            moves = ["聚气"]

        best_score = float("-inf")
        best_move = moves[0]

        for move in moves:
            total_score = 0
            total_weight = 0

            for p_move in get_moves(state.player_qi, state.player_reflect_cd, state.player_reflect_disabled):
                new_state = simulate(state, move, p_move)

                mtype = SKILLS[p_move]["type"]
                if mtype == "attack":
                    w = max(state.player_atk_tendency, 0.25)
                elif mtype == "defend" or p_move == "反弹":
                    w = max(state.player_def_tendency, 0.15)
                elif mtype == "buff":
                    w = max(state.player_buf_tendency, 0.20)
                else:
                    w = 0.15

                score, _ = minimax(new_state, depth - 1, alpha, beta, False)
                total_score += score * w
                total_weight += w

            avg_score = total_score / total_weight if total_weight > 0 else 0

            if avg_score > best_score:
                best_score = avg_score
                best_move = move

        return best_score, best_move

    else:
        moves = get_moves(state.player_qi, state.player_reflect_cd, state.player_reflect_disabled)
        if not moves:
            moves = ["聚气"]

        total_score = 0
        total_weight = 0
        best_move = moves[0]

        for move in moves:
            mtype = SKILLS[move]["type"]
            if mtype == "attack":
                w = max(state.player_atk_tendency, 0.25)
            elif mtype == "defend" or move == "反弹":
                w = max(state.player_def_tendency, 0.15)
            elif mtype == "buff":
                w = max(state.player_buf_tendency, 0.20)
            else:
                w = 0.15

            move_score = 0
            count = 0

            for a_move in get_moves(state.ai_qi, state.ai_reflect_cd, state.ai_reflect_disabled):
                new_state = simulate(state, a_move, move)
                score, _ = minimax(new_state, depth - 1, alpha, beta, True)
                move_score += score
                count += 1

            avg_move_score = move_score / count if count > 0 else 0
            total_score += avg_move_score * w
            total_weight += w

        weighted_avg = total_score / total_weight if total_weight > 0 else 0
        return weighted_avg, best_move


def find_best_move(state, depth=3):
    score, move = minimax(state, depth, float("-inf"), float("inf"), True)
    return move, score


def state_from_fighter(ai, player, player_tendencies=None):
    patk = 0.0
    pdef = 0.0
    pbuf = 0.0
    if player_tendencies:
        total = sum(player_tendencies.values())
        if total > 0:
            for move, count in player_tendencies.items():
                ratio = count / total
                mtype = SKILLS[move]["type"]
                if mtype == "attack":
                    patk += ratio
                elif mtype == "defend" or move == "反弹":
                    pdef += ratio
                elif mtype == "buff":
                    pbuf += ratio
    return GameState(
        ai_hp=ai.hp,
        ai_qi=ai.qi,
        ai_shield=ai.shield,
        ai_reflect_cd=ai.reflect_cooldown,
        ai_reflect_disabled=ai.reflect_disabled,
        ai_damage_bonus=ai.damage_bonus,
        player_hp=player.hp,
        player_qi=player.qi,
        player_shield=player.shield,
        player_reflect_cd=player.reflect_cooldown,
        player_reflect_disabled=player.reflect_disabled,
        player_damage_bonus=player.damage_bonus,
        player_atk_tendency=patk,
        player_def_tendency=pdef,
        player_buf_tendency=pbuf,
    )
