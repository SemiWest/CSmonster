from game_menu import *
from ForGrd.playerForGrd import *

''' 전역변수 설정 '''
battleturn = 0
hap_num = 0
item_num = 0
player = None
enemy = None
enemyCSmon = None
battle_end = False

# 기존 좌표 및 이미지 로드는 그대로 유지
sX, sY = 32, 32
stX = sX+20
stY = sY+568
esX, esY = sX+20, sY+36
psX, psY = sX+632, sY+347

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
    elif type == "SN":
        screen.blit(SYS, (x, y))
    elif type == "PS":
        screen.blit(PS, (x, y))
    elif type == "*":
        screen.blit(EVENT, (x, y))
    elif type == "AI":
        screen.blit(AI, (x, y))

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
    draw_text(screen, f"플레이어: {player.name}", sX, sY+920, VIOLET)
    draw_text(screen, f"스테이지 {battleturn}", sX, sY+960, BLUE)
    draw_text(screen, f"턴 {hap_num}", sX, sY+1000, CYAN)
    
    # 적 상태 (상단)
    screen.blit(STAT, (esX, esY))
    if hasattr(enemyCSmon, 'image'):
        image = pygame.image.load(enemyCSmon.image)
        image = pygame.transform.scale_by(image, 8)
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
    
    # 플레이어 상태 (하단) - 직접 전투
    screen.blit(STAT, (psX, psY))
    screen.blit(ME, (sX+320-ME.get_width()//2, sY+536-ME.get_height()))
    
    draw_text(screen, f"{player.name}", psX+64, psY+52, WHITE)
    draw_text(screen, f"lv.{player.level}", psX+384, psY+52, WHITE)
    
    # 플레이어 체력바
    animate_health_bar(screen, psY+104, psX+135, player.currentHp, player.currentHp, player.maxHp)

    screen.blit(TEXT, (sX+8, sY+536))

def display_player_details(screen, player, x):
    """플레이어 상세 정보 출력"""
    details = [
        (("이름", 0, WHITE), (f"{player.name}", 192, CYAN)),
        (("레벨", 0, WHITE), (f"{player.level}", 192, CYAN)),
        (("다음 레벨까지", 0, WHITE), (f"{player.expToNext - player.exp}", 192, BLUE), ("경험치 남음", 352, WHITE)),
        "",
        (("체력", 0, WHITE), (f"{player.currentHp}"+"/"+f"{player.maxHp}", 192, CYAN)),
        (("공격", 0, WHITE), (f"{player.attack}", 192, CYAN)),
        (("방어", 0, WHITE), (f"{player.defense}", 192, CYAN)),
        (("속도", 0, WHITE), (f"{player.speed}", 192, CYAN)),
        "",
        (("현재 학기", 0, WHITE), (f"{player.current_semester}", 192, WHITE)),
        (("PNR 사용가능", 0, WHITE), (f"{'가능' if player.can_use_pnr() else '불가능'}", 192, GREEN if player.can_use_pnr() else RED)),
        "",
        (("스킬 레벨", 0, WHITE), ("", 0, WHITE)),
    ]
    
    # 스킬 레벨 추가
    for skill_type, level in player.learned_skills.items():
        if level > 0:
            details.append(((f"  {skill_type}", 0, WHITE), (f"Lv.{level}", 192, GREEN if level >= 3 else YELLOW if level >= 2 else WHITE)))
    
    for i, detail_item in enumerate(details):
        y_pos = sY + 50 + i * 40
        if isinstance(detail_item, tuple):
            for detail in detail_item:
                if not isinstance(detail, tuple) and not isinstance(detail, str):
                    continue
                if isinstance(detail, tuple) and len(detail) >= 3:
                    draw_text(screen, detail[0], x + detail[1], y_pos, detail[2])

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
            y_pos = stY + int(i / 2) * 56
            
            prefix = "> " if i == current_index else "  "
            draw_text(screen, f"{prefix}{skill['name']}", x_pos, y_pos)
            
            if i == current_index:
                # 선택된 스킬 상세정보 표시
                draw_text(screen, f"{skill['description']}", sX+64, stY+160, WHITE)
                draw_text(screen, f"타입: {skill['type']}", sX+64, stY+200, WHITE)
                draw_text(screen, f"위력: {skill['damage']}", sX+64, stY+240, WHITE)
                
                # 상성 표시
                enemy_types = getattr(enemyCSmon, 'type', ['전산이론'])
                if isinstance(enemy_types, str):
                    enemy_types = [enemy_types]
                
                effectiveness = 1.0
                for enemy_type in enemy_types:
                    from ForGrd.playerForGrd import TYPE_EFFECTIVENESS
                    type_eff = TYPE_EFFECTIVENESS.get(skill['type'], {}).get(enemy_type, 1.0)
                    effectiveness = max(effectiveness, type_eff)
                
                if effectiveness > 1.0:
                    draw_text(screen, "효과: 뛰어남!", sX+64, stY+280, GREEN)
                elif effectiveness < 1.0:
                    draw_text(screen, "효과: 별로...", sX+64, stY+280, BLUE)
                else:
                    draw_text(screen, "효과: 보통", sX+64, stY+280, WHITE)

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
        
        # PNR 안내 메시지
        if player.can_use_pnr():
            draw_text(screen, "※ PNR: 95% 확률로 과목 패스 (1-2학기 통합 1회)", stX, stY+200, BLUE)

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

def show_pnr_result(screen, message, success):
    """PNR 사용 결과 표시"""
    screen.fill(WHITE)
    
    color = GREEN if success else RED
    result_text = "PNR 성공!" if success else "PNR 실패!"
    
    draw_text(screen, result_text, SCREEN_WIDTH//2 - len(result_text)*16, 250, color)
    draw_text(screen, message, SCREEN_WIDTH//2 - len(message)*8, 300, BLACK)
    
    if success:
        draw_text(screen, "과목을 자동으로 패스했습니다!", SCREEN_WIDTH//2 - 176, 350, GREEN)
    else:
        draw_text(screen, "전투를 계속 진행합니다...", SCREEN_WIDTH//2 - 144, 350, BLACK)
    
    draw_text(screen, "아무 키나 눌러 계속...", SCREEN_WIDTH//2 - 128, 450, BLACK)
    
    pygame.display.flip()
    wait_for_key()

def gpaCalculator(enemy, hap_num, item_num):
    score = max(0, (17-hap_num)/16) * 0.3 + max(0, (3-item_num)/3) * 0.3 + (player.currentHp/player.maxHp)*0.4
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

# 플레이어 스킬 사용 단계
def player_skill_phase(screen):
    """플레이어 스킬 사용 단계"""
    selected_skill = select_player_skill(screen)
    if selected_skill == -1:
        return -1
    
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
    
    # 결과 메시지
    display_status(screen, True)
    if result:
        effectiveness = result["effectiveness"]
        damage = result["damage"]
        
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
        
        draw_text(screen, f"  {enemyCSmon.name}에게 {damage}의 데미지!", stX, stY, WHITE)
    else:
        draw_text(screen, f"  {message}", stX, stY, WHITE)
    
    pygame.display.flip()
    wait_for_key()

# 적 공격 단계
def enemy_attack_phase(screen):
    """적 공격 단계"""
    playerCurrentHP = player.currentHp
    
    # 적 스킬 선택 (랜덤)
    enemy_skills = getattr(enemyCSmon, 'skills', {})
    if enemy_skills:
        skill_name = random.choice(list(enemy_skills.keys()))
        skill = enemy_skills[skill_name]
        
        if getattr(skill, 'nowpp', 1) > 0:
            # 스킬 사용
            display_status(screen, True)
            draw_text(screen, f"  {enemyCSmon.name}의 {skill.name}!", stX, stY, WHITE)
            pygame.display.flip()
            wait_for_key()
            
            # 데미지 계산
            skill_power = getattr(skill, 'skW', 30)
            enemy_attack = getattr(enemyCSmon, 'ATK', 15)
            base_damage = int((skill_power * enemy_attack) / 50)
            
            damage = player.take_damage(base_damage)
            
            # 체력바 애니메이션
            animate_health_bar(screen, psY+104, psX+135, playerCurrentHP, player.currentHp, player.maxHp)
            
            # 데미지 메시지
            display_status(screen, True)
            draw_text(screen, f"  {player.name}에게 {damage}의 데미지!", stX, stY, WHITE)
            pygame.display.flip()
            wait_for_key()
            
            # 스킬 PP 감소
            if hasattr(skill, 'nowpp'):
                skill.nowpp -= 1
        else:
            # 기본 공격
            enemy_attack = getattr(enemyCSmon, 'ATK', 15)
            damage = player.take_damage(enemy_attack)
            
            animate_health_bar(screen, psY+104, psX+135, playerCurrentHP, player.currentHp, player.maxHp)
            
            display_status(screen, True)
            draw_text(screen, f"  {enemyCSmon.name}의 기본 공격!", stX, stY, WHITE)
            pygame.display.flip()
            wait_for_key()
            
            display_status(screen, True)
            draw_text(screen, f"  {player.name}에게 {damage}의 데미지!", stX, stY, WHITE)
            pygame.display.flip()
            wait_for_key()
    else:
        # 스킬이 없으면 기본 공격
        enemy_attack = getattr(enemyCSmon, 'ATK', 15)
        damage = player.take_damage(enemy_attack)
        
        animate_health_bar(screen, psY+104, psX+135, playerCurrentHP, player.currentHp, player.maxHp)
        
        display_status(screen, True)
        draw_text(screen, f"  {enemyCSmon.name}의 기본 공격!", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()
        
        display_status(screen, True)
        draw_text(screen, f"  {player.name}에게 {damage}의 데미지!", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()

# 기존 아이템 관련 함수들 그대로 유지하되 플레이어용으로 수정
def select_item(screen, temp=None):
    """아이템 선택 - 플레이어용"""
    descriptions = [i.description for i in player.items]
    coloring = [False]*len(player.items)
    
    for i in range(len(player.items)):
        if player.items[i].name == "빈 슬롯":
            coloring[i] = CYAN
        elif player.items[i].grade == "레어":
            coloring[i] = GREEN
        elif player.items[i].grade == "에픽":
            coloring[i] = PURPLE
        elif player.items[i].grade == "레전더리":
            coloring[i] = YELLOW
    
    display_status(screen)
    current_index = 0
    
    while True:
        display_status(screen)
        
        for i, item in enumerate(player.items):
            x_pos = stX + (300 * (i % 2))
            y_pos = stY + int(i / 2) * 56
            
            color = coloring[i] if coloring[i] else WHITE
            
            prefix = "> " if i == current_index else "  "
            draw_text(screen, f"{prefix}{item.name}", x_pos, y_pos, color)
            
            if i == current_index:
                draw_text(screen, f"{descriptions[i]}", sX+30, stY+120, WHITE)
        
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
        elif key == 'up' and (current_index > 1 and current_index < len(player.items)):
            current_index -= 2
            option_change_sound()
        elif key == 'down' and (current_index >= 0 and current_index < len(player.items)-2):
            current_index += 2
            option_change_sound()
        elif key == 'left' and (current_index % 2 == 1 and current_index < len(player.items) and current_index >= 0):
            current_index -= 1
            option_change_sound()
        elif key == 'right' and (current_index % 2 == 0 and current_index < len(player.items) and current_index >= 0 and current_index != len(player.items)-1):
            current_index += 1
            option_change_sound()

def item_phase(screen):
    """아이템 사용 단계 - 플레이어용"""
    global item_num

    # TODO: 등급에 따라 아이쳄 색 표현

    playerCurrentHP = player.currentHp
    enemyCurrentHP = getattr(enemyCSmon, 'nowhp', getattr(enemyCSmon, 'HP', 100))
    
    item_num = select_item(screen)
    if item_num == -1:
        return -1
    
    selected_item = player.items[item_num]
    
    display_status(screen)
    draw_text(screen, f"  {selected_item.name}을/를 사용했다!", stX, stY, WHITE)
    pygame.display.flip()
    item_num += 1
    wait_for_key()

    # 아이템 효과 적용
    # heal, damage, buff, debuff
    
    if selected_item.effect == "heal":
        heal_amount = max(selected_item.fixed, int(player.maxHp * selected_item.varied))
        player.heal(heal_amount)
        
        animate_health_bar(screen, psY+104, psX+135, playerCurrentHP, player.currentHp, player.maxHp)
        
        display_status(screen)
        draw_text(screen, f"  {player.name}의 체력이 {heal_amount} 회복되었다!", stX, stY, WHITE)

    elif selected_item.effect == "damage":
        damage_amount = max(selected_item.fixed, int(enemyCSmon.maxHp * selected_item.varied))
        # 데미지 구현을 잘 했는지 모르겠음 ㅇㅅㅇ
        enemyCSmon.take_damage(damage_amount)

        enemy_hp_after = getattr(enemyCSmon, 'nowhp', getattr(enemyCSmon, 'HP', 100))
        animate_health_bar(screen, esY+104, esX+135, enemyCurrentHP, enemy_hp_after, getattr(enemyCSmon, 'HP', 100))


        display_status(screen)
        draw_text(screen, f"  {enemyCSmon.name}에게 {damage_amount}의 데미지를 입혔다!", stX, stY, WHITE)

    elif selected_item.effect == "buff":
        # 버프 대상: speed, defense
        if selected_item.buffto == "speed":
            player.speed += int(player.speed * selected_item.varied)
            display_status(screen)
            draw_text(screen, f"  {player.name}의 속도가 {int(selected_item.varied * 100)}% 증가했다!", stX, stY, WHITE)
        
        elif selected_item.buffto == "defense":
            player.defense += int(player.defense * selected_item.varied)
            display_status(screen)
            draw_text(screen, f"  {player.name}의 방어력이 {int(selected_item.varied * 100)}% 증가했다!", stX, stY, WHITE)
        
    elif selected_item.effect == "debuff":
        # 디버프 대상: speed, defense
        if selected_item.debuffto == "speed":
            enemyCSmon.speed -= int(enemyCSmon.speed * selected_item.varied)
            display_status(screen)
            draw_text(screen, f"  {enemyCSmon.name}의 속도가 {int(selected_item.varied * 100)}% 감소했다!", stX, stY, WHITE)
        
        elif selected_item.debuffto == "defense":
            enemyCSmon.defense -= int(enemyCSmon.defense * selected_item.varied)
            display_status(screen)
            draw_text(screen, f"  {enemyCSmon.name}의 방어력이 {int(selected_item.varied * 100)}% 감소했다!", stX, stY, WHITE)


    pygame.display.flip()
    wait_for_key()
    
    # 아이템 제거
    from ForGrd.itemForGrd import Noneitem
    player.items[item_num] = copy.deepcopy(Noneitem)
    
    # 적 공격
    enemy_attack_phase(screen)

# 메인 전투 함수 수정
def battle(getplayer, getenemy, screen=None):
    global player, enemy, enemyCSmon, battle_end
    player = getplayer
    enemy = getenemy
    battle_end = False
    
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
                esc = player_skill_phase(screen)
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
                success, message = player.use_pnr_in_battle()
                show_pnr_result(screen, message, success)
                
                if success:
                    battle_end = True
                    return "PNR"
            
            # 적 체력 확인
            enemy_hp = getattr(enemyCSmon, 'nowhp', getattr(enemyCSmon, 'HP', 100))
            if enemy_hp <= 0:
                display_status(screen, detail=True)
                draw_text(screen, f"  {enemyCSmon.name}이/가 쓰러졌다!", stX, stY, WHITE)
                pygame.display.flip()
                wait_for_key()
                
                battle_end = True
                return "승리"
            
            # 적 턴 (스킬 사용이 아닌 경우에만)
            if action == 0:  # 스킬 사용했을 때만 적이 공격
                enemy_attack_phase(screen)
            
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
    
    if result == "승리":
        Battle_win()
        display_status(screen)
        draw_text(screen, f"  승리했다!", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()
        return 1, gpaCalculator(enemyCSmon, hap_num, item_num)
    elif result == "패배":
        Lose()
        display_status(screen)
        draw_text(screen, f"  패배했다...", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()
        return 0, (enemy.credit, "F")
    elif result == "드랍":
        Lose()
        display_status(screen)
        draw_text(screen, f"  과목을 드랍했다!", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()
        return 3, (0, "W")
    elif result == "PNR":
        Battle_win()
        display_status(screen)
        draw_text(screen, f"  PNR로 과목을 패스했다!", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()
        return 2, (0, "P")
    else: return 0, (enemy.credit, "F")