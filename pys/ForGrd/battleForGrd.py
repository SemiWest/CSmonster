from game_menu import *
from ForGrd.playerForGrd import *
from ForGrd.itemForGrd import get_item_color_by_grade
import logging
import time

logger = logging.getLogger(__name__)

def is_invulnerable(target):
    """디버그 모드 무적 상태 확인 헬퍼 함수"""
    dbg = getattr(target, "debug_config", None)
    if dbg and dbg.debug:
        return dbg.damage  # True => 무적, False => 데미지 받음
    return getattr(target, "cheatmode", False)

''' 전역변수 설정 '''
hap_num = 0
item_num = 0
player = None
enemy = None
enemyCSmon = None
battle_end = False
startBattleHp = 0
BASIC_PNR_SUCCESS_RATE = 0.7
# 난이도 조절을 위한 전역 변수
# 1~100 사이의 값으로 설정. 값이 높을수록 더 지능적인 선택을 함.
INTELLIGENCE_LEVEL = 80

# 기존 좌표 및 이미지 로드는 그대로 유지
sX, sY = 32, 32
stX = sX+42
stY = sY+575
esX, esY = sX+20, sY+36
psX, psY = sX+582, sY+346
HPLEN = 64

# 기존 이미지들 그대로 유지
BACKGROUND = pygame.image.load("../img/background.png")
STAT = pygame.image.load("../img/stat.png")
TEXT = pygame.image.load("../img/text.png")
RANK = pygame.image.load("../img/rank.png")

CT = pygame.image.load("../img/CT.png")
DS = pygame.image.load("../img/DS.png")
AI = pygame.image.load("../img/AI.png")
PS = pygame.image.load("../img/PS.png")
SYS = pygame.image.load("../img/SYS.png")
EVENT = pygame.image.load("../img/EVENT.png")
STAR = pygame.image.load("../img/STAR.png")

ME = pygame.image.load("../img/monsters/ME.png")
ATK = pygame.image.load("../img/ATK.png")
SPATK = pygame.image.load("../img/SP.ATK.png")
ETC = pygame.image.load("../img/ETC.png")
SPEC_TEXT = pygame.image.load("../img/spc_text.png")
SKILL = pygame.image.load("../img/skill.png")

BACKGROUND = pygame.transform.scale_by(BACKGROUND, 11)
TEXT = pygame.transform.scale_by(TEXT, 5)
SPEC_TEXT = pygame.transform.scale_by(SPEC_TEXT, 5)
SKILL = pygame.transform.scale_by(SKILL, 4)
RANK = pygame.transform.scale_by(RANK, 4)
ME = pygame.transform.scale_by(ME, 10)
CT = pygame.transform.scale_by(CT, 4)
DS = pygame.transform.scale_by(DS, 4)
AI = pygame.transform.scale_by(AI, 4)
PS = pygame.transform.scale_by(PS, 4)
SYS = pygame.transform.scale_by(SYS, 4)
EVENT = pygame.transform.scale_by(EVENT, 4)
STAR = pygame.transform.scale_by(STAR, 4)

BUFF = []
path = "../img/animations/buff"
for i in range(len(os.listdir(path))):
    img = pygame.image.load(f"{path}/{i}.png")
    img = pygame.transform.scale_by(img, 10)
    BUFF.append(img)
DEBUFF = []
path = "../img/animations/debuff"
for i in range(len(os.listdir(path))):
    img = pygame.image.load(f"{path}/{i}.png")
    img = pygame.transform.scale_by(img, 10)
    DEBUFF.append(img)
HEALFORP = []
HEALFORE = []
HEAL = []
path = "../img/animations/heal"
for i in range(len(os.listdir(path))):
    img = pygame.image.load(f"{path}/{i}.png")
    img = pygame.transform.scale_by(img, 10)
    HEAL.append(img)
HEALFORE = HEAL
for i in range(len(HEAL)):
    HEALFORP.append(pygame.transform.scale_by(HEAL[i], 2))


# 반사 스킬용 이미지 로드
SHIELD = pygame.image.load("../img/animations/items/shield.png")
SHIELD = pygame.transform.scale_by(SHIELD, 8)
MIRROR = pygame.image.load("../img/animations/items/mirror.png")
MIRROR = pygame.transform.scale_by(MIRROR, 8)

def comp(atskilltype, tgtype):
    """
    공격 타입(atskilltype)과 방어 타입(tgtypes: str 또는 list)을 받아 상성 배율을 반환.
    - 방어 타입이 여러 개인 경우 배율을 곱셈으로 적용.
    - 존재하지 않는 키가 오면 기본 1.0 처리.
    """
    return TYPE_EFFECTIVENESS[atskilltype][tgtype]

def Damage(target, attacker, skilldict):
    basedmg = ((2*attacker.level + 10)/250) * attacker.CATK / max(1, target.CDEF)  # ✅ max(1, ...)
    multiplier = comp(skilldict["type"], target.type[0])
    Jasok = 1.5 if attacker.type[0] == skilldict["type"] else 1.0
    return int(multiplier * (basedmg*skilldict["skW"] + 2) * Jasok * random.uniform(0.85, 1.00)), multiplier

import random

# 가정: Enemy와 Player 객체가 각각 `nowhp`, `HP` 등의 속성을 가지고 있음
# player_used_skill: 플레이어가 최근에 사용한 스킬. (예: "Pdamage")

def get_best_enemy_skill(enemy, player):
    # selected_skill 객체가 딕셔너리 형태가 아닐 경우를 대비해 effect_type을 추출
    enemy_skills = getattr(enemy, 'skills', {})
    if not enemy_skills:
        return None

    skill_scores = {}

    # 몬스터의 스킬 딕셔너리에서 스킬 객체들을 순회
    for skill_name, skill_data in enemy_skills.items():
        score = 0
        
        # Skill 객체의 속성에 직접 접근
        skill_type = skill_data.effect_type
        
        # 1. 자신의 현재 HP를 기반으로 점수 계산
        if enemy.nowhp < enemy.HP * 0.6 and skill_type == "heal":
            score += 40
        if enemy.nowhp == enemy.HP and skill_type == "heal":
            score = 0
        # 2. 상대방의 HP를 기반으로 점수 계산
        if player.nowhp < player.HP * 0.5 and skill_type in ["Pdamage", "Sdamage", "halve_hp"]:
            score += 30
        # 3. 자신의 스탯 버프 필요성에 따라 점수 계산
        if skill_type == "buff":
            if enemy.Rank[0] < 0:
                if isinstance(skill_data.skW, tuple):
                    if 0 in [b % 3 for b in skill_data.skW]:
                        score += 30
                else:
                    if skill_data.skW % 3 == 0:
                        score += 30
            if enemy.Rank[1] < 0:
                if isinstance(skill_data.skW, tuple):
                    if 1 in [b % 3 for b in skill_data.skW]:
                        score += 30
                else:
                    if skill_data.skW % 3 == 1:
                        score += 30
            if enemy.Rank[2] < 0:
                if isinstance(skill_data.skW, tuple):
                    if 2 in [b % 3 for b in skill_data.skW]:
                        score += 30
                else:
                    if skill_data.skW % 3 == 2:
                        score += 30

        # 4. 자신의 스탯이 최대치면 가중치 제거
            if enemy.Rank[0] != 6:
                if isinstance(skill_data.skW, tuple):
                    if 0 in [b % 3 for b in skill_data.skW]:
                        score += 5
                else:
                    if skill_data.skW % 3 == 0:
                        score += 10
            if enemy.Rank[1] != 6:
                if isinstance(skill_data.skW, tuple):
                    if 1 in [b % 3 for b in skill_data.skW]:
                        score += 5
                else:
                    if skill_data.skW % 3 == 1:
                        score += 10
            if enemy.Rank[2] != 6:
                if isinstance(skill_data.skW, tuple):
                    if 2 in [b % 3 for b in skill_data.skW]:
                        score += 5
                else:
                    if skill_data.skW % 3 == 2:
                        score += 10
        
    total_score = sum(skill_scores.values())
    
    if total_score == 0:
        return random.choice(list(enemy_skills.values()))

    # 지능 지수에 따라 무작위 또는 점수 기반 선택
    if random.randint(1, 100) > INTELLIGENCE_LEVEL:
        return random.choice(list(enemy_skills.values()))
    else:
        skill_list = list(skill_scores.keys())
        probabilities = [score / total_score for score in skill_scores.values()]
        
        selected_skill_name = random.choices(skill_list, weights=probabilities, k=1)[0]
        return enemy_skills[selected_skill_name]

def use_skill(attackerType, player, monster, playerskill, monsterskill, screen):
    # --- 1. 초기 설정: 변수 준비 ---
    if playerskill is None:
        playerskill_dict = None
    else:
        playerskill_dict = {
            "type": playerskill["type"],
            "effect_type": playerskill["effect_type"],
            "skW": playerskill["skW"],
            "animation": playerskill["animation"],
            "bonus_effect": playerskill.get("bonus_effect", None)
        }
    if monsterskill is None:
        monsterskill_dict = None
    else:
        monsterskill_dict = {
            "type": monsterskill.skill_type,
            "effect_type": monsterskill.effect_type,
            "skW": monsterskill.skW,
            "animation": monsterskill.animation,
            "bonus_effect": getattr(monsterskill, "bonus_effect", None)
        }
        if isinstance(monster.skW, str):
            if monster.skW == "DEF":
                monsterskill_dict["skW"] = 10+40*(max(1, monster.Rank[1]))
            elif monster.skW == "SPD":
                monsterskill_dict["skW"] = 10+50*(max(1, monster.Rank[2]))
                
    if attackerType == "monster":
        user, target, skill, counter_skill = monster, player, monsterskill_dict, playerskill_dict
    else:  # player
        user, target, skill, counter_skill = player, monster, playerskill_dict, monsterskill_dict

    # 스킬이 없는 경우(버그 방지)
    if not skill:
        return False, 0, False
        
    effect = skill["effect_type"]
    # --- 2. 스킬 효과별 로직 분기 ---

    # A. 데미지를 주거나 체력을 직접 변경하는 스킬 (Damage, Halve HP)
    if effect in ["Pdamage", "Sdamage", "halve_hp"]:
        old_hp = target.nowhp
        new_hp = old_hp
        damage = 0
        Mul = 1

        if effect in ["Pdamage", "Sdamage"]:
            damage, Mul = Damage(target, user, skill)
            if not (attackerType == "monster" and is_invulnerable(target)):
                new_hp = max(0, int(old_hp - damage))
        
        elif effect == "halve_hp":
            damage = old_hp // 2
            if not (attackerType == "monster" and is_invulnerable(target)):
                new_hp = old_hp - damage
        
        # 애니메이션을 먼저 재생
        play_damage_sequence(screen, skill, user, target, old_hp, new_hp, Mul)
        
        # 애니메이션 종료 후 실제 데이터 반영
        target.nowhp = new_hp

        if skill["bonus_effect"] != None:
            if skill["bonus_effect"][0] == "buff":
                if isinstance(skill["bonus_effect"][1], tuple):
                    for B in skill["bonus_effect"][1]:
                        user.Rank[B % 3] = max(-6, min(6, user.Rank[B % 3] + B // 3 + 1))
                else:
                    user.Rank[skill["bonus_effect"][1] % 3] = max(-6, min(6, user.Rank[skill["bonus_effect"][1] % 3] + skill["bonus_effect"][1] // 3 + 1))
                
                user.update_battle()
            elif skill["bonus_effect"][0] == "heal":
                if skill["bonus_effect"][1] =="absorb":
                    heal_amount = int(damage * skill["bonus_effect"][2])
                else:
                    heal_amount = int(skill["bonus_effect"][1] * user.HP)
                new_user_hp = min(user.HP, user.nowhp + heal_amount)

                healAnimation("player" if attackerType == "player" else "enemy")
                animate_health_bar(screen, psY + 121 if attackerType == "player" else esY+121, psX+122 if attackerType == "player" else esX+122, user.nowhp, new_user_hp, user.HP)
                user.nowhp = new_user_hp
            
            return False, damage, (Mul, skill["bonus_effect"])

        return False, damage, Mul

    # B. 회복 스킬 (Heal)
    elif effect == "heal":
        old_hp = user.nowhp
        heal_amount = int(skill["skW"] * user.HP)
        new_hp = min(user.HP, old_hp + heal_amount)
        
        healAnimation("player" if attackerType == "player" else "enemy")
        animate_health_bar(screen, psY + 121 if attackerType == "player" else esY+121, psX+122 if attackerType == "player" else esX+122, old_hp, new_hp, user.HP)
        user.nowhp = new_hp
        return False, 0, False

    # C. 버프/디버프 스킬 (Buff)
    elif effect == "buff":
        if isinstance(skill["skW"], tuple):
            for B in skill["skW"]:
                user.Rank[B % 3] = max(-6, min(6, user.Rank[B % 3] + B // 3 + 1))
        else:
            user.Rank[skill["skW"] % 3] = max(-6, min(6, user.Rank[skill["skW"] % 3] + skill["skW"] // 3 + 1))
        
        user.update_battle()

        return False, 0, False
        
    # D. 반사 스킬 (Reflect) - <<수정된 부분>>
    elif effect == "reflect":
        # 1. 애니메이션을 재생하는 대신, 캐릭터에게 '방어 중' 상태를 부여합니다.
        stance = 'shield' if skill["skW"] == 0 else 'mirror'
        setattr(user, 'defensive_stance', stance)

        # 2. 상대방이 공격 스킬을 사용했는지 확인
        if counter_skill is None or counter_skill["effect_type"] not in ["Pdamage", "Sdamage"]:
            return False, -121, False

        # 3. 스킬 효과 분기: 방어(skW=0) 또는 반사(skW>0)
        if skill["skW"] == 0:  # 방어 (shield)
            play_damage_sequence(screen, counter_skill, user, target, target.nowhp, target.nowhp, 1)
            
            # 공격을 막았다는 메시지를 출력합니다.
            display_status(screen, True)
            draw_text(screen, f"  {target.name}이(가) 공격을 막아냈다!", stX, stY, WHITE)
            pygame.display.flip()
            wait_for_key()
            
            return True, 0, 1 # 상대 턴 종료
        else:  # 반사 (mirror)
            damage, Mul = Damage(target, user, counter_skill)
            damage = int(damage * skill["skW"])
            
            old_hp = target.nowhp
            new_hp = max(0, old_hp - damage)

            # 반사 데미지 애니메이션 재생 (이제 거울과 함께 표시됩니다)
            play_damage_sequence(screen, counter_skill, user, target, old_hp, new_hp, Mul)
            
            target.nowhp = new_hp
            return True, damage, Mul # 상대 턴 종료

    # E. 그 외 모든 스킬
    else:
        return False, 0, False        

# 기존 함수들 그대로 유지
def display_type(screen, y, x, type):
    """타입 표시 (pygame)"""
    if type == "CT":
        screen.blit(CT, (x, y))
    elif type == "DS":
        screen.blit(DS, (x, y))
    elif type == "SYS":
        screen.blit(SYS, (x, y))
    elif type == "PS":
        screen.blit(PS, (x, y))
    elif type == "*":
        screen.blit(STAR, (x, y))
    elif type == "AI":
        screen.blit(AI, (x, y))
    elif type == "EVENT":
        screen.blit(EVENT, (x, y))

def get_ratio(hp, max_hp):
    if hp <= 0:
        return 0
    ratio = int(hp * HPLEN / max_hp)
    return max(1, ratio) if hp > 0 else 0

def hpcolor(ratio):
    """체력 상태에 따른 색상 선택"""
    if ratio >= 42:
        color_pair = GREEN
    elif ratio >= 21:
        color_pair = YELLOW
    elif ratio >= 1:
        color_pair = RED
    else: color_pair = BLACK
    return color_pair

def animate_health_bar(screen, y, x, current_hp, target_hp, max_hp):
    """체력바를 부드럽게 애니메이션으로 업데이트 (pygame)"""
    current_ratio = get_ratio(current_hp, max_hp)
    target_ratio = get_ratio(target_hp, max_hp)
    steps = abs(current_ratio - target_ratio)

    def draw_HP(surface, text, x, y, color, highlight=BLACK):
        fontforHP = pygame.font.Font("../neodgm.ttf", 10)
        font_obj = fontforHP
        text_surface = font_obj.render(text, True, color, highlight)
        surface.blit(text_surface, (x, y))
        return text_surface.get_rect(topleft=(x, y))

    if steps == 0:
        draw_HP(screen, f"{'█' * current_ratio}{' ' * (HPLEN - current_ratio)}", x, y+10, hpcolor(current_ratio))
        draw_HP(screen, f"{'█' * current_ratio}{' ' * (HPLEN - current_ratio)}", x, y+5, hpcolor(current_ratio))
        draw_HP(screen, f"{'█' * current_ratio}{' ' * (HPLEN - current_ratio)}", x, y+0, hpcolor(current_ratio))
        return
    for step in range(steps + 1):
        interpolated_ratio = current_ratio + int((target_ratio - current_ratio) * step / steps)
        draw_HP(screen, f"{'█' * interpolated_ratio}{' ' * (HPLEN - interpolated_ratio)}", x, y+10, hpcolor(interpolated_ratio))
        draw_HP(screen, f"{'█' * interpolated_ratio}{' ' * (HPLEN - interpolated_ratio)}", x, y+5, hpcolor(interpolated_ratio))
        draw_HP(screen, f"{'█' * interpolated_ratio}{' ' * (HPLEN - interpolated_ratio)}", x, y+0, hpcolor(interpolated_ratio))
        pygame.display.flip()
        time.sleep(0.666/steps)

def healAnimation(targettype="player"):
    """회복 애니메이션 재생"""
    if targettype=="player":
        x, y = sX+320, sY+536
        screen = pygame.display.get_surface()
        Heal()
        for i in range(len(HEALFORP)):
            display_status(screen, detail=True)
            image = HEALFORP[i]
            screen.blit(image, (x-image.get_width()//2, y-image.get_height()))
            pygame.display.flip()
            time.sleep(0.03)
    else:
        x, y = esX+900, esY+305
        screen = pygame.display.get_surface()
        Heal()
        for i in range(len(HEALFORE)):
            display_status(screen, detail=True)
            image = HEALFORE[i]
            screen.blit(image, (x-image.get_width()//2, y-image.get_height()))
            pygame.display.flip()
            time.sleep(0.03)
    
def buffAnimation(is_increase, targettype="player"):
    """버프 애니메이션 재생"""
    if targettype=="player":
        x, y = sX+320, sY+536
    else:
        x, y = esX+900, esY+305
    screen = pygame.display.get_surface()
    if is_increase:
        RankUp()
        for i in range(len(BUFF)):
            display_status(screen, detail=True)
            image = BUFF[i]
            screen.blit(image, (x-image.get_width()//2, y-image.get_height()))
            pygame.display.flip()
            time.sleep(0.03)
    else:
        RankDown()
        for i in range(len(DEBUFF)):
            display_status(screen, detail=True)
            image = DEBUFF[i]
            screen.blit(image, (x-image.get_width()//2, y-image.get_height()))
            pygame.display.flip()
            time.sleep(0.03)

def play_damage_sequence(screen, skill, attacker, target, old_hp, new_hp, Mul=1):
    """[최종 수정] 스킬 렌더링 순서 및 변수 할당 오류를 수정한 최종 버전입니다."""
    ENEMY = pygame.image.load(enemyCSmon.image).convert_alpha()
    ENEMY = pygame.transform.scale_by(ENEMY, 10)
    active_stance = getattr(enemyCSmon if target == player else player, 'defensive_stance', None)
    skill_frames = []
    if active_stance == "mirror":
        if target != enemyCSmon:
            for i in range(len(os.listdir(f"../img/animations/skill/default_enemy"))):
                img = pygame.image.load(f"../img/animations/skill/default_enemy/{i}.png")
                img = pygame.transform.scale_by(img, 11/3)
                skill_frames.append(img)
        else:
            for i in range(len(os.listdir(f"../img/animations/skill/default_player"))):
                img = pygame.image.load(f"../img/animations/skill/default_player/{i}.png")
                img = pygame.transform.scale_by(img, 11/3)
                skill_frames.append(img)
    elif skill["animation"] != "none":    
        for i in range(len(os.listdir(f"../img/animations/skill/{skill['animation']}"))):
            img = pygame.image.load(f"../img/animations/skill/{skill['animation']}/{i}.png")
            img = pygame.transform.scale_by(img, 11/3)
            skill_frames.append(img)
    else:
        if attacker == player:
            for i in range(len(os.listdir(f"../img/animations/skill/default_player"))):
                img = pygame.image.load(f"../img/animations/skill/default_player/{i}.png")
                img = pygame.transform.scale_by(img, 11/3)
                skill_frames.append(img)
        else:
            for i in range(len(os.listdir(f"../img/animations/skill/default_enemy"))):
                img = pygame.image.load(f"../img/animations/skill/default_enemy/{i}.png")
                img = pygame.transform.scale_by(img, 11/3)
                skill_frames.append(img)
    
    red_surface = ENEMY.copy() if target != player else ME.copy()
    red_surface.fill((255, 60, 60, 150), special_flags=pygame.BLEND_RGBA_MULT)

    # --- 2. 애니메이션 시간 설정 (오류 수정) ---
    SKILL_ANIM_END_TIME = 1100
    IMPACT_START_TIME = 1300
    FLASH_DURATION = 800
    HP_BAR_START_TIME = IMPACT_START_TIME
    HP_BAR_DURATION = 800
    TOTAL_DURATION = HP_BAR_START_TIME + HP_BAR_DURATION
    
    start_time = pygame.time.get_ticks()
    hurt_sound_played = False
    if skill["animation"] != "none": play_effect(f"../sound/skills/{skill['animation']}.mp3")
    else: play_effect("../sound/skills/default.mp3")
    # --- 3. 통합 애니메이션 루프 ---
    while True:
        elapsed_time = pygame.time.get_ticks() - start_time
        if elapsed_time > TOTAL_DURATION: break

        # --- 프레임별 렌더링 ---
        
        # [레이어 1] 배경
        screen.blit(BACKGROUND, (sX, sY))

        # [레이어 2] 몹
        if getattr(enemyCSmon, 'is_defeated', False):
            silhouette = ENEMY.copy(); silhouette.fill((30, 30, 30), special_flags=pygame.BLEND_RGB_MULT)
            screen.blit(silhouette, (esX + 900 - ENEMY.get_width() // 2, esY + 305 - ENEMY.get_height()))
        else:
            screen.blit(ENEMY, (esX + 900 - ENEMY.get_width() // 2, esY + 305 - ENEMY.get_height()))

        # [레이어 2.5] 방패/거울
        if active_stance:
            defense_img = SHIELD if active_stance == 'shield' else MIRROR
            if target != player:
                anchor_x, anchor_y = sX + 320, sY + 536
            else:
                # ▼▼▼ [수정 1] 방패/거울 기준점도 몬스터 위치에 맞게 변경 (900, 305 -> 900, 305) ▼▼▼
                anchor_x, anchor_y = esX + 880, esY + 305
            img_pos_x = anchor_x - defense_img.get_width()//2
            img_pos_y = anchor_y - defense_img.get_height()
            screen.blit(defense_img, (img_pos_x, img_pos_y))

        # [레이어 3] 스킬 애니메이션
        if elapsed_time < SKILL_ANIM_END_TIME and skill_frames:
            frame_index = int((elapsed_time / SKILL_ANIM_END_TIME) * len(skill_frames))
            frame_index = min(frame_index, len(skill_frames) - 1)
            screen.blit(skill_frames[frame_index], (sX, sY))

        # [레이어 4] 플레이어
        if getattr(player, 'is_defeated', False):
            silhouette = ME.copy(); silhouette.fill((30, 30, 30), special_flags=pygame.BLEND_RGB_MULT)
            screen.blit(silhouette, (sX + 320 - ME.get_width() // 2, sY + 536 - ME.get_height()))
        else:
            screen.blit(ME, (sX + 320 - ME.get_width() // 2, sY + 536 - ME.get_height()))
        
        # [레이어 5] 피격 점멸 효과
        if elapsed_time >= IMPACT_START_TIME:
            if not hurt_sound_played and new_hp < old_hp: Effective() if Mul > 1.7 else NotEffective() if Mul<0.8 else NormalDamage(); hurt_sound_played = True
            flash_elapsed = elapsed_time - IMPACT_START_TIME
            if flash_elapsed < FLASH_DURATION and new_hp < old_hp:
                if (int(flash_elapsed / 100)) % 2 == 0: screen.blit(red_surface, (esX + 900 - ENEMY.get_width() // 2, esY + 305 - ENEMY.get_height())) if target != player else screen.blit(red_surface, (sX + 320 - ME.get_width() // 2, sY + 536 - ME.get_height()))

        # [레이어 6] UI
        screen.blit(STAT, (esX, esY))
        # ▼▼▼ [수정 2] 이름/레벨 y좌표를 display_status와 동일하게 변경 (52 -> 70) ▼▼▼
        draw_text(screen, f"{enemyCSmon.name}", esX + 64, esY + 70, WHITE)
        draw_text(screen, f"lv {getattr(enemyCSmon, 'level', 1)}", esX + 384, esY + 70, WHITE)
        enemy_types = getattr(enemyCSmon, 'type', ['전산이론'])
        if isinstance(enemy_types, str): enemy_types = [enemy_types]
        for i, enemy_type in enumerate(enemy_types[:2]):
            display_type(screen, esY, esX + 470 + i * 124, enemy_type)
        
        screen.blit(STAT, (psX, psY))
        if any(rank != 0 for rank in enemyCSmon.Rank):
            screen.blit(RANK, (esX+470+160, esY))
            for i, rank in enumerate(enemyCSmon.Rank):
                draw_text(screen, "ATK" if i==0 else "DEF" if i==1 else "SPD", esX+470+160+20, esY+30+i*44, WHITE)
                draw_text(screen, f"{'+' if rank>=0 else ''}{rank}", esX+470+160+80, esY+30+i*44, RED if rank<0 else GREEN if rank>0 else WHITE)

        # ▼▼▼ [수정 2] 이름/레벨 y좌표를 display_status와 동일하게 변경 (52 -> 70) ▼▼▼
        draw_text(screen, f"{player.name}", psX + 64, psY + 70, WHITE)
        draw_text(screen, f"lv {player.level}", psX + 384, psY + 70, WHITE)
        display_type(screen, psY, psX + 470, player.type[0])
        display_player_details(screen, player, sX + 1264)
        screen.blit(TEXT, (sX+11, sY+535))

        # [레이어 7] 체력바 애니메이션
        if target == player:
            progress = min(1.0, (elapsed_time - HP_BAR_START_TIME) / HP_BAR_DURATION) if elapsed_time >= HP_BAR_START_TIME else 0
            animated_hp = old_hp - (old_hp - new_hp) * progress
            # ▼▼▼ [수정 3] 체력바 위치를 display_status와 동일하게 변경 (y+104, x+135 -> y+121, x+122) ▼▼▼
            draw_health_bar(screen, psY + 121, psX + 122, animated_hp, player.HP)
            draw_health_bar(screen, esY + 121, esX + 122, enemyCSmon.nowhp, enemyCSmon.HP)

        else:
            progress = min(1.0, (elapsed_time - HP_BAR_START_TIME) / HP_BAR_DURATION) if elapsed_time >= HP_BAR_START_TIME else 0
            animated_hp = old_hp - (old_hp - new_hp) * progress
            # ▼▼▼ [수정 3] 체력바 위치를 display_status와 동일하게 변경 (y+104, x+135 -> y+121, x+122) ▼▼▼
            draw_health_bar(screen, esY + 121, esX + 122, animated_hp, enemyCSmon.HP)
            draw_health_bar(screen, psY + 121, psX + 122, player.nowhp, player.HP)

        pygame.display.flip()
  
def play_death_animation(target_character, screen):
    """[재수정됨] 지정한 캐릭터가 검정/흰색으로 점멸하는 애니메이션만 재생합니다."""

    # --- 1. 초기 설정 ---
    # (이전 코드와 동일)
    target_surface, target_pos, living_char_surface, living_char_pos = None, (0, 0), None, (0, 0)
    if target_character == 'monster':
        if hasattr(enemyCSmon, 'image'):
            enemy_img = pygame.image.load(enemyCSmon.image).convert_alpha()
            target_surface = pygame.transform.scale_by(enemy_img, 10)
        target_pos = (esX + 900 - target_surface.get_width() // 2, esY + 305 - target_surface.get_height())
        living_char_surface, living_char_pos = ME, (sX + 320 - ME.get_width() // 2, sY + 536 - ME.get_height())
    elif target_character == 'player':
        target_surface = ME; target_pos = (sX + 320 - ME.get_width() // 2, sY + 536 - ME.get_height())
        if hasattr(enemyCSmon, 'image'):
            enemy_img = pygame.image.load(enemyCSmon.image).convert_alpha()
            living_char_surface = pygame.transform.scale_by(enemy_img, 10)
        living_char_pos = (esX + 900 - living_char_surface.get_width() // 2, esY + 305 - living_char_surface.get_height())
    if not target_surface: return

    # --- 2. 실루엣 생성 ---
    white_flash_surface = target_surface.copy()
    white_flash_surface.fill((200, 200, 200), special_flags=pygame.BLEND_RGB_MULT)
    dark_silhouette_surface = target_surface.copy()
    dark_silhouette_surface.fill((30, 30, 30), special_flags=pygame.BLEND_RGB_MULT)

    # --- 3. 애니메이션 시간 설정 ---
    FLASH_DURATION = 600
    FLASH_INTERVAL = 100
    start_time = pygame.time.get_ticks()
    
    # --- 4. 점멸 애니메이션 루프 ---
    while True:
        elapsed_time = pygame.time.get_ticks() - start_time
        if elapsed_time > FLASH_DURATION:
            break

        display_status(screen, detail=True)
        if living_char_surface:
            screen.blit(living_char_surface, living_char_pos)

        if (int(elapsed_time / FLASH_INTERVAL)) % 2 == 0:
            screen.blit(dark_silhouette_surface, target_pos)
        else:
            screen.blit(white_flash_surface, target_pos)

        pygame.display.flip()
    # 마지막 프레임을 그리는 부분을 삭제하여 역할을 분리함
   
def flash_red(target_character, screen):
    """지정한 캐릭터를 붉은색으로 깜빡이게 만듭니다. ('player' 또는 'monster')"""
    
    target_surface = None
    target_pos = (0, 0)

    if target_character == 'player':
        target_surface = ME
        target_pos = (sX + 320 - ME.get_width() // 2, sY + 536 - ME.get_height())
    elif target_character == 'monster' and hasattr(enemyCSmon, 'image'):
        # 몬스터 이미지를 동적으로 로드하고 위치를 계산
        enemy_image_surface = pygame.image.load(enemyCSmon.image).convert_alpha()
        enemy_image_surface = pygame.transform.scale_by(enemy_image_surface, 10)
        target_surface = enemy_image_surface
        target_pos = (esX + 900 - target_surface.get_width() // 2, esY + 305 - target_surface.get_height())
    
    if not target_surface:
        return # 대상이 없으면 함수 종료

    red_surface = target_surface.copy()
    red_surface.fill((255, 60, 60, 150), special_flags=pygame.BLEND_RGBA_MULT)
    
    duration = 300  # 애니메이션 총 지속 시간 (ms)
    interval = 100   # 각 깜빡임 사이의 간격 (ms)
    start_time = pygame.time.get_ticks()
    
    while pygame.time.get_ticks() - start_time < duration:
        current_time = pygame.time.get_ticks() - start_time
        display_status(screen, detail=True) # 매 프레임 화면을 다시 그림
        
        # 간격에 따라 붉은색 오버레이를 그림
        if (current_time % interval) < (interval / 2):
            screen.blit(red_surface, target_pos)
        
        pygame.display.flip()

    # 애니메이션이 끝난 후 화면을 한 번 더 깔끔하게 업데이트
    display_status(screen, detail=True)
    pygame.display.flip()
            
def display_status(screen, detail=True, skill_frame_to_draw=None):
    """상태 화면 표시 - 플레이어 직접 전투용으로 수정 (스킬 레이어 처리 기능 추가)"""
    screen.fill((113,113,113))
    screen.blit(BACKGROUND, (sX, sY))

    # 스킬 프레임이 전달된 경우, 배경 위에 먼저 그립니다.
    if skill_frame_to_draw:
        screen.blit(skill_frame_to_draw, (sX, sY))
    
    # 배틀 정보 출력
    draw_text(screen, f"플레이어: {player.name}", sX, sY+820, VIOLET)
    draw_text(screen, f"현재 학기: {player.current_semester}", sX, sY+860, BLUE)
    draw_text(screen, f"턴 {hap_num}", sX, sY+900, CYAN)
    gpa = gpaCalculator(enemyCSmon, hap_num, item_num)[1]
    draw_text(screen, f"현재 성적: ", sX, sY+940, GREEN)
    draw_text(screen, f"{gpa}", sX+200, sY+940, gpaColor(gpa))
    
    # 적 스프라이트
    if hasattr(enemyCSmon, 'is_defeated') and enemyCSmon.is_defeated:
        if hasattr(enemyCSmon, 'image'):
            enemy_img = pygame.image.load(enemyCSmon.image).convert_alpha()
            silhouette = pygame.transform.scale_by(enemy_img, 10)
            dark_fill = (30, 30, 30)
            silhouette.fill(dark_fill, special_flags=pygame.BLEND_RGB_MULT)
            screen.blit(silhouette, (esX+900-silhouette.get_width()//2, esY+305-silhouette.get_height()))
    elif hasattr(enemyCSmon, 'image'):
        image = pygame.image.load(enemyCSmon.image).convert_alpha()
        image = pygame.transform.scale_by(image, 10)
        screen.blit(image, (esX+900-image.get_width()//2, esY+305-image.get_height()))

    # 내 스프라이트 그리기
    if hasattr(player, 'is_defeated') and player.is_defeated:
        silhouette = ME.copy()
        dark_fill = (30, 30, 30)
        silhouette.fill(dark_fill, special_flags=pygame.BLEND_RGB_MULT)
        screen.blit(silhouette, (sX+320-ME.get_width()//2, sY+536-ME.get_height()))
    else:
        screen.blit(ME, (sX+320-ME.get_width()//2, sY+536-ME.get_height()))
    
    # 적 상태
    screen.blit(STAT, (esX, esY))
    draw_text(screen, f"{enemyCSmon.name}", esX+64, esY+70, WHITE)
    draw_text(screen, f"lv {enemyCSmon.level}", esX+384, esY+70, WHITE)
    animate_health_bar(screen, esY+121, esX+122, enemyCSmon.nowhp, enemyCSmon.nowhp, enemyCSmon.HP)
    
    # 적 타입 표시
    enemy_types = getattr(enemyCSmon, 'type', ['전산이론'])
    if isinstance(enemy_types, str):
        enemy_types = [enemy_types]
    for i, enemy_type in enumerate(enemy_types[:2]):
        display_type(screen, esY, esX+470, enemy_type)
    if any(rank != 0 for rank in enemyCSmon.Rank):
        screen.blit(RANK, (esX+470+160, esY))
        for i, rank in enumerate(enemyCSmon.Rank):
            draw_text(screen, "ATK" if i==0 else "DEF" if i==1 else "SPD", esX+470+160+20, esY+30+i*44, WHITE)
            draw_text(screen, f"{'+' if rank>=0 else ''}{rank}", esX+470+160+80, esY+30+i*44, RED if rank<0 else GREEN if rank>0 else WHITE)

    # 디버그/치트모드 시 상대 능력치 표시
    dbg = getattr(player, "debug_config", None)
    show_debug_overlay = player.cheatmode or (dbg and dbg.debug)
    
    if show_debug_overlay:
        draw_text(screen, f"{getattr(enemyCSmon, 'nowhp', getattr(enemyCSmon, 'HP', 100))}/{getattr(enemyCSmon, 'HP', 100)}", esX+445, esY+100, WHITE, highlight=VIOLET)
        draw_text(screen, f"ATK {getattr(enemyCSmon, 'CATK', 10)}/{getattr(enemyCSmon, 'ATK', 10)}", esX+610, esY+16, WHITE, highlight=RED)
        draw_text(screen, f"DEF {getattr(enemyCSmon, 'CDEF', 10)}/{getattr(enemyCSmon, 'DEF', 10)}", esX+610, esY+56, WHITE, highlight=RED)
        draw_text(screen, f"SPD {getattr(enemyCSmon, 'CSPD', 10)}/{getattr(enemyCSmon, 'SPD', 10)}", esX+610, esY+96, WHITE, highlight=RED)
        
        if dbg and dbg.debug:
            draw_text(screen, "DEBUG", 50, 50, YELLOW, size=24)
            
    # 플레이어 상태 (하단)
    screen.blit(STAT, (psX, psY))
    
    draw_text(screen, f"{player.name}", psX+64, psY+70, WHITE)
    draw_text(screen, f"lv {player.level}", psX+384, psY+70, WHITE)

    # 플레이어 타입 표시
    display_type(screen, psY, psX+470, player.type[0])
    
    # 플레이어 체력바
    animate_health_bar(screen, psY+121, psX+122, player.nowhp, player.nowhp, player.HP)

    if detail:
        display_player_details(screen, player, sX+1264)

    screen.blit(TEXT, (sX+11, sY+535))
    draw_text(screen, "Enter를 눌러 확인", SCREEN_WIDTH//2, SCREEN_HEIGHT - 60, LIGHTGRAY, align='center')

def display_player_details(screen, player, x):
    """플레이어 상세 정보 출력"""

    # [True, False, False, False, False, False] 형식
    current_skill_boolean = [player.current_skills[t] > 0 for t in ["*", "CT", "DS", "PS", "SYS", "AI"]]

    def get_color_by_level_skill(current_skill_boolean, type_index = 0):

        type  = ["*", "CT", "DS", "PS", "SYS", "AI"][type_index]

        if not current_skill_boolean[type_index]:
            return GRAY
        else:
            if player.learned_skills[type] == 0:
                return GRAY
            elif player.learned_skills[type] < 2:
                return WHITE
            elif player.learned_skills[type] < 4:
                return YELLOW
            elif player.learned_skills[type] < 5:
                return ORANGE
            else:
                return RED

    details = [
        (("이름", 0, WHITE), (f"{player.name}", 228, CYAN)),
        (("레벨", 0, WHITE), (f"{player.level}", 228, CYAN)),
        (("다음 레벨까지", 0, WHITE), (f"{player.max_exp - player.exp}", 228, BLUE), ("경험치 남음", 352, WHITE)),
        "",
        (("체력", 0, WHITE), (f"{player.nowhp}"+"/"+f"{player.HP}", 228, CYAN)),
        (("공격", 0, WHITE), (f"{player.CATK}", 228, GREEN if player.CATK > player.ATK else RED if player.CATK < player.ATK else WHITE), None if player.Rank[0]==0 else ((("+" if player.Rank[0]>0 else "-") + f"{abs(player.Rank[0])}랭크"), 292, RED if player.Rank[0]<0 else GREEN)),
        (("방어", 0, WHITE), (f"{player.CDEF}", 228, GREEN if player.CDEF > player.DEF else RED if player.CDEF < player.DEF else WHITE), None if player.Rank[1]==0 else ((("+" if player.Rank[1]>0 else "-") + f"{abs(player.Rank[1])}랭크"), 292, RED if player.Rank[1]<0 else GREEN)),
        (("속도", 0, WHITE), (f"{player.CSPD}", 228, GREEN if player.CSPD > player.SPD else RED if player.CSPD < player.SPD else WHITE), None if player.Rank[2]==0 else ((("+" if player.Rank[2]>0 else "-") + f"{abs(player.Rank[2])}랭크"), 292, RED if player.Rank[2]<0 else GREEN)),
        "",
        (("현재 학기", 0, WHITE), (f"{player.current_semester}", 228, WHITE)),
        "",
        (("스킬 별 레벨", 0, WHITE), ("", 0, WHITE)),
        (("  *   ", 0 , STARC if current_skill_boolean[0] else GRAY), (f"Level {player.learned_skills['*']}", 228, get_color_by_level_skill(current_skill_boolean, 0))),
        (("  CT  ", 0 , CTC if current_skill_boolean[1] else GRAY), (f"Level {player.learned_skills['CT']}", 228, get_color_by_level_skill(current_skill_boolean, 1))),
        (("  DS  ", 0 , DSC if current_skill_boolean[2] else GRAY), (f"Level {player.learned_skills['DS']}", 228, get_color_by_level_skill(current_skill_boolean, 2))),
        (("  PS  ", 0 , PSC if current_skill_boolean[3] else GRAY), (f"Level {player.learned_skills['PS']}", 228, get_color_by_level_skill(current_skill_boolean, 3))),
        (("  SYS ", 0 , SYSC if current_skill_boolean[4] else GRAY), (f"Level {player.learned_skills['SYS']}", 228, get_color_by_level_skill(current_skill_boolean, 4))),
        (("  AI  ", 0 , AIC if current_skill_boolean[5] else GRAY), (f"Level {player.learned_skills['AI']}", 228, get_color_by_level_skill(current_skill_boolean, 5))),
    ]
    
    for i, detail_item in enumerate(details):
        y_pos = sY + 50 + i * 40
        if isinstance(detail_item, tuple):
            for detail in detail_item:
                if not isinstance(detail, tuple) and not isinstance(detail, str):
                    continue
                if isinstance(detail, tuple) and len(detail) >= 3:
                    draw_text(screen, detail[0], x + detail[1], y_pos, detail[2])

def select_action(screen):
    """행동 선택 메뉴 - PNR 버튼 포함"""
    display_status(screen, detail=True)
    
    # 기본 옵션들
    options = ["스킬 사용", "아이템 사용", "도망가기"]
    if player.current_semester == "새터":
        options = ["스킬 사용"]
    
    # PNR 버튼 추가 (조건부)
    if player.can_use_pnr():
        options.append("PNR 사용")
    
    current_index = 0
    
    while True:
        display_status(screen, detail=True)
        
        for i, option in enumerate(options):
            x_pos = stX + (300 * (i % 2))
            y_pos = stY + int(i / 2) * 64
            
            # PNR 버튼은 파란색으로 표시
            color = BLUE if option == "PNR 사용" else WHITE
            
            prefix = "> " if i == current_index else "  "
            draw_text(screen, prefix, x_pos, y_pos, WHITE if i == current_index else GRAY)
            draw_text(screen, f"{option}", x_pos+32, y_pos, color)
        
        pygame.display.flip()
        
        key = wait_for_key(Noescape=True)
        if key == 'enter':
            return current_index
        elif key == 'tab':
            # 디버그 스킵 기능
            dbg = getattr(player, "debug_config", None)
            if dbg and dbg.skip:
                return -999  # 특별한 값으로 스킵 신호
        elif len(options) == 1:
            current_index = 0
        elif key == 'up' and (current_index > 1 and current_index < len(options)):
            current_index -= 2
            option_change_sound()
        elif key == 'down' and (current_index >= 0 and current_index < len(options)-2):
            current_index += 2
            option_change_sound()
        elif key == 'left' and (current_index % 2 == 1 and current_index < len(options) and current_index >= 0):
            current_index -= 1
            option_change_sound()
        elif key == 'right' and (current_index % 2 == 0 and current_index < len(options) and current_index >= 0 and current_index != len(options)-1):
            current_index += 1
            option_change_sound()

def get_color_by_effectiveness(effectiveness):
    if effectiveness > 1.5:             # 2배
        return RED
    elif 0.4 <= effectiveness < 0.8:    # 0.5배
        return LIGHTGRAY
    elif effectiveness < 0.4:           # 0배
        return GRAY
    else:                               # 1배
        return WHITE

def select_player_skill(screen):
    """플레이어 스킬 선택"""
    available_skills = player.get_available_skills()
    
    if not available_skills:
        display_status(screen, True)
        draw_text(screen, "  사용할 수 있는 스킬이 없습니다!", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()
        return -1
    
    current_index = 0
    
    while True:
        display_status(screen, True)
        
        # 스킬 목록 표시
        for i, skill in enumerate(available_skills):
            x_pos = stX + (300 * (i % 2))
            y_pos = stY + int(i / 2) * 69 - 5
            effectiveness = comp(skill["type"], enemyCSmon.type[0])
            
            # 스킬 표시
            prefix = "> " if i == current_index else "  "
            prefix_color = WHITE if i == current_index else GRAY  # 원하는 색상 지정
            draw_text(screen, prefix, x_pos, y_pos+5, prefix_color)
            draw_text(screen, skill['name'], x_pos + 32, y_pos, get_color_by_effectiveness(effectiveness))
            # draw_text(screen, skill['name'], x_pos + 32, y_pos, get_color_by_effectiveness(effectiveness), highlight= typecolor_dict[skill['type']])

            # 효과 표시
            if get_color_by_effectiveness(effectiveness) == RED:
                draw_text(screen, "효과가 굉장함", x_pos + 32, y_pos + 35, RED, size=16)
            elif get_color_by_effectiveness(effectiveness) == GRAY:
                draw_text(screen, "효과 없음", x_pos + 32, y_pos + 35, GRAY, size=16)
            elif get_color_by_effectiveness(effectiveness) == LIGHTGRAY:
                draw_text(screen, "효과가 별로임", x_pos + 32, y_pos + 35, LIGHTGRAY, size=16)
            else:
                draw_text(screen, "효과 있음", x_pos + 32, y_pos + 35, WHITE, size=16)

            if i == current_index:
                # 선택된 스킬 상세정보 표시
                # 선택된 스킬의 상세정보 표시
                infoX = sX+621
                infoY = sY+535
                infoText = infoX + 200
                
                display_type(screen, infoY, infoX, skill['type'])
                screen.blit(SKILL, (infoX+160, infoY))
                draw_text(screen, "타입", infoText - 25, infoY+30, WHITE)
                draw_text(screen, f"{type_dict[skill['type']]}", infoText+344, infoY+24, typecolor_dict[skill['type']], align='right')
                
                draw_text(screen, "위력", infoText - 25, infoY+70, WHITE)
                draw_text(screen,f"{skill['skW']}", infoText+344, infoY+64, WHITE, align='right')
                draw_wrapped_text(
                    screen,
                    skill['description'],
                    infoText - 25,
                    infoY + 115,
                    WHITE,
                    font_size=16,
                    max_width= 344 # 원하는 최대 너비 지정
                )
        if i < 3:
            for j in range(i+1, 4):
                x_pos = stX + (300 * (j % 2))
                y_pos = stY + int(j / 2) * 61 - 5
                prefix = "> " if j == current_index else "  "
                prefix_color = WHITE if i == current_index else GRAY  # 원하는 색상 지정
                draw_text(screen, prefix, x_pos, y_pos+5, prefix_color)
                draw_text(screen, "빈 슬롯", x_pos + 32, y_pos, CYAN)
        
        pygame.display.flip()
        
        key = wait_for_key()
        if key == 'enter':
            if current_index >= len(available_skills):
                display_status(screen, True)
                draw_text(screen, "  빈 슬롯이다!", stX, stY, WHITE)
                pygame.display.flip()
                wait_for_key()
                continue
            selected_skill = available_skills[current_index]
            return selected_skill
        elif key == 'escape':
            option_escape_sound()
            return -1
        elif key == 'up' and (current_index > 1 and current_index < 4):
            current_index -= 2
            option_change_sound()
        elif key == 'down' and (current_index >= 0 and current_index < 4-2):
            current_index += 2
            option_change_sound()
        elif key == 'left' and (current_index % 2 == 1 and current_index < 4 and current_index >= 0):
            current_index -= 1
            option_change_sound()
        elif key == 'right' and (current_index % 2 == 0 and current_index < 4 and current_index >= 0 and current_index != 4-1):
            current_index += 1
            option_change_sound()

def show_pnr_result(screen, success):
    """PNR 사용 결과 표시"""
    screen.fill(WHITE)
    draw_text(screen, "PNR을 사용하였습니다.", SCREEN_WIDTH//2, SCREEN_HEIGHT//2, BLACK, align='center')
    pygame.display.flip()
    time.sleep(1)
    screen.fill(WHITE)
    draw_text(screen, "PNR을 사용하였습니다..", SCREEN_WIDTH//2, SCREEN_HEIGHT//2, BLACK, align='center')
    pygame.display.flip()
    time.sleep(1)
    screen.fill(WHITE)
    draw_text(screen, "PNR을 사용하였습니다...", SCREEN_WIDTH//2, SCREEN_HEIGHT//2, BLACK, align='center')
    pygame.display.flip()
    time.sleep(1)
    screen.fill(WHITE)
    color = GREEN if success=="P" else RED
    message = "성공!" if success == "P" else "실패..."
    draw_text(screen, message, SCREEN_WIDTH//2, 300, color, align='center')
    Battle_win() if success == "P" else Lose()
    pygame.display.flip()
    wait_for_key()    
    if success == "P":
        draw_text(screen, "P를 받는데에 성공하였습니다!", SCREEN_WIDTH//2, 350, BLACK, align='center')
    else:
        draw_text(screen, "NR이 떠 버리고 말았습니다...", SCREEN_WIDTH//2, 350, BLACK, align='center')
    
    draw_text(screen, "아무 키나 눌러 계속...", SCREEN_WIDTH//2, 450, BLACK, align='center')
    
    pygame.display.flip()
    wait_for_key()

def gpaCalculator(enemy, hap_num, item_num):
    score = max(0, (17-hap_num)/16) * 0.3 + max(0, (3-item_num)/3) * 0.3 + (1-(startBattleHp-player.nowhp)/player.HP)*0.4
    if score >= 0.90: gpa = "A+"
    elif score >= 0.80: gpa = "A0"
    elif score >= 0.70: gpa = "A-"
    elif score >= 0.60: gpa = "B+"
    elif score >= 0.40: gpa = "B0"
    elif score >= 0.30: gpa = "B-"
    elif score >= 0.20: gpa = "C+"
    elif score >= 0.10: gpa = "C0"
    else: gpa = "C-"
    return (enemy.credit, gpa)

def skill_phase(screen):
    selected_skill = select_player_skill(screen)
    if selected_skill == -1:
        return -1
    
    # 지능형 알고리즘을 사용한 적 스킬 선택
    enemy_skill = get_best_enemy_skill(enemyCSmon, player)

    # 스킬 우선순위에 따른 턴 진행
    if selected_skill["priority"] > enemy_skill.priority or (selected_skill["priority"] == enemy_skill.priority and player.CSPD >= enemyCSmon.CSPD):
        # 플레이어 스킬 사용
        stop = player_skill_phase(screen, selected_skill, enemy_skill)
        
        # 몬스터가 살아있고, 턴이 중단되지 않았다면 몬스터 스킬 사용
        if enemyCSmon.is_alive() and not stop:
            enemy_attack_phase(screen, selected_skill, enemy_skill)
            
    else:
        # 몬스터 스킬 사용
        stop = enemy_attack_phase(screen, selected_skill, enemy_skill)
        
        # 플레이어가 살아있고, 턴이 중단되지 않았다면 플레이어 스킬 사용
        if player.is_alive() and not stop:
            player_skill_phase(screen, selected_skill, enemy_skill)

def skill_message(screen, AttackerType, player, enemyCSmon, Pskill, Mskill, damage = None, Mul=1):
    if Pskill is None:
        playerskill_dict = None
    else:
        playerskill_dict = {
            "name": Pskill["name"],
            "type": Pskill["type"],
            "effect_type": Pskill["effect_type"],
            "skW": Pskill["skW"]
        }
    if Mskill is None:
        monsterskill_dict = None
    else:
        monsterskill_dict = {
            "name": Mskill.name,
            "type": Mskill.skill_type, 
            "effect_type": Mskill.effect_type, 
            "skW": Mskill.skW
        }
        if isinstance(Mskill.skW, str):
            if Mskill.skW == "DEF":
                monsterskill_dict["skW"] = 10+40*(max(1, Mskill.Rank[1]))
            elif Mskill.skW == "SPD":
                monsterskill_dict["skW"] = 10+50*(max(1, Mskill.Rank[2]))

    """스킬 메시지를 출력하기 전에 상태를 먼저 출력 (pygame)"""
    if damage != None:
        damage = int(damage)
    # 스킬 메시지 출력
    if AttackerType == "player":
        user = player
        target = enemyCSmon
        skill = playerskill_dict
        counter_skill = monsterskill_dict
    else:
        user = enemyCSmon
        target = player
        skill = monsterskill_dict
        counter_skill = playerskill_dict
    
    display_status(screen, True)  # 상태 출력
    
    if skill["effect_type"] == "reflect":
        if damage == -121:
            draw_text(screen, "  하지만 실패했다!", stX, stY, WHITE)
        elif counter_skill is not None:
            if counter_skill["effect_type"] == "Pdamage" or counter_skill["effect_type"] == "Sdamage":
                if skill["skW"] == 0:
                    draw_text(screen, f"  {user.name}이/가 {target.name}의 {counter_skill['name']}을/를 방어했다.", stX, stY, WHITE)
                else:
                    draw_text(screen, f"  {user.name}이/가 {target.name}의 {counter_skill['name']}을/를 반사!", stX, stY, WHITE)
                    pygame.display.flip()
                    wait_for_key()
                    display_status(screen, True)  # 상태 출력 
                    if damage  == False:
                        if Mul == 0:
                            draw_text(screen, "  효과가 없는 것 같다...", stX, stY, WHITE)
                        else:
                            draw_text(screen, f"  그러나 {user.name}의 공격은 빗나갔다!", stX, stY, WHITE)
                    else:
                        draw_text(screen, f"  {target.name}이/가 {damage}의 피해를 입었다.", stX, stY, WHITE)
                        if Mul >= 1.7:
                            pygame.display.flip()
                            wait_for_key()
                            draw_text(screen, "  효과가 굉장했다!", stX, stY, WHITE)
                            display_status(screen, True)  # 상태 출력
                        elif Mul < 0.8:
                            pygame.display.flip()
                            wait_for_key()
                            draw_text(screen, "  효과가 별로인 듯 하다...", stX, stY, WHITE)
                            display_status(screen, True)  # 상태 출력
            else:
                draw_text(screen, "  그러나 아무 일도 일어나지 않았다!", stX, stY, WHITE)
        else:
            draw_text(screen, "  그러나 아무 일도 일어나지 않았다!", stX, stY, WHITE)

    elif skill["effect_type"] == "Pdamage" or skill["effect_type"] == "Sdamage":
        if damage  == False:
            if Mul == 0:
                draw_text(screen, "  효과가 없는 것 같다...", stX, stY, WHITE)
            else:
                draw_text(screen, f"  그러나 {user.name}의 공격은 빗나갔다!", stX, stY, WHITE)
        else:
            if Mul >= 1.7:
                draw_text(screen, "  효과가 굉장했다!", stX, stY, WHITE)
                pygame.display.flip()
                wait_for_key()
            elif Mul <= 0.8:
                draw_text(screen, "  효과가 별로인 듯 하다...", stX, stY, WHITE)
                pygame.display.flip()
                wait_for_key()
            display_status(screen, True)  # 상태 출력
            draw_text(screen, f"  {target.name}이/가 {damage}의 데미지를 입었다.", stX, stY, WHITE)

    elif skill["effect_type"] == "halve_hp":
        if damage == False:
            draw_text(screen, f"  그러나 {user.name}의 공격은 빗나갔다!", stX, stY, WHITE)
        else:
            draw_text(screen, f"  {target.name}이/가 {damage}의 데미지를 입었다!", stX, stY, WHITE)
            pygame.display.flip()
            wait_for_key()
            display_status(screen, True)  # 상태 출력
            draw_text(screen, f"  {target.name}의 체력이 반으로 줄었다!", stX, stY, WHITE)
            
    elif skill["effect_type"] == "heal":
        heal_amount = int(skill["skW"] * user.HP)
        draw_text(screen, f"  {user.name}의 체력이 {heal_amount} 회복되었다!", stX, stY, WHITE)

    elif skill["effect_type"] == "buff":
        if isinstance(skill["skW"], tuple):
            for B in skill["skW"]:
                buffAnimation(B>=0, "player" if AttackerType=="player" else "monster")
                if B % 3 == 0:
                    draw_text(screen, f"  {user.name}의 공격이 " + (f"{B//3 + 1}랭크 증가했다!" if B//3 >= 0 else f"{-(B//3 + 1)}랭크 감소했다!"), stX, stY, WHITE)
                elif B % 3 == 1:
                    draw_text(screen, f"  {user.name}의 방어가 " + (f"{B//3 + 1}랭크 증가했다!" if B//3 >= 0 else f"{-(B//3 + 1)}랭크 감소했다!"), stX, stY, WHITE)
                elif B % 3 == 2:
                    draw_text(screen, f"  {user.name}의 스피드가 " + (f"{B//3 + 1}랭크 증가했다!" if B//3 >= 0 else f"{-(B//3 + 1)}랭크 감소했다!"), stX, stY, WHITE)
                if B != skill["skW"][-1]:
                    pygame.display.flip()
                    wait_for_key(False)
                    display_status(screen, True)  # 상태 출력
        else:
            buffAnimation(skill['skW']>=0, "player" if AttackerType=="player" else "monster")
            if skill['skW'] % 3 == 0:
                draw_text(screen, f"  {user.name}의 공격이 " + (f"{skill['skW']//3 + 1}랭크 증가했다!" if skill['skW']//3 >= 0 else f"{-(skill['skW']//3 + 1)}랭크 감소했다!"), stX, stY, WHITE)
            elif skill['skW'] % 3 == 1:
                draw_text(screen, f"  {user.name}의 방어가 " + (f"{skill['skW']//3 + 1}랭크 증가했다!" if skill['skW']//3 >= 0 else f"{-(skill['skW']//3 + 1)}랭크 감소했다!"), stX, stY, WHITE)
            elif skill['skW'] % 3 == 2:
                draw_text(screen, f"  {user.name}의 스피드가 " + (f"{skill['skW']//3 + 1}랭크 증가했다!" if skill['skW']//3 >= 0 else f"{-(skill['skW']//3 + 1)}랭크 감소했다!"), stX, stY, WHITE)
    pygame.display.flip()
    wait_for_key(sound=False)  # 메시지를 잠시 보여줌

def player_skill_phase(screen, selected_skill, enemy_skill):
    # playerCurrentHP, enemyCurrentHP 변수는 이제 필요 없습니다.
    
    # 스킬 사용 메시지
    display_status(screen, True)
    draw_text(screen, f"  {player.name}의 {selected_skill['name']}!", stX, stY, WHITE)
    pygame.display.flip()
    wait_for_key(False)

    # 스킬 효과 적용
    stop, damage, Mul = use_skill("player", player, enemyCSmon, selected_skill, enemy_skill, screen)
    if isinstance(Mul, tuple):
        skill_message(screen, "player", player, enemyCSmon, selected_skill, enemy_skill, damage, Mul[0])
        bonusskilldict = {
            "name": selected_skill["name"],
            "type": selected_skill["type"],
            "effect_type": selected_skill["bonus_effect"][0],
            "skW": selected_skill["bonus_effect"][1] if not isinstance(selected_skill["bonus_effect"][1], str) else selected_skill["bonus_effect"][2]
        }
        skill_message(screen, "player", player, enemyCSmon, bonusskilldict, enemy_skill, None, Mul[0])
    else: skill_message(screen, "player", player, enemyCSmon, selected_skill, enemy_skill, damage, Mul)
    option_select_sound()
    return stop

def enemy_attack_phase(screen, selected_skill, enemy_skill):
    # 스킬 사용 메시지
    display_status(screen, True)
    draw_text(screen, f"  {enemyCSmon.name}의 {enemy_skill.name}!", stX, stY, WHITE)
    pygame.display.flip()
    wait_for_key(False)

    # 스킬 효과 적용
    display_status(screen, True)
    stop, damage, Mul = use_skill("monster", player, enemyCSmon, selected_skill, enemy_skill, screen)
    skill_message(screen, "monster", player, enemyCSmon, selected_skill, enemy_skill, damage, Mul)

    return stop

def select_item(screen, temp=None):
    """아이템 선택 - 플레이어용"""

    # 빈 슬롯을 맨 뒤로 보내기 위해 정렬
    sorted_items = sorted(player.items, key=lambda x: x.name == "빈 슬롯")
    player.items = sorted_items  # 플레이어 아이템 순서도 변경
    descriptions = [i.description for i in sorted_items]
    coloring = [False]*len(sorted_items)

    for i in range(len(sorted_items)):
        if sorted_items[i].name == "빈 슬롯":
            coloring[i] = CYAN
        else:
            coloring[i] = get_item_color_by_grade(sorted_items[i].grade)

    display_status(screen)
    current_index = 0
    
    while True:
        display_status(screen)
        
        for i, item in enumerate(sorted_items):
            x_pos = stX + (200 * (i % 3))
            y_pos = stY + int(i / 3) * 64

            color = coloring[i] if coloring[i] else WHITE
            
            # 스킬 표시
            prefix = "> " if i == current_index else "  "
            prefix_color = WHITE if i == current_index else GRAY  # 원하는 색상 지정
            draw_text(screen, prefix, x_pos, y_pos, prefix_color)
            draw_text(screen, f"{item.name}", x_pos + 32, y_pos, color)
            infoY = sY+536
            if i == current_index:
                draw_wrapped_text(
                    screen,
                    descriptions[i],
                    sX+660,
                    infoY + 20,
                    WHITE,
                    font_size=32,
                    max_width= 560 # 원하는 최대 너비 지정
                )
        
        pygame.display.flip()
        
        key = wait_for_key()
        if key == 'enter':
            if player.items[current_index].name == "빈 슬롯":
                display_status(screen)
                draw_text(screen, "  빈 슬롯이다!", stX, stY, WHITE)
                pygame.display.flip()
                wait_for_key()
                continue
            return current_index
        elif key == 'escape':
            option_escape_sound()
            return -1
        elif len(player.items) == 1:
            current_index = 0
        elif key == 'up' and (current_index > 2 and current_index < len(player.items)):
            current_index -= 3
            option_change_sound()
        elif key == 'down' and (current_index >= 0 and current_index < len(player.items)-3):
            current_index += 3
            option_change_sound()
        elif key == 'left' and (current_index % 3 != 0 and current_index < len(player.items) and current_index >= 0):
            current_index -= 1
            option_change_sound()
        elif key == 'right' and (current_index % 3 != 2 and current_index < len(player.items) and current_index >= 0 and current_index != len(player.items)-1):
            current_index += 1
            option_change_sound()

def item_phase(screen):
    """아이템 사용 단계 - 플레이어용"""
    global item_num

    playerCurrentHP = player.nowhp
    enemyCurrentHP = getattr(enemyCSmon, 'nowhp', getattr(enemyCSmon, 'HP', 100))
    
    chosen_idx = select_item(screen)
    if chosen_idx == -1:
        return -1
    
    selected_item = player.items[chosen_idx]
    
    display_status(screen)
    draw_text(screen, f"  {selected_item.name}을/를 사용했다!", stX, stY, WHITE)
    pygame.display.flip()
    # 아이템 사용 횟수 카운트만 올리기 (전역 카운터)
    item_num += 1
    wait_for_key(False)

    # 아이템 효과 적용
    # heal, damage, buff, debuff

    # 특수효과 아이템 (GPT)
    if selected_item.special:
        if selected_item.name == "GPT":
            enemyCSmon.nowhp = 1
            Effective()
            animate_health_bar(screen, esY+121, esX+122, enemyCurrentHP, 1, getattr(enemyCSmon, 'HP', 100))
            display_status(screen)
            draw_text(screen, f"  {enemyCSmon.name}의 체력이 1이 되었다!", stX, stY, WHITE)
    
    elif selected_item.effect == "heal":
        heal_amount_req = 0
        
        # MonsterZero처럼 varied가 1인 경우 (전체 회복)
        if selected_item.varied == 1:
            heal_amount_req = player.HP - player.nowhp
        
        # 아메리카노처럼 fixed와 varied가 모두 있는 경우 (큰 값 선택)
        elif selected_item.fixed > 0 and selected_item.varied > 0:
            heal_base = selected_item.fixed
            heal_pct = int(player.HP * selected_item.varied)
            heal_amount_req = max(heal_base, heal_pct)
        
        # 구글신, 에너지바처럼 fixed만 있는 경우
        elif selected_item.fixed > 0:
            heal_amount_req = selected_item.fixed
        
        # 그 외 varied만 있는 경우 (에너지바의 varied=0.1처럼)
        elif selected_item.varied > 0:
            heal_amount_req = int(player.HP * selected_item.varied)
        healAnimation()
        healed = player.heal(heal_amount_req, allow_revive=getattr(selected_item, "canuse_on_fainted", False))
        animate_health_bar(screen, psY+121, psX+122, playerCurrentHP, player.nowhp, player.HP)
        display_status(screen)
        draw_text(screen, f"  {player.name}의 체력이 {healed} 회복되었다!", stX, stY, WHITE)

    elif selected_item.effect == "damage":
        if selected_item.name == "렉쳐노트":
            new_hp = int(enemyCSmon.nowhp * 0.5)
            damage_amount = enemyCSmon.nowhp - new_hp
            enemyCSmon.nowhp = new_hp
        else:
            base = selected_item.fixed if selected_item.fixed else 0
            pct  = int(getattr(enemyCSmon, "HP", enemyCurrentHP) * selected_item.varied) if selected_item.varied else 0
            damage_amount = max(base, pct)
            enemyCSmon.take_damage(damage_amount)
        enemy_hp_after = getattr(enemyCSmon, 'nowhp', getattr(enemyCSmon, 'HP', 100))
        NormalDamage()
        animate_health_bar(screen, esY+121, esX+122, enemyCurrentHP, enemy_hp_after, getattr(enemyCSmon, 'HP', 100))

        display_status(screen)
        draw_text(screen, f"  {enemyCSmon.name}에게 {damage_amount}의 데미지를 입혔다!", stX, stY, WHITE)

    elif selected_item.effect == "buff":
        if isinstance(selected_item.fixed, tuple):
            for B in selected_item.fixed:
                player.Rank[B % 3] = max(-6,min(6, player.Rank[B % 3] + B//3 + 1))
                buffAnimation(B>=0, "player")
                display_status(screen)
                if B % 3 == 0:
                    draw_text(screen, f"  {player.name}의 공격력이 {B//3 + 1}랭크 증가했다!", stX, stY, WHITE)
                elif B % 3 == 1:
                    draw_text(screen, f"  {player.name}의 방어력이 {B//3 + 1}랭크 증가했다!", stX, stY, WHITE)
                elif B % 3 == 2:
                    draw_text(screen, f"  {player.name}의 속도가 {B//3 + 1}랭크 증가했다!", stX, stY, WHITE)
                if B != selected_item.fixed[-1]:
                    pygame.display.flip()
                    wait_for_key(False)
                    display_status(screen)
        else:
            player.Rank[selected_item.fixed % 3] = max(-6,min(6, player.Rank[selected_item.fixed % 3] + selected_item.fixed//3 + 1))
            buffAnimation(selected_item.fixed>=0, "player")
            display_status(screen)
            if selected_item.fixed % 3 == 0:
                draw_text(screen, f"  {player.name}의 공격력이 {selected_item.fixed//3 + 1}랭크 증가했다!", stX, stY, WHITE)
            elif selected_item.fixed % 3 == 1:
                draw_text(screen, f"  {player.name}의 방어력이 {selected_item.fixed//3 + 1}랭크 증가했다!", stX, stY, WHITE)
            elif selected_item.fixed % 3 == 2:
                draw_text(screen, f"  {player.name}의 속도가 {selected_item.fixed//3 + 1}랭크 증가했다!", stX, stY, WHITE)

        player.update_battle()

    elif selected_item.effect == "debuff":
        if isinstance(selected_item.fixed, tuple):
            for B in selected_item.fixed:
                enemyCSmon.Rank[B % 3] = max(-6,min(6, enemyCSmon.Rank[B % 3] + B//3 + 1))
                buffAnimation(B>=0, "monster")
                display_status(screen)
                if B % 3 == 0:
                    draw_text(screen, f"  {enemyCSmon.name}의 공격력이 {-(B//3 + 1)}랭크 감소했다!", stX, stY, WHITE)
                elif B % 3 == 1:
                    draw_text(screen, f"  {enemyCSmon.name}의 방어력이 {-(B//3 + 1)}랭크 감소했다!", stX, stY, WHITE)
                elif B % 3 == 2:
                    draw_text(screen, f"  {enemyCSmon.name}의 속도가 {-(B//3 + 1)}랭크 감소했다!", stX, stY, WHITE)
                if B != selected_item.fixed[-1]:
                    pygame.display.flip()
                    wait_for_key(False)
                    display_status(screen)
        else:
            enemyCSmon.Rank[selected_item.fixed % 3] = max(-6,min(6, enemyCSmon.Rank[selected_item.fixed % 3] + selected_item.fixed//3 + 1))
            buffAnimation(selected_item.fixed>=0, "monster")
            display_status(screen)
            if selected_item.fixed % 3 == 0:
                draw_text(screen, f"  {enemyCSmon.name}의 공격력이 {-(selected_item.fixed//3 + 1)}랭크 감소했다!", stX, stY, WHITE)
            elif selected_item.fixed % 3 == 1:
                draw_text(screen, f"  {enemyCSmon.name}의 방어력이 {-(selected_item.fixed//3 + 1)}랭크 감소했다!", stX, stY, WHITE)
            elif selected_item.fixed % 3 == 2:
                draw_text(screen, f"  {enemyCSmon.name}의 속도가 {-(selected_item.fixed//3 + 1)}랭크 감소했다!", stX, stY, WHITE)

        enemyCSmon.update_battle()
            
    pygame.display.flip()
    wait_for_key()
    
    # 아이템 제거
    from ForGrd.itemForGrd import Noneitem
    player.items[chosen_idx] = copy.deepcopy(Noneitem)
    
    enemy_skill = get_best_enemy_skill(enemyCSmon, player)
    enemy_attack_phase(screen, None, enemy_skill)
    
def get_random_reward_items(num_items):
    reward_pool = []
    
    droppable_items = []
    for i in range(100):
        if i<50:
            droppable_items.append(random.choice(list(item for item in items.values() if item.grade == "노말")))
        elif i<80:
            droppable_items.append(random.choice(list(item for item in items.values() if item.grade == "레어")))
        elif i<95:
            droppable_items.append(random.choice(list(item for item in items.values() if item.grade == "에픽")))
        else:
            droppable_items.append(random.choice(list(item for item in items.values() if item.grade == "레전더리")))
    while len(reward_pool) < num_items:
        droppedtem = random.choice(droppable_items)
        if droppedtem not in reward_pool:
            reward_pool.append(droppedtem)
        else: continue
            
    return reward_pool

def select_reward_item(screen, items):
    """승리 후 아이템 선택 UI"""
    current_index = 0
    while True:

        display_status(screen)
        # dark_overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        # dark_overlay.fill((0, 0, 0, 180))  # 마지막 값(120)은 투명도, 0~255
        # screen.blit(dark_overlay, (0, 0))

        apply_alpha_overlay(screen, (sX, sY, 2*psX + 4, 2*psY - 221))

        
        draw_text(screen, "  승리 보상! 아이템을 선택하자.", stX, stY, YELLOW)

        for i, item in enumerate(items):
            name_color = get_item_color_by_grade(item.grade)  # 등급별 색상 함수 사용

            prefix = "> " if i == current_index else "  "
            # 이름만 색상 적용, 설명은 그대로 WHITE
            draw_text(screen, f"{prefix}", stX, stY-400+i*100, WHITE)
            draw_text(screen, f"{item.name}", stX+30, stY-400+i*100, name_color)
            draw_text(screen, f"{item.gradeSymbol}{item.grade}", stX+30, stY-400+i*100+40, name_color, size=16)
            draw_wrapped_text(
                screen,
                item.description,
                stX+300,
                stY-400+i*100,
                WHITE,
                max_width= psX - sX + 300 # 원하는 최대 너비 지정
            )
        pygame.display.flip()
        key = wait_for_key()
        if key == 'enter':
            return items[current_index]
        elif key == 'up' and current_index > 0:
            current_index -= 1
            option_change_sound()
        elif key == 'down' and current_index < len(items)-1:
            current_index += 1
            option_change_sound()

        # Esc 누르면 아이템 획득 안함
        elif key == 'escape':
            return None

# 메인 전투 함수 수정
# 기존의 battle 함수를 아래 코드로 교체하세요.
def option_accept_challenge_molcamp(screen, options, y_offset = 30):
    current_index = 0
    while True:

        display_status(screen)
        screen.blit(SPEC_TEXT, (sX+11, sY+536 - 300))
        draw_text(screen, "몰입 캠프! 코드 문해력 퀴즈!", sX+8 + 300, sY+536 - 300 + 30, ORANGE, size = 32, align='center')
        draw_wrapped_text(screen, "수락한다면 주어진 파이썬 코드의 실행 결과(출력값)를 맞추는 미니게임에 도전하게 된다. ", sX+ 20 , sY+536 - 300 + 50 + y_offset, WHITE, max_width= 600, font_size=16)
        draw_wrapped_text(screen, "플레이어가 문제의 정답을 맞히면, 몰입 캠프에서 많은 경험치를 얻게 되어 빠르게 성장할 수 있다. 정답을 맞히지 못하면, 패널티 없이 전투가 계속 진행된다.", sX+20, sY+536 - 300 + 50 + y_offset * 3, WHITE, max_width= 600, font_size=16)
        draw_wrapped_text(screen, "정답을 맞혀 더 강한 자신이 되어 보자!", sX+20, sY+536 - 300 + 50 + y_offset * 6, WHITE, max_width= 600, font_size=16)
        draw_wrapped_text(screen, "도전을 수락할까?", sX+20, sY+536 - 300 + 50 + y_offset * 7, YELLOW, max_width= 600, font_size=16)

        for i, option in enumerate(options):
            x_pos = stX + (300 * (i % 2))
            y_pos = stY + int(i / 2) * 64

            prefix = "> " if i == current_index else "  "
            draw_text(screen, f"{prefix}{option}", x_pos, y_pos, WHITE)

        pygame.display.flip()

        key = wait_for_key()
        if key == 'enter':
            return current_index
        elif key == 'left' and current_index > 0:
            current_index -= 1
            option_change_sound()
        elif key == 'right' and current_index < len(options)-1:
            current_index += 1
            option_change_sound()
    
def option_accept_challenge_2(screen, options, y_offset = 30, num = 888):

    if num == 888:
        name = "Co-op"
    elif num == 999:
        name = "개별 연구"
    else:
        name = "특별 이벤트"

    current_index = 0
    while True:

        display_status(screen)
        screen.blit(SPEC_TEXT, (sX+11, sY+536 - 300))
        draw_text(screen, f"{name}! 마구마구 때려라!", sX+8 + 300, sY+536 - 300 + 30, ORANGE, size = 32, align='center')
        draw_wrapped_text(screen, f"수락한다면 {name} 몬스터를 상대하게 된다. ", sX+ 20 , sY+536 - 300 + 50 + y_offset, WHITE, max_width= 600, font_size=16)
        draw_wrapped_text(screen, f"{name} 몬스터를 3턴 동안 체력을 10% 이내로 만들면 성공이다. 만약 몬스터가 죽거나 10% 이상의 체력을 가지게 되면 실패하게 된다.", sX+20, sY+536 - 300 + 50 + y_offset * 3, WHITE, max_width= 600, font_size=16)
        draw_wrapped_text(screen, "도전을 성공하게 된다면 체력을 모두 회복한다.", sX+20, sY+536 - 300 + 50 + y_offset * 6, WHITE, max_width= 600, font_size=16)
        draw_wrapped_text(screen, "도전을 수락할까?", sX+20, sY+536 - 300 + 50 + y_offset * 7, YELLOW, max_width= 600, font_size=16)

        for i, option in enumerate(options):
            x_pos = stX + (300 * (i % 2))
            y_pos = stY + int(i / 2) * 64

            prefix = "> " if i == current_index else "  "
            draw_text(screen, f"{prefix}{option}", x_pos, y_pos, WHITE)

        pygame.display.flip()

        key = wait_for_key()
        if key == 'enter':
            return current_index
        elif key == 'left' and current_index > 0:
            current_index -= 1
            option_change_sound()
        elif key == 'right' and current_index < len(options)-1:
            current_index += 1
            option_change_sound()

def molcamp_quiz(screen):
    # 몰입 캠프 퀴즈 로직 구현
    quizes = [
        {'Question': ["x = 5", "x += True", "print(x)"], 'Options': ["1. Error", "2. 5", "3. 6"], 'Answer': 3},
        {'Question': ["print(len([0] * 5 == [0, 0, 0, 0, 0]))"], 'Options': ["1. Error", "2. True", "3. False"], 'Answer': 1},
        {'Question': ["print([1, 2, 3][True])"], 'Options': ["1. 1", "2. 2", "3. 3"], 'Answer': 2}
    ]
    return display_molcamp_quiz(screen, quizes)

def display_quiz_interface(screen, quiz):
    for line in quiz['Question']:
        draw_text(screen, line, stX + 600, stY - 300 + quiz['Question'].index(line) * 40, WHITE, size=48, align='center')

def display_molcamp_quiz(screen, quizes):
    result = 0
    for i, quiz in enumerate(quizes):
        current_index = 0
        while True:
            display_status(screen)
            apply_alpha_overlay(screen, (sX, sY, 2*psX + 4, 2*psY - 221))
            draw_text(screen, f"  {i+1}번 문제: 다음 출력값의 결과는?", stX, stY, YELLOW)

            display_quiz_interface(screen, quiz)

            for option in quiz['Options']:
                x_pos = stX + quiz['Options'].index(option) * 200
                y_pos = stY + 50

                prefix = "> " if quiz['Options'].index(option) == current_index else "  "
                draw_text(screen, f"{prefix}{option}", x_pos, y_pos, WHITE)

            pygame.display.flip()
            key = wait_for_key()
            if key == 'enter':
                option_select_sound()
                break
            elif key == 'left' and current_index > 0:
                current_index -= 1
                option_change_sound()
            elif key == 'right' and current_index < len(quiz["Options"])-1:
                current_index += 1
                option_change_sound()
        
        display_status(screen)
        apply_alpha_overlay(screen, (sX, sY, 2*psX + 4, 2*psY - 221))
        display_quiz_interface(screen, quiz)
        draw_text(screen, f"  {quiz['Options'][current_index]}를 선택했다.", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()

        display_status(screen)
        apply_alpha_overlay(screen, (sX, sY, 2*psX + 4, 2*psY - 221))
        display_quiz_interface(screen, quiz)
        draw_text(screen, f"  {quiz['Options'][quiz['Answer']-1]}가 정답이였다!", stX, stY, YELLOW)
        pygame.display.flip()
        wait_for_key()

        # 정답
        if quiz['Options'][current_index] == quiz['Options'][quiz['Answer']-1]:

            result += 1

            display_status(screen)
            draw_text(screen, f"  맞았다!", stX, stY, YELLOW)
            pygame.display.flip()
            wait_for_key()

            player.level += 1
            display_status(screen)
            draw_text(screen, f"  레벨이 1 올랐다!", stX, stY, YELLOW)
            pygame.display.flip()

            display_status(screen) 
            Level_up()
            wait_for_key()


        else:
            display_status(screen)
            draw_text(screen, f"  틀렸다!", stX, stY, RED)
            pygame.display.flip()
            wait_for_key()

    display_status(screen)
    draw_text(screen, f"  총 {result}문제를 맞췄다!", stX, stY, WHITE)
    pygame.display.flip()
    wait_for_key()

    return result

def draw_health_bar(screen, y, x, current_hp, max_hp):
    """체력바를 현재 체력 기준으로 그림 (애니메이션 루프 없음)"""
    def get_ratio(hp, max_hp):
        if hp <= 0:
            return 0
        ratio = int(hp * HPLEN / max_hp)
        return max(1, ratio) if hp > 0 else 0

    def draw_HP(surface, text, x, y, color, highlight=BLACK):
        fontforHP = pygame.font.Font("../neodgm.ttf", 10)
        font_obj = fontforHP
        text_surface = font_obj.render(text, True, color, highlight)
        surface.blit(text_surface, (x, y))
        return text_surface.get_rect(topleft=(x, y))

    current_ratio = get_ratio(current_hp, max_hp)
    color = hpcolor(current_ratio)
    bar_text = '█' * current_ratio + ' ' * (HPLEN - current_ratio)
    draw_HP(screen, bar_text, x, y+10, color)
    draw_HP(screen, bar_text, x, y+5, color)
    draw_HP(screen, bar_text, x, y+0, color)

    

def battle(getplayer, getenemy, screen=None):
    global player, enemy, enemyCSmon, battle_end, startBattleHp
    player = getplayer
    enemy = getenemy
    battle_end = False
    startBattleHp = player.nowhp
    
    player.is_defeated = False
    if hasattr(enemy, 'is_defeated'):
        enemy.is_defeated = False
    if hasattr(enemyCSmon, 'is_defeated'):
        enemyCSmon.is_defeated = False
    
    if logger.isEnabledFor(logging.INFO):
        enemy_name = getattr(enemyCSmon if isinstance(enemy, Monster) else (enemy.nowCSmon if hasattr(enemy, 'nowCSmon') else enemy), 'name', '알 수 없는 적')
        logger.info(f"전투 시작: {player.name} vs {enemy_name}")
    
    # 적이 Monster 객체인 경우
    if isinstance(enemy, Monster):
        enemyCSmon = enemy
    else:
        enemyCSmon = enemy.nowCSmon if hasattr(enemy, 'nowCSmon') else enemy
    
    player.update()
    enemyCSmon.update()
    
    setattr(player, 'defensive_stance', None)
    setattr(enemyCSmon, 'defensive_stance', None)

    # 적 초기화
    if not hasattr(enemyCSmon, 'nowhp'):
        enemyCSmon.nowhp = getattr(enemyCSmon, 'HP', 100)
    
    if screen is None:
        import game_menu
        screen = game_menu.screen
        
    def battle_logic(screen):
        global hap_num, battle_end, item_num
        hap_num = 1
        item_num = 0

        # 특수몹이 아닌 경우에만 등장 메시지 출력
        if not enemyCSmon.special:
            display_status(screen, detail=True)
            draw_text(screen, f"  앗! 야생의 {enemyCSmon.name}이/가 나타났다!", stX, stY, WHITE)
            pygame.display.flip()
            wait_for_key()

        if player.current_semester == "새터":
            display_status(screen, detail=True)
            draw_text(screen, f"* 스킬을 사용해 적을 쓰러뜨리자!", stX, stY, WHITE)
            pygame.display.flip()
            wait_for_key()
        if player.current_semester ==  "1-1":
            display_status(screen, detail=True)
            draw_text(screen, f"* 스킬과 아이템을 적절히 활용해 휼륭한 성적으로 졸업해보자!", stX, stY, WHITE)
            pygame.display.flip()
            wait_for_key()

        if enemyCSmon.special:
            display_status(screen, detail=True)
            draw_text(screen, f"  어라, 야생의 {enemyCSmon.name}이/가 나타났다!", stX, stY, WHITE)
            pygame.display.flip()
            wait_for_key()

            y_offset = 30

            if enemyCSmon.Num == 777:     # 몰캠
                # print("Debug: 몰캠 전투 시작")
                current_index = option_accept_challenge_molcamp(screen, options=["수락한다", "거절한다"], y_offset=y_offset)
                do_event = False

                # 거절
                if current_index == 1:
                    do_event = False
                    display_status(screen, detail=True)
                    draw_text(screen, f"  몰입 캠프를 거절한다...", stX, stY, WHITE)
                    player.molcam = False
                    pygame.display.flip()
                    wait_for_key()

                # 수락
                elif current_index == 0:
                    do_event = True
                    display_status(screen, detail=True)
                    draw_text(screen, f"  몰입 캠프에 도전한다!", stX, stY, WHITE)
                    pygame.display.flip()
                    wait_for_key()

            elif enemyCSmon.Num == 888 or enemyCSmon.Num == 999:   # 코옵 or 개별연구

                current_index = option_accept_challenge_2(screen, options=["수락한다", "거절한다"], y_offset=y_offset, num = enemyCSmon.Num)
                do_event = False

                # 거절
                if current_index == 1:
                    do_event = False
                    display_status(screen, detail=True)
                    draw_text(screen, f"  {enemyCSmon.name}를 거절한다...", stX, stY, WHITE)
                    # player.molcam = False
                    pygame.display.flip()
                    wait_for_key()

                # 수락
                elif current_index == 0:
                    do_event = True
                    display_status(screen, detail=True)
                    draw_text(screen, f"  {enemyCSmon.name}에 도전한다!", stX, stY, WHITE)
                    pygame.display.flip()
                    wait_for_key()


                    display_status(screen, detail=True)
                    turn = 0

                    while turn < 3 and enemyCSmon.nowhp > 0 and player.is_alive():
                        display_status(screen, detail=True)
                        draw_text(screen, f"  {turn+1}번째 행동을 선택하자!", stX, stY, WHITE)
                        pygame.display.flip()
                        wait_for_key()

                        display_status(screen, detail=True)
                        action = select_action(screen)
                        if action not in [0, 1]:
                            display_status(screen, detail=True)
                            draw_text(screen, f"  스킬 또는 아이템을 사용해야 한다!", stX, stY, WHITE)
                            pygame.display.flip()
                            wait_for_key()
                            continue

                        if action == 0: # 스킬 사용
                            esc = skill_phase(screen)
                            if esc == -1:
                                pass
                            else:
                                turn += 1
                            
                        elif action == 1: # 아이템 사용
                            if not any(i.name != "빈 슬롯" for i in player.items):
                                display_status(screen, detail=True)
                                draw_text(screen, f"  아이템이 없다!", stX, stY, WHITE)
                                pygame.display.flip()
                                wait_for_key()
                            else:
                                esc = item_phase(screen)
                                if esc == -1:
                                    pass
                                else: 
                                    turn += 1
                        # 적 체력 확인
                        enemy_hp = getattr(enemyCSmon, 'nowhp', getattr(enemyCSmon, 'HP', 100))
                        if enemy_hp <= 0:
                            display_status(screen, detail=True)
                            draw_text(screen, f"  {enemyCSmon.name}이/가 쓰러졌다!", stX, stY, WHITE)
                            pygame.display.flip()
                            wait_for_key()
                            
                            battle_end = True
                            return "실패"
                        
                    # 3턴 종료 후 체력 체크
                    enemy_hp = getattr(enemyCSmon, 'nowhp', getattr(enemyCSmon, 'HP', 100))
                    if enemy_hp <= 0:
                        display_status(screen, detail=True)
                        draw_text(screen, f"  {enemyCSmon.name}이/가 쓰러졌다!", stX, stY, WHITE)
                        pygame.display.flip()
                        wait_for_key()

                        battle_end = True
                        return "실패"
                    elif enemy_hp <= int(enemyCSmon.HP * 0.1):
                        display_status(screen, detail=True)
                        draw_text(screen, f"  {enemyCSmon.name}의 체력이 충분히 낮아졌다!", stX, stY, WHITE)
                        pygame.display.flip()
                        wait_for_key()
                        player.event_success = True

                        battle_end = True
                        return "성공"
                    else:
                        display_status(screen, detail=True)
                        draw_text(screen, f"  {enemyCSmon.name}의 체력이 충분히 낮아지지 않았다...", stX, stY, WHITE)
                        pygame.display.flip()
                        wait_for_key()

                        battle_end = True
                        return "실패"
                           
        while not battle_end:
            if enemyCSmon.Num == 777:     # 몰캠
                if do_event:
                    lup_amt = molcamp_quiz(screen)
                    strl = "레벨업" + " +" + str(lup_amt)
                    print(strl)
                    madcamp.reward = strl
                    player.molcam = lup_amt
                    return "승리"

                else:
                    return "드랍"

            if enemyCSmon.Num == 888 or enemyCSmon.Num == 999:   # 코옵 or 개별연구
                if do_event:
                    return "승리"
                else:
                    return "드랍"
                
            else:
                # 플레이어 턴
                if hpcolor(get_ratio(player.nowhp, player.HP)) == RED:
                    HP_low()
                action = select_action(screen)
                
                if action == -999:  # 디버그 스킵
                    # 스킵으로 즉시 승리 처리
                    Battle_win()
                    display_status(screen, detail=True)
                    draw_text(screen, f"  [DEBUG] 전투를 스킵했습니다!", stX, stY, YELLOW)
                    pygame.display.flip()
                    wait_for_key()
                    battle_end = True
                    return "승리"
                elif action == 0:  # 스킬 사용
                    esc = skill_phase(screen)
                    if esc == -1:
                        continue
                elif action == 1:  # 아이템 사용
                    if not any(i.name != "빈 슬롯" for i in player.items):
                        display_status(screen, detail=True)
                        draw_text(screen, f"  아이템이 없다!", stX, stY, WHITE)
                        pygame.display.flip()
                        wait_for_key()
                        continue
                    else:
                        esc = item_phase(screen)
                        if esc == -1:
                            continue
                elif action == 2:  # 드랍
                    display_status(screen, detail=True)
                    draw_text(screen, f"  과목을 드랍했다!", stX, stY, WHITE)
                    pygame.display.flip()
                    wait_for_key()
                    return "드랍"
                elif action == 3 and player.can_use_pnr():  # PNR 사용
                    player.pnr_used = True
                
                    
                    # 몬스터의 현재 HP와 최대 HP를 가져옵니다.
                    enemy_current_hp = getattr(enemyCSmon, 'nowhp', getattr(enemyCSmon, 'HP', 100))
                    enemy_max_hp = getattr(enemyCSmon, 'HP', 100)

                    # 몬스터의 남은 체력 비율을 계산합니다.
                    hp_ratio = enemy_current_hp / enemy_max_hp
                    
                    # PNR 성공률의 최대 변동 폭을 계산합니다. (최대 확률 95%로 고정)
                    pnr_variable_rate = 0.95 - BASIC_PNR_SUCCESS_RATE
                    
                    # 최종 PNR 성공 확률을 계산합니다.
                    pnr_success_rate = BASIC_PNR_SUCCESS_RATE + (1 - hp_ratio) * pnr_variable_rate
                    
                    # 확률을 적용하여 PNR 성공 여부를 결정합니다.
                    success = "P" if random.random() < pnr_success_rate else "NR"
                    show_pnr_result(screen, success)
                    
                    if success == "P":
                        return "PNR_P"
                    else:
                        return "PNR_NR"
                
                # 적 체력 확인
                enemy_hp = getattr(enemyCSmon, 'nowhp', getattr(enemyCSmon, 'HP', 100))
                if enemy_hp <= 0:
                    enemyCSmon.is_defeated = True # 1. 쓰러짐 상태로 변경
                    play_death_animation('monster', screen) # 2. 애니메이션 재생
                    
                    # 3. 이제 display_status가 알아서 실루엣을 그려줌
                    display_status(screen, detail=True)
                    draw_text(screen, f"  {enemyCSmon.name}이/가 쓰러졌다!", stX, stY, WHITE)
                    pygame.display.flip()
                    wait_for_key()
                    
                    battle_end = True
                    return "승리"
                
                # 수정된 부분: 플레이어 체력 확인
                if not player.is_alive():
                    player.is_defeated = True # 1. 쓰러짐 상태로 변경
                    play_death_animation('player', screen) # 2. 애니메이션 재생
                    
                    # 3. 이제 display_status가 알아서 실루엣을 그려줌
                    display_status(screen, detail=True)
                    draw_text(screen, f"  {player.name}이/가 쓰러졌다!", stX, stY, WHITE)
                    pygame.display.flip()
                    wait_for_key()

                    battle_end = True
                    return "패배"
                setattr(player, 'defensive_stance', None)
                setattr(enemyCSmon, 'defensive_stance', None)
                
                hap_num += 1
    
    # 전투 시작
    result = battle_logic(screen)
    
    if result == "승리":
        Battle_win()
        display_status(screen)

        if enemyCSmon.Num == 777:     # 몰캠
            draw_text(screen, f"  몰캠을 수료했다!", stX, stY, WHITE)
        elif enemyCSmon.Num == 888 or enemyCSmon.Num == 999:
            draw_text(screen, f"  {enemyCSmon.name} 도전에 성공했다!", stX, stY, WHITE) 


            display_status(screen)
            healAnimation()
            animate_health_bar(screen, psY+121, psX+122, player.nowhp, player.HP, player.HP)
            draw_text(screen, f"  {player.name}의 체력이 전부 회복되었다!", stX, stY, GREEN)
            pygame.display.flip()
            wait_for_key()


        else:
            draw_text(screen, f"  승리했다!", stX, stY, WHITE)
    
        pygame.display.flip()
        wait_for_key()
        gpa = gpaCalculator(enemyCSmon, hap_num, item_num)

        if player.nowhp != player.HP:
            heal_amount = max(1, int(player.HP * 0.20))
            healAnimation()
            playerCurrentHP = player.nowhp
            player.heal(heal_amount)
            display_status(screen)
            animate_health_bar(screen, psY+121, psX+122, playerCurrentHP, player.nowhp, player.HP)
            draw_text(screen, f"  {player.name}의 체력이 회복되었다!", stX, stY, GREEN)
            pygame.display.flip()
            wait_for_key()

        reward_items = get_random_reward_items(3)
        selected_item = select_reward_item(screen, reward_items)
        
        if selected_item is None: 
            option_escape_sound()
            display_status(screen)
            draw_text(screen, "  아이템을 선택하지 않았다!", stX, stY, YELLOW)
        else:
            for idx, item in enumerate(player.items):
                if item.name == "빈 슬롯":
                    player.items[idx] = copy.deepcopy(selected_item)
                    break
            else:
                while True:
                    display_status(screen)
                    draw_text(screen, "  인벤토리가 가득 찼다! 버릴 아이템을 선택하자.", stX, stY, YELLOW)
                    pygame.display.flip()
                    wait_for_key()
                    option_change_sound()
                    discard_idx = select_item(screen)
                    if discard_idx == -1:
                        selected_item = select_reward_item(screen, reward_items)
                        if selected_item is None:
                            option_escape_sound()
                            display_status(screen)
                            draw_text(screen, "  아이템을 선택하지 않았다!", stX, stY, YELLOW)
                            break
                        continue
                    player.items[discard_idx] = copy.deepcopy(selected_item)
                    break
            
            if selected_item is not None:    
                display_status(screen)
                draw_text(screen, f"  {selected_item.name}을/를 획득했다!", stX, stY, GREEN)

        pygame.display.flip()
        wait_for_key()

        if enemy.type[0] == "EVENT":
            return 4, (0, "성공!")
        if enemy.name in player.clearedMonsters:
            if gpa[1] == "A+" or gpa[1] == "A0":
                gpa = (enemy.credit, "A-") 
            return 1, gpa
        return 1, gpa
    
    elif result == "패배":
        Lose()
        display_status(screen)
        draw_text(screen, f"  패배했다...", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()
        if enemy.type[0] == "EVENT":
            return 4, (0, "실패...")
        return 0, (enemy.credit, "F")
    
    elif result == "드랍":
        Lose()
        display_status(screen)
        draw_text(screen, f"  과목을 드랍했다!", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()
        if enemy.type[0] == "EVENT":
            return 4, (0, "실패...")
        return 3, (0, "W")

    # PNR 결과 처리
    elif result == "PNR_P":
        Battle_win()
        display_status(screen)
        draw_text(screen, f"  PNR로 과목을 패스했다!", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()
        
        # 아이템 보상 로직은 그대로 유지
        healAnimation()
        heal_amount = max(1, int(player.HP * 0.05))
        playerCurrentHP = player.nowhp
        player.heal(heal_amount)
        display_status(screen)
        animate_health_bar(screen, psY+121, psX+122, playerCurrentHP, player.nowhp, player.HP)
        draw_text(screen, f"  {player.name}의 체력이 회복되었다!", stX, stY, GREEN)
        pygame.display.flip()
        wait_for_key()
        
        pnr_reward_items_pool = [i for i in item_list if i.grade == "노말"]
        if pnr_reward_items_pool:
            reward_items = random.sample(pnr_reward_items_pool, min(3, len(pnr_reward_items_pool)))
            selected_item = select_reward_item(screen, reward_items)
        else:
            selected_item = None
        
        if selected_item is None: 
            option_escape_sound()
            display_status(screen)
            draw_text(screen, "  아이템을 선택하지 않았다!", stX, stY, YELLOW)
        else:
            for idx, item in enumerate(player.items):
                if item.name == "빈 슬롯":
                    player.items[idx] = copy.deepcopy(selected_item)
                    break
            else:
                while True:
                    display_status(screen)
                    draw_text(screen, "  인벤토리가 가득 찼다! 버릴 아이템을 선택하자.", stX, stY, YELLOW)
                    pygame.display.flip()
                    wait_for_key()
                    option_change_sound()
                    discard_idx = select_item(screen)
                    if discard_idx == -1:
                        selected_item = select_reward_item(screen, reward_items)
                        if selected_item is None:
                            option_escape_sound()
                            display_status(screen)
                            draw_text(screen, "  아이템을 선택하지 않았다!", stX, stY, YELLOW)
                            break
                        continue
                    player.items[discard_idx] = copy.deepcopy(selected_item)
                    break
            if selected_item is not None:    
                display_status(screen)
                draw_text(screen, f"  {selected_item.name}을/를 획득했다!", stX, stY, GREEN)

        pygame.display.flip()
        wait_for_key()
        
        return 2, (0, "P") # PNR 성공은 2를 반환
        
    elif result == "PNR_NR":
        Lose()
        display_status(screen)
        draw_text(screen, f"  NR이 떠 버리고 말았다...", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()
        
        return 5, (0, "NR") # PNR 실패는 5를 반환

    elif result == "실패":
        Lose()
        display_status(screen)
        draw_text(screen, f" 특별 미션에 실패했다...", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()
        if enemy.type[0] == "EVENT":
            return 4, (0, "실패...")
    elif result == "성공":
        Battle_win()
        display_status(screen)
        draw_text(screen, f" 특별 미션에 성공했다!", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()
        if enemy.type[0] == "EVENT":
            return 4, (0, "성공!")
    
        
    else: return 0, (enemy.credit, "F")