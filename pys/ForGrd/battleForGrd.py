from game_menu import *
from ForGrd.playerForGrd import *
from ForGrd.itemForGrd import get_item_color_by_grade

''' 전역변수 설정 '''
hap_num = 0
item_num = 0
player = None
enemy = None
enemyCSmon = None
battle_end = False
startBattleHp = 0

# 아이템 보상 확률 차등 설정
ITEM_DROP_RATES = {
    "레전더리": 0.05,  # 05%
    "에픽": 0.15,     # 15%
    "레어": 0.30,     # 30%
    "노말": 0.50,     # 50%
}

# 기존 좌표 및 이미지 로드는 그대로 유지
sX, sY = 32, 32
stX = sX+20
stY = sY+568
esX, esY = sX+20, sY+36
psX, psY = sX+582, sY+347

# 기존 이미지들 그대로 유지
BACKGROUND = pygame.image.load("../img/background.png")
STAT = pygame.image.load("../img/stat.png")
TEXT = pygame.image.load("../img/text.png")
CST = pygame.image.load("../img/CST.png")
DTS = pygame.image.load("../img/DTS.png")
AI = pygame.image.load("../img/AI.png")
PS = pygame.image.load("../img/PS.png")
SYS = pygame.image.load("../img/SYS.png")
EVENT = pygame.image.load("../img/EVENT.png")
STAR = pygame.image.load("../img/STAR.png")
ME = pygame.image.load("../img/monsters/ME.png")
ME = pygame.transform.scale_by(ME, 10)
ATK = pygame.image.load("../img/ATK.png")
SPATK = pygame.image.load("../img/SP.ATK.png")
ETC = pygame.image.load("../img/ETC.png")

# 기존 함수들 그대로 유지
def display_type(screen, y, x, type):
    """타입 표시 (pygame)"""
    if type == "CT":
        screen.blit(CST, (x, y))
    elif type == "DS":
        screen.blit(DTS, (x, y))
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

def hpcolor(ratio):
    """체력 상태에 따른 색상 선택"""
    if ratio >= 14:
        color_pair = GREEN
    elif ratio >= 7:
        color_pair = YELLOW
    else:
        color_pair = RED
    return color_pair

def animate_health_bar(screen, y, x, current_hp, target_hp, max_hp):
    """체력바를 부드럽게 애니메이션으로 업데이트 (pygame)"""
    current_ratio = int(current_hp * 31 / max_hp)
    target_ratio = int(target_hp * 31 / max_hp)
    steps = abs(current_ratio-target_ratio)

    def draw_HP(surface, text, x, y, color, highlight=BLACK):
        fontforHP = pygame.font.Font("../neodgm.ttf", 20)
        font_obj = fontforHP
        text_surface = font_obj.render(text, True, color, highlight)
        surface.blit(text_surface, (x, y))
        return text_surface.get_rect(topleft=(x, y))

    if steps == 0:
        draw_HP(screen, f"{'█' * current_ratio}{' ' * (31 - current_ratio)}", x, y, hpcolor(current_ratio))
        return

    # 애니메이션 단계별로 체력바 업데이트
    elif (current_hp-target_hp)/max_hp > 0.5:
        Damage_strong()
    elif (current_hp-target_hp)/max_hp > 0:
        Damage_weak()
    else: 
        Heal()
    for step in range(steps + 1):
        interpolated_ratio = current_ratio + int((target_ratio - current_ratio) * step / steps)
        draw_HP(screen, f"{'█' * interpolated_ratio}{' ' * (31 - interpolated_ratio)}", x, y, hpcolor(interpolated_ratio))
        pygame.display.flip()
        time.sleep(0.05)

def display_status(screen, detail=False):
    """상태 화면 표시 - 플레이어 직접 전투용으로 수정"""
    screen.fill((113,113,113))
    screen.blit(BACKGROUND, (sX, sY))

    # 배틀 정보 출력
    draw_text(screen, f"플레이어: {player.name}", sX, sY+820, VIOLET)
    draw_text(screen, f"현재 학기: {player.current_semester}", sX, sY+860, BLUE)
    draw_text(screen, f"턴 {hap_num}", sX, sY+900, CYAN)
    gpa = gpaCalculator(enemyCSmon, hap_num, item_num)[1]
    draw_text(screen, f"현재 성적: ", sX, sY+940, GREEN)
    draw_text(screen, f"{gpa}", sX+200, sY+940, gpaColor(gpa))
    
    # 적 상태 (상단)
    screen.blit(STAT, (esX, esY))
    if hasattr(enemyCSmon, 'image'):
        image = pygame.image.load(enemyCSmon.image)
        image = pygame.transform.scale_by(image, 10)
        screen.blit(image, (esX+860-image.get_width()//2, esY+310-image.get_height()))
    
    draw_text(screen, f"{enemyCSmon.name}", esX+64, esY+52, WHITE)
    draw_text(screen, f"lv.{getattr(enemyCSmon, 'level', 1)}", esX+384, esY+52, WHITE)
    
    enemy_hp = getattr(enemyCSmon, 'nowhp', getattr(enemyCSmon, 'HP', 100))
    enemy_max_hp = getattr(enemyCSmon, 'HP', 100)
    animate_health_bar(screen, esY+104, esX+135, enemy_hp, enemy_hp, enemy_max_hp)

    # 적 타입 표시
    enemy_types = getattr(enemyCSmon, 'type', ['전산이론'])
    if isinstance(enemy_types, str):
        enemy_types = [enemy_types]
    for i, enemy_type in enumerate(enemy_types[:2]):  # 최대 2개만 표시
        display_type(screen, esY, esX+470+i*124, enemy_type)
    
    if player.cheatmode:
        # 상대 능력치 표시 (치트모드)
        draw_text(screen, f"{getattr(enemyCSmon, 'nowhp', getattr(enemyCSmon, 'HP', 100))}/{getattr(enemyCSmon, 'HP', 100)}", esX+445, esY+100, WHITE, highlight=VIOLET)
        draw_text(screen, f"ATK {getattr(enemyCSmon, 'CATK', 10)}/{getattr(enemyCSmon, 'ATK', 10)}", esX+610, esY+16, WHITE, highlight=RED)
        draw_text(screen, f"DEF {getattr(enemyCSmon, 'CDEF', 10)}/{getattr(enemyCSmon, 'DEF', 10)}", esX+610, esY+56, WHITE, highlight=RED)
        draw_text(screen, f"SPD {getattr(enemyCSmon, 'CSPD', 10)}/{getattr(enemyCSmon, 'SPD', 10)}", esX+610, esY+96, WHITE, highlight=RED)
       
    
    # 플레이어 상태 (하단) - 직접 전투
    screen.blit(STAT, (psX, psY))
    screen.blit(ME, (sX+320-ME.get_width()//2, sY+536-ME.get_height()))
    
    draw_text(screen, f"{player.name}", psX+64, psY+52, WHITE)
    draw_text(screen, f"lv.{player.level}", psX+384, psY+52, WHITE)

    # 플레이어 타입 표시
    player_type = player.playertype()
    display_type(screen, psY, psX+470, player_type)
    
    # 플레이어 체력바
    player_hp = getattr(player, 'nowhp', getattr(player, 'HP', 100))
    player_max_hp = getattr(player, 'HP', 100)
    animate_health_bar(screen, psY+104, psX+135, player_hp, player_hp, player_max_hp)

    if detail:
        display_player_details(screen, player, sX+1264)

    screen.blit(TEXT, (sX+8, sY+536))

def display_player_details(screen, player, x):
    """플레이어 상세 정보 출력"""
    details = [
        (("이름", 0, WHITE), (f"{player.name}", 228, CYAN)),
        (("레벨", 0, WHITE), (f"{player.level}", 228, CYAN)),
        (("다음 레벨까지", 0, WHITE), (f"{player.max_exp - player.exp}", 228, BLUE), ("경험치 남음", 352, WHITE)),
        "",
        (("체력", 0, WHITE), (f"{player.nowhp}"+"/"+f"{player.HP}", 228, CYAN)),
        (("공격", 0, WHITE), (f"{player.ATK}", 228, CYAN)),
        (("방어", 0, WHITE), (f"{player.DEF}", 228, CYAN)),
        (("속도", 0, WHITE), (f"{player.SPD}", 228, CYAN)),
        "",
        (("현재 학기", 0, WHITE), (f"{player.current_semester}", 228, WHITE)),
        "",
        (("스킬 별 레벨", 0, WHITE), ("", 0, WHITE)),
        (("  *   ", 0 , STARC), (f"Level {player.learned_skills['*']}", 228, GRAY if player.learned_skills["*"] == 0 else WHITE if player.learned_skills["*"] < 2 else YELLOW if player.learned_skills["*"] < 4 else ORANGE if player.learned_skills["*"] < 5 else RED)),
        (("  CT  ", 0 , CTC), (f"Level {player.learned_skills['CT']}", 228, GRAY if player.learned_skills["CT"] == 0 else WHITE if player.learned_skills["CT"] < 2 else YELLOW if player.learned_skills["CT"] < 4 else ORANGE if player.learned_skills["CT"] < 5 else RED)),
        (("  DS  ", 0 , DSC), (f"Level {player.learned_skills['DS']}", 228, GRAY if player.learned_skills["DS"] == 0 else WHITE if player.learned_skills["DS"] < 2 else YELLOW if player.learned_skills["DS"] < 4 else ORANGE if player.learned_skills["DS"] < 5 else RED)),
        (("  PS  ", 0 , PSC), (f"Level {player.learned_skills['PS']}", 228, GRAY if player.learned_skills["PS"] == 0 else WHITE if player.learned_skills["PS"] < 2 else YELLOW if player.learned_skills["PS"] < 4 else ORANGE if player.learned_skills["PS"] < 5 else RED)),
        (("  SYS ", 0 , SYSC), (f"Level {player.learned_skills['SYS']}", 228, GRAY if player.learned_skills["SYS"] == 0 else WHITE if player.learned_skills["SYS"] < 2 else YELLOW if player.learned_skills["SYS"] < 4 else ORANGE if player.learned_skills["SYS"] < 5 else RED)),
        (("  AI  ", 0 , AIC), (f"Level {player.learned_skills['AI']}", 228, GRAY if player.learned_skills["AI"] == 0 else WHITE if player.learned_skills["AI"] < 2 else YELLOW if player.learned_skills["AI"] < 4 else ORANGE if player.learned_skills["AI"] < 5 else RED)),
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
    
    # PNR 버튼 추가 (조건부)
    if player.can_use_pnr():
        options.append("PNR 사용")
    
    current_index = 0
    
    while True:
        display_status(screen, detail=True)
        
        for i, option in enumerate(options):
            x_pos = stX + (300 * (i % 2))
            y_pos = stY + int(i / 2) * 56
            
            # PNR 버튼은 파란색으로 표시
            color = BLUE if option == "PNR 사용" else WHITE
            
            prefix = "> " if i == current_index else "  "
            draw_text(screen, f"{prefix}{option}", x_pos, y_pos, color)
        
        pygame.display.flip()
        
        key = wait_for_key()
        if key == 'enter':
            return current_index
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
            y_pos = stY + int(i / 2) * 61 - 5
            effectiveness = Comp(skill, enemyCSmon)
            
            # 스킬 표시
            prefix = "> " if i == current_index else "  "
            prefix_color = WHITE if i == current_index else GRAY  # 원하는 색상 지정
            draw_text(screen, prefix, x_pos, y_pos, prefix_color)
            draw_text(screen, skill['name'], x_pos + 30, y_pos, get_color_by_effectiveness(effectiveness))
            # draw_text(screen, skill['name'], x_pos + 30, y_pos, get_color_by_effectiveness(effectiveness), highlight= typecolor_dict[skill['type']])

            # 효과 표시
            if get_color_by_effectiveness(effectiveness) == RED:
                draw_text(screen, "효과가 굉장함", x_pos + 30, y_pos + 35, RED, size=16)
            elif get_color_by_effectiveness(effectiveness) == GRAY:
                draw_text(screen, "효과 없음", x_pos + 30, y_pos + 35, GRAY, size=16)
            elif get_color_by_effectiveness(effectiveness) == LIGHTGRAY:
                draw_text(screen, "효과가 별로임", x_pos + 30, y_pos + 35, LIGHTGRAY, size=16)
            else:
                draw_text(screen, "효과 있음", x_pos + 30, y_pos + 35, WHITE, size=16)

            if i == current_index:
                # 선택된 스킬 상세정보 표시
                # 선택된 스킬의 상세정보 표시
                infoY = sY+536
                display_type(screen, infoY, sX+600, skill['type'])
                draw_text(screen, "타입", sX+760, infoY+20, WHITE)
                draw_text(screen, f"{type_dict[skill['type']]}", sX+1212, infoY+20, typecolor_dict[skill['type']], align='right')
                
                draw_text(screen, "위력", sX+760, infoY+60, WHITE)
                draw_text(screen,f"{skill['damage']}", sX+1212, infoY+60, WHITE, align='right')
                draw_wrapped_text(
                    screen,
                    skill['description'],
                    sX+760,
                    infoY + 100,
                    WHITE,
                    font_size=16,
                    max_width= 452 # 원하는 최대 너비 지정
                )
        pygame.display.flip()
        
        key = wait_for_key()
        if key == 'enter':
            selected_skill = available_skills[current_index]
            return selected_skill
        elif key == 'escape':
            option_escape_sound()
            return -1
        elif len(available_skills) == 1:
            current_index = 0
        elif key == 'up' and (current_index > 1 and current_index < len(available_skills)):
            current_index -= 2
            option_change_sound()
        elif key == 'down' and (current_index >= 0 and current_index < len(available_skills)-2):
            current_index += 2
            option_change_sound()
        elif key == 'left' and (current_index % 2 == 1 and current_index < len(available_skills) and current_index >= 0):
            current_index -= 1
            option_change_sound()
        elif key == 'right' and (current_index % 2 == 0 and current_index < len(available_skills) and current_index >= 0 and current_index != len(available_skills)-1):
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

def gpaCalculator(enemy, hap_num, item_num, first_time=True):
    score = max(0, (17-hap_num)/16) * 0.3 + max(0, (3-item_num)/3) * 0.3 + (1-(startBattleHp-player.nowhp)/player.HP)*0.4
    if score >= 0.90: gpa = "A+" if first_time else "A-"
    elif score >= 0.80: gpa = "A0" if first_time else "A-"
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
    # 적 스킬 선택 (랜덤)
    enemy_skills = getattr(enemyCSmon, 'skills', {})
    if enemy_skills:
        enemy_skill = random.choice(list(enemy_skills.values()))
    if selected_skill["priority"] > enemy_skill.priority or (selected_skill["priority"] == enemy_skill.priority and player.CSPD >= enemyCSmon.CSPD):
        stop = player_skill_phase(screen, selected_skill, enemy_skill)
        if enemyCSmon.is_alive() and not stop:
            enemy_attack_phase(screen, selected_skill, enemy_skill)
    else:
        stop = enemy_attack_phase(screen, selected_skill, enemy_skill)
        if player.is_alive() and not stop:
            player_skill_phase(screen, selected_skill, enemy_skill)

def player_skill_phase(screen, selected_skill, enemy_skill):
    enemyCurrentHP = getattr(enemyCSmon, 'nowhp', getattr(enemyCSmon, 'HP', 100))
    # 스킬 사용 메시지
    display_status(screen, True)
    draw_text(screen, f"  {player.name}의 {selected_skill['name']}!", stX, stY, WHITE)
    pygame.display.flip()
    wait_for_key()

    # 스킬 효과 적용
    result, message = player.use_skill(selected_skill["name"], enemyCSmon)
    
    # 체력바 애니메이션
    enemy_hp_after = getattr(enemyCSmon, 'nowhp', getattr(enemyCSmon, 'HP', 100))
    animate_health_bar(screen, esY+104, esX+135, enemyCurrentHP, enemy_hp_after, getattr(enemyCSmon, 'HP', 100))
    # [추가] 반사 처리: 적이 반사 준비 상태였다면 플레이어에게 반사 피해
    if getattr(enemyCSmon, "hpShield", False) and getattr(enemyCSmon, "reflect_ratio", 0.0) > 0.0:
        reflect = int(result.get("damage", 0) * enemyCSmon.reflect_ratio)
        if reflect > 0:
            player_prev = player.nowhp
            player.nowhp = max(0, player.nowhp - reflect)
            # 1회성 해제
            enemyCSmon.hpShield = False
            # 반사 애니메이션 & 메시지
            animate_health_bar(screen, psY+104, psX+135, player_prev, player.nowhp, getattr(player, 'HP', 100))
            display_status(screen, True)
            draw_text(screen, f"  {enemyCSmon.name}의 반사! {player.name}에게 {reflect} 피해를 돌려주었다!", stX, stY, WHITE)
            pygame.display.flip()
            wait_for_key()
    
    # 결과 메시지
    display_status(screen, True)
    if result:
        kind = result.get("kind", "damage")
        damage = result.get("damage", 0)
        effectiveness = result.get("effectiveness", 1.0)
        msg = result.get("message")

        # 1) use_skill이 만든 문장 먼저 표시
        if msg:
            draw_text(screen, f"  {msg}", stX, stY, WHITE)
            pygame.display.flip()
            wait_for_key()
            display_status(screen, True)

        # 2) 종류별 보조 출력
        if kind == "damage":
            draw_text(screen, f"  {enemyCSmon.name}는 {damage}의 피해를 입었다!", stX, stY, WHITE)
            pygame.display.flip()
            wait_for_key()
            display_status(screen, True)

            if effectiveness > 1.5:
                draw_text(screen, "  효과가 뛰어났다!", stX, stY, WHITE)
                pygame.display.flip()
                wait_for_key()
                display_status(screen, True)
            elif effectiveness < 0.8:
                draw_text(screen, "  효과가 별로인 듯 하다...", stX, stY, WHITE)
                pygame.display.flip()
                wait_for_key()
                display_status(screen, True)

        elif kind == "heal":
            healed = result.get("healed", 0)
            # msg가 이미 뜨지만, 여분 안내를 추가하고 싶으면:
            # draw_text(screen, f"  {player.name}의 체력이 {healed} 회복되었다!", stX, stY, WHITE)
            # pygame.display.flip(); wait_for_key()

        elif kind == "buff":
            # 버프 수치 표시를 추가하고 싶다면:
            Vatk = result.get("Vatk"); Vdef = result.get("Vdef"); Vspd = result.get("Vspd")
            # draw_text(screen, f"  능력치 변경 ATK×{Vatk} DEF×{Vdef} SPD×{Vspd}", stX, stY, WHITE)
            # pygame.display.flip(); wait_for_key()

        elif kind == "reflect":
            # 반사 준비 안내는 msg에 이미 포함됨
            pass

        elif kind == "halve_hp":
            # 이미 상대 HP가 줄었고 msg도 표시됨
            pass

        else:
            # noop 등
            pass
    else:
        draw_text(screen, f"  {message}", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()

def enemy_attack_phase(screen, player_skill, skill):
    """적 공격 단계"""
    playerCurrentHP = getattr(player, 'nowhp', getattr(player, 'HP', 100))
    enemyCurrentHP_snap = getattr(enemyCSmon, 'nowhp', getattr(enemyCSmon, 'HP', 100))

    # 스킬 사용
    display_status(screen, True)
    draw_text(screen, f"  {enemyCSmon.name}의 {skill.name}!", stX, stY, WHITE)
    pygame.display.flip()
    wait_for_key()
    
    result, message = enemyCSmon.use_skill(player, skill)
    # kind에 따라 애니메이션 대상 분기
    kind = (result or {}).get("kind", "damage")
    if kind == "damage" or kind == "halve_hp":
        player_hp_after = getattr(player, 'nowhp', getattr(player, 'HP', 100))
        animate_health_bar(screen, psY+104, psX+135, playerCurrentHP, player_hp_after, getattr(player, 'HP', 100))
    elif kind == "heal":
        enemy_hp_after = getattr(enemyCSmon, 'nowhp', getattr(enemyCSmon, 'HP', 100))
        animate_health_bar(screen, esY+104, esX+135, enemyCurrentHP_snap, enemy_hp_after, getattr(enemyCSmon, 'HP', 100))
    else:
        # buff / reflect / noop 등: HP 변화 없음 → 애니메이션 생략
        pass
    
    # [추가] 반사 처리: 플레이어가 반사 준비 상태였다면 적에게 반사 피해
    if getattr(player, "hpShield", False) and getattr(player, "reflect_ratio", 0.0) > 0.0:
        reflect = int(result.get("damage", 0) * player.reflect_ratio)
        if reflect > 0:
            enemy_prev = enemyCSmon.nowhp
            enemyCSmon.nowhp = max(0, enemyCSmon.nowhp - reflect)
            # 1회성 해제
            player.hpShield = False
            # 반사 애니메이션 & 메시지
            animate_health_bar(screen, esY+104, esX+135, enemy_prev, enemyCSmon.nowhp, getattr(enemyCSmon, 'HP', 100))
            display_status(screen, True)
            draw_text(screen, f"  {player.name}의 반사! {enemyCSmon.name}에게 {reflect} 피해를 돌려주었다!", stX, stY, WHITE)
            pygame.display.flip()
            wait_for_key()

    # 결과 메시지
    # ──[ 교체: enemy_attack_phase()의 "결과 메시지" 부분 전체 ]───────────────
    # 결과 메시지
    display_status(screen, True)
    if result:
        kind = result.get("kind", "damage")
        damage = result.get("damage", 0)
        effectiveness = result.get("effectiveness", 1.0)
        msg = result.get("message")

        # 1) 메시지 우선
        if msg:
            draw_text(screen, f"  {msg}", stX, stY, WHITE)
            pygame.display.flip()
            wait_for_key()
            display_status(screen, True)

        # 2) 종류별 보조 출력
        if kind == "damage":
            draw_text(screen, f"  {player.name}은(는) {damage}의 피해를 입었다!", stX, stY, WHITE)
            pygame.display.flip()
            wait_for_key()
            display_status(screen, True)

            if effectiveness > 1.5:
                draw_text(screen, "  효과가 뛰어났다!", stX, stY, WHITE)
                pygame.display.flip()
                wait_for_key()
                display_status(screen, True)
            elif effectiveness < 0.8:
                draw_text(screen, "  효과가 별로인 듯 하다...", stX, stY, WHITE)
                pygame.display.flip()
                wait_for_key()
                display_status(screen, True)

        elif kind == "heal":
            # 힐: msg에 이미 안내 포함
            pass

        elif kind == "buff":
            # 버프: 필요 시 수치 표시
            pass

        elif kind == "reflect":
            # 반사 준비: msg에 포함
            pass

        elif kind == "halve_hp":
            # 이미 플레이어 HP 반감 적용 완료
            pass

        else:
            pass
    else:
        draw_text(screen, f"  {message}", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()

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
            x_pos = stX + i * 210
            y_pos = stY 

            color = coloring[i] if coloring[i] else WHITE
            
            prefix = "> " if i == current_index else "  "
            draw_text(screen, f"{prefix}{item.name}", x_pos, y_pos, color)
            
            if i == current_index:
                draw_wrapped_text(
                    screen,
                    descriptions[i],
                    stX,
                    stY + 60,
                    WHITE,
                    max_width=1100
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
        # elif key == 'up' and (current_index > 1 and current_index < len(player.items)):
        #     current_index -= 2
        #     option_change_sound()
        # elif key == 'down' and (current_index >= 0 and current_index < len(player.items)-2):
        #     current_index += 2
        #     option_change_sound()
        # elif key == 'left' and (current_index % 2 == 1 and current_index < len(player.items) and current_index >= 0):
        #     current_index -= 1
        #     option_change_sound()
        # elif key == 'right' and (current_index % 2 == 0 and current_index < len(player.items) and current_index >= 0 and current_index != len(player.items)-1):
        #     current_index += 1
        #     option_change_sound()

        elif key == 'left' and current_index > 0:
            current_index -= 1
            option_change_sound()
        elif key == 'right' and current_index < len(player.items) - 1:
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
    wait_for_key()

    # 아이템 효과 적용
    # heal, damage, buff, debuff

    # 특수효과 아이템 (GPT)
    if selected_item.special:
        if selected_item.name == "GPT":
            enemyCSmon.nowhp = 1
            animate_health_bar(screen, esY+104, esX+135, enemyCurrentHP, 1, getattr(enemyCSmon, 'HP', 100))
            display_status(screen)
            draw_text(screen, f"  {enemyCSmon.name}의 체력이 1이 되었다!", stX, stY, WHITE)
    
    elif selected_item.effect == "heal":
        heal_amount_req = 0
        
        # 'fixed' 속성만 있는 경우
        if hasattr(selected_item, 'fixed') and selected_item.fixed and not hasattr(selected_item, 'varied'):
            heal_amount_req = selected_item.fixed
        
        # 'varied' 속성만 있는 경우
        elif hasattr(selected_item, 'varied') and selected_item.varied and not hasattr(selected_item, 'fixed'):
            heal_amount_req = int(player.HP * selected_item.varied)
        
        # 'fixed'와 'varied'가 모두 있는 경우
        elif hasattr(selected_item, 'fixed') and selected_item.fixed and hasattr(selected_item, 'varied') and selected_item.varied:
            heal_base = selected_item.fixed
            heal_pct = int(player.HP * selected_item.varied)
            heal_amount_req = max(heal_base, heal_pct)
        
        healed = player.heal(heal_amount_req, allow_revive=getattr(selected_item, "canuse_on_fainted", False))

        animate_health_bar(screen, psY+104, psX+135, playerCurrentHP, player.nowhp, player.HP)
        display_status(screen)
        draw_text(screen, f"  {player.name}의 체력이 {healed} 회복되었다!", stX, stY, WHITE)

    elif selected_item.effect == "damage":
        # GPT(고정 -1) 특별 처리: 상대 체력을 '1'로 만든다
        # if getattr(selected_item, "fixed", None) == -1 or selected_item.name == "GPT":
        #     target_after = 1 if enemyCurrentHP > 1 else enemyCurrentHP
        #     damage_amount = enemyCurrentHP - target_after
        #     enemyCSmon.nowhp = target_after
        # else:
        #     base = selected_item.fixed if selected_item.fixed else 0
        #     pct  = int(getattr(enemyCSmon, "HP", enemyCurrentHP) * selected_item.varied) if selected_item.varied else 0
        #     damage_amount = max(base, pct)
        #     enemyCSmon.take_damage(damage_amount)
        if selected_item.name == "렉쳐노트":
            new_hp = enemyCSmon.nowhp * 0.5
            damage_amount = enemyCSmon.nowhp - new_hp
            enemyCSmon.nowhp = int(new_hp)
        else:
            # 기존 코드 유지 (최대 체력 기준)
            base = selected_item.fixed if selected_item.fixed else 0
            pct  = int(getattr(enemyCSmon, "HP", enemyCurrentHP) * selected_item.varied) if selected_item.varied else 0
            damage_amount = max(base, pct)
            enemyCSmon.take_damage(damage_amount)


        enemy_hp_after = getattr(enemyCSmon, 'nowhp', getattr(enemyCSmon, 'HP', 100))
        animate_health_bar(screen, esY+104, esX+135, enemyCurrentHP, enemy_hp_after, getattr(enemyCSmon, 'HP', 100))

        display_status(screen)
        draw_text(screen, f"  {enemyCSmon.name}에게 {damage_amount}의 데미지를 입혔다!", stX, stY, WHITE)

    elif selected_item.effect == "buff":
        if selected_item.buffto == "speed":
            player.CSPD += int(player.CSPD * selected_item.varied)
            display_status(screen)
            draw_text(screen, f"  {player.name}의 속도가 {int(selected_item.varied * 100)}% 증가했다!", stX, stY, WHITE)
        elif selected_item.buffto == "defense":
            player.CDEF += int(player.CDEF * selected_item.varied)
            display_status(screen)
            draw_text(screen, f"  {player.name}의 방어력이 {int(selected_item.varied * 100)}% 증가했다!", stX, stY, WHITE)

    elif selected_item.effect == "debuff":
        if selected_item.buffto == "speed":
            enemyCSmon.CSPD -= int(enemyCSmon.CSPD * selected_item.varied)
            display_status(screen)
            draw_text(screen, f"  {enemyCSmon.name}의 속도가 {int(selected_item.varied * 100)}% 감소했다!", stX, stY, WHITE)
        elif selected_item.buffto == "defense":
            enemyCSmon.CDEF -= int(enemyCSmon.CDEF * selected_item.varied)
            display_status(screen)
            draw_text(screen, f"  {enemyCSmon.name}의 방어력이 {int(selected_item.varied * 100)}% 감소했다!", stX, stY, WHITE)


    pygame.display.flip()
    wait_for_key()
    
    # 아이템 제거
    from ForGrd.itemForGrd import Noneitem
    player.items[chosen_idx] = copy.deepcopy(Noneitem)
    
    # 적 공격
    enemy_attack_phase(screen, None, enemy_skill=random.choice(list(enemyCSmon.skills.values())))
    
def get_random_reward_items(num_items):
    """
    등급별 확률에 따라 비복원추출 방식으로 보상 아이템을 선택하는 함수
    """
    reward_pool = []
    # 모든 아이템을 등급별로 분류
    items_by_grade = {
        "레전더리": [item for item in item_list if item.grade == "레전더리"],
        "에픽": [item for item in item_list if item.grade == "에픽"],
        "레어": [item for item in item_list if item.grade == "레어"],
        "노말": [item for item in item_list if item.grade == "노말"],
    }
    
    # 각 등급별 아이템 목록을 섞어둡니다.
    for grade in items_by_grade.keys():
        random.shuffle(items_by_grade[grade])
    
    # 설정된 확률에 따라 아이템을 num_items만큼 뽑습니다.
    # 중복을 방지하기 위해 뽑은 아이템은 해당 목록에서 제거합니다.
    for _ in range(num_items):
        rand_num = random.random()
        cumulative_prob = 0
        selected_grade = "노말"  # 기본값 설정
        
        # 누적 확률에 따라 아이템 등급 선택
        for grade, prob in ITEM_DROP_RATES.items():
            cumulative_prob += prob
            if rand_num < cumulative_prob:
                selected_grade = grade
                break
        
        # 선택된 등급의 아이템 목록에서 하나를 뽑고, 리스트에서 제거합니다.
        if items_by_grade[selected_grade]:
            selected_item = items_by_grade[selected_grade].pop()
            reward_pool.append(selected_item)
        else:
            # 해당 등급의 아이템이 모두 소진된 경우, 다른 등급에서 뽑습니다.
            all_grades = ["레전더리", "에픽", "레어", "노말"]
            random.shuffle(all_grades) # 다른 등급을 무작위로 순회
            found_item = False
            for g in all_grades:
                if items_by_grade[g]:
                    selected_item = items_by_grade[g].pop()
                    reward_pool.append(selected_item)
                    found_item = True
                    break
            if not found_item:
                # 모든 아이템이 소진된 경우
                print("Warning: All reward items have been exhausted.")
                break # 루프 종료
            
    return reward_pool


def select_reward_item(screen, items):
    """승리 후 아이템 선택 UI"""
    current_index = 0
    while True:

        display_status(screen)
        dark_overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        dark_overlay.fill((0, 0, 0, 180))  # 마지막 값(120)은 투명도, 0~255
        screen.blit(dark_overlay, (0, 0))

        
        draw_text(screen, "  승리 보상! 아이템을 선택하세요.", stX, stY, YELLOW)

        for i, item in enumerate(items):
            name_color = get_item_color_by_grade(item.grade)  # 등급별 색상 함수 사용

            prefix = "> " if i == current_index else "  "
            # 이름만 색상 적용, 설명은 그대로 WHITE
            draw_text(screen, f"{prefix}", stX, stY-350+i*100, WHITE)
            draw_text(screen, f"{item.name}", stX+30, stY-350+i*100, name_color)
            draw_text(screen, f"{item.gradeSymbol}{item.grade}", stX+30, stY-350+i*100+40, name_color, size=16)
            draw_wrapped_text(
                screen,
                item.description,
                stX+300,
                stY-350+i*100,
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

def battle(getplayer, getenemy, screen=None):
    global player, enemy, enemyCSmon, battle_end, startBattleHp
    player = getplayer
    enemy = getenemy
    battle_end = False
    startBattleHp = player.nowhp
    player.pnr_used = False  # 전투 시작 시 PNR 사용 여부 초기화
    
    # 적이 Monster 객체인 경우
    if isinstance(enemy, Monster):
        enemyCSmon = enemy
    else:
        enemyCSmon = enemy.nowCSmon if hasattr(enemy, 'nowCSmon') else enemy
    
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
        
        display_status(screen, detail=True)
        draw_text(screen, f"  앗! 야생의 {enemyCSmon.name}이/가 나타났다!", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()
        
        while not battle_end:
            # 플레이어 턴
            action = select_action(screen)
            
            if action == 0:  # 스킬 사용
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
                success = "P" if random.random() < 0.80 else "NR"
                show_pnr_result(screen, success)
                # PNR 사용 시에도 전투 루프를 계속 진행
                if success == "P":
                    return "PNR_P" # 새로운 반환값
                else:
                    return "PNR_NR" # 새로운 반환값
            
            # 적 체력 확인
            enemy_hp = getattr(enemyCSmon, 'nowhp', getattr(enemyCSmon, 'HP', 100))
            if enemy_hp <= 0:
                display_status(screen, detail=True)
                draw_text(screen, f"  {enemyCSmon.name}이/가 쓰러졌다!", stX, stY, WHITE)
                pygame.display.flip()
                wait_for_key()
                
                battle_end = True
                return "승리"
            
            # 플레이어 체력 확인
            if not player.is_alive():
                display_status(screen, detail=True)
                draw_text(screen, f"  {player.name}이/가 쓰러졌다!", stX, stY, WHITE)
                pygame.display.flip()
                wait_for_key()
                battle_end = True
                return "패배"
            
            hap_num += 1
    
    # 전투 시작
    result = battle_logic(screen)
    
    # 여기는 변경 없음
    if result == "승리":
        Battle_win()
        display_status(screen)
        draw_text(screen, f"  승리했다!", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()

        heal_amount = max(1, int(player.HP * 0.10))
        playerCurrentHP = player.nowhp
        player.heal(heal_amount)
        display_status(screen)
        animate_health_bar(screen, psY+104, psX+135, playerCurrentHP, player.nowhp, player.HP)
        draw_text(screen, f"  {player.name}의 체력이 회복되었다!", stX, stY, GREEN)
        pygame.display.flip()
        wait_for_key()

        reward_items = get_random_reward_items(3)
        selected_item = select_reward_item(screen, reward_items)
        
        if selected_item is None: 
            option_escape_sound()
            display_status(screen)
            draw_text(screen, "  아이템을 선택하지 않았습니다.", stX, stY, YELLOW)
        else:
            for idx, item in enumerate(player.items):
                if item.name == "빈 슬롯":
                    player.items[idx] = copy.deepcopy(selected_item)
                    break
            else:
                while True:
                    display_status(screen)
                    draw_text(screen, "  인벤토리가 가득 찼습니다! 버릴 아이템을 선택하세요.", stX, stY, YELLOW)
                    pygame.display.flip()
                    wait_for_key()
                    option_change_sound()
                    discard_idx = select_item(screen)
                    if discard_idx == -1:
                        selected_item = select_reward_item(screen, reward_items)
                        if selected_item is None:
                            option_escape_sound()
                            display_status(screen)
                            draw_text(screen, "  아이템을 선택하지 않았습니다.", stX, stY, YELLOW)
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
            return 1, gpaCalculator(enemyCSmon, hap_num, item_num, False)
        return 1, gpaCalculator(enemyCSmon, hap_num, item_num)
    
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
        heal_amount = max(1, int(player.HP * 0.05))
        playerCurrentHP = player.nowhp
        player.heal(heal_amount)
        display_status(screen)
        animate_health_bar(screen, psY+104, psX+135, playerCurrentHP, player.nowhp, player.HP)
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
            draw_text(screen, "  아이템을 선택하지 않았습니다.", stX, stY, YELLOW)
        else:
            for idx, item in enumerate(player.items):
                if item.name == "빈 슬롯":
                    player.items[idx] = copy.deepcopy(selected_item)
                    break
            else:
                while True:
                    display_status(screen)
                    draw_text(screen, "  인벤토리가 가득 찼습니다! 버릴 아이템을 선택하세요.", stX, stY, YELLOW)
                    pygame.display.flip()
                    wait_for_key()
                    option_change_sound()
                    discard_idx = select_item(screen)
                    if discard_idx == -1:
                        selected_item = select_reward_item(screen, reward_items)
                        if selected_item is None:
                            option_escape_sound()
                            display_status(screen)
                            draw_text(screen, "  아이템을 선택하지 않았습니다.", stX, stY, YELLOW)
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
    
    else: return 0, (enemy.credit, "F")